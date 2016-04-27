'''# !/bin/bash
#$ -wd /home1/a/agshash/Spring_2016/Independent_Study/nate/modules
#$ -N create_confusion_matrix
#$ -pe parallel-onenode 1
#$ -j y -o /nlp/data/agshash/LOGFILES/CM_COARSE_LOGS
#$ -m eas
#$ -m n
starting_line=$(grep -m2 -n -i python-code-start "$0"|tail -1|awk -F: '{print $1}')
tail -n +$starting_line "$0" | exec python - "$*"
exit

'''
#python-code-start
from sklearn.metrics import confusion_matrix
import pickle
import numpy as np
import sys
import os
import matplotlib.pyplot as plt
from sklearn import svm, datasets
from sklearn.cross_validation import train_test_split
from sklearn.metrics import confusion_matrix
import json
from collections import Counter

def absoluteFilePaths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def invertJsonObj(jsonObj):
    with open(jsonObj, 'r') as f:
        jsondata = json.loads(f.read())
        # print jsondata
        inverted_dict = dict((i, k) for k, v in jsondata.items() for i in v)
    return inverted_dict

'''
    Create a a confusion matrix using sklearn
    parameters:
    inDir : contains files in the following format
        trueLabel: label1, label2
    labels : list of unique labels corresponding to the training models
    inverted_index : map between predicted label and actual label
    labelCategory : class of labels used for training [pico or coarse]
    return:
	list generator of label1
'''
def create_cm(inDir, labels, inverted_index, labelCategory, numLabels=2):
    yPred1 = read_or_new_pickle("/nlp/data/agshash/statistics/yPred1.pkl",{})
    yTrue = read_or_new_pickle("/nlp/data/agshash/statistics/yTrue.pkl",{})
    yPred2 = read_or_new_pickle("/nlp/data/agshash/statistics/yPred2.pkl",{})
    labelMetrics = {}
    label1Predictions = read_or_new_pickle("/nlp/data/agshash/statistics/label1Predictions.pkl",[])
    label2Predictions = read_or_new_pickle("/nlp/data/agshash/statistics/label2Predictions.pkl",[])
    actualLabels =  read_or_new_pickle("/nlp/data/agshash/statistics/actualLabels.pkl",[])

    for label in labels:
	if label not in yPred1:
		yPred1[label] = [] # for checking only top label
	if label not in yTrue:
		yTrue[label] = []
	if label not in yPred2:
		yPred2[label] = [] # for checking top 2 labels
	labelMetrics[label] = [] # maintain accuracy, precision, recall in the list for each label

    '''
    Test on smaller subset
    '''
    # index = 0;
    for predFilePath in absoluteFilePaths(inDir):
	# print('Predicting for : ' + predFilePath)
	# index += 1
        predFile = open(predFilePath)
        for line in predFile:
	    # print('Line : ' + line)
            lineSplit = line.split(":")
            actual = lineSplit[0]
            
	    if actual != " ":
		 # index += 1
		 # print('Line : ' + line)
		 topPreds = lineSplit[1].split(",")
		 if len(topPreds) != 2:
		 	continue
	    	 pred1 = topPreds[0].strip()
	    	 pred2 = topPreds[1].strip() 
		 if inverted_index.has_key(actual):
           	 	actual = inverted_index[actual]
		 
		 label1Predictions.append(pred1)
		 label2Predictions.append(pred2)
		 actualLabels.append(actual)	
		 
		 for label in labels:
			if actual == label:
				yTrue[label].append(1)
			else:
				yTrue[label].append(0)
			if pred1 == label:
				yPred1[label].append(1)
			else:
				yPred1[label].append(0)
			if pred1 == actual or pred2 == label:
				yPred2[label].append(1)
			else:
				yPred2[label].append(0)

	# print('---------------------------------------------------------------')
	# print('---------------------------------------------------------------')
	'''
	Test on smaller subset
	if index >= 20:
	    break
	'''

    # print('---------------------------------------------------------------')
    # print('---------------------------------------------------------------')
    # print('Co-occurence Data')
    # print('Actual Labels ' + ','.join(actualLabels))
    # print('Label 1 Predictions ' + ','.join(label1Predictions))
    # print('Label 2 Predictions ' + ','.join(label2Predictions))
    plot_cm("/nlp/data/agshash/statistics/cm_"+labelCategory+"_co_occurence", "Co-occurence of "+labelCategory+" Labels", label1Predictions, label2Predictions, labels)
    for label in labels:
	# print('Label : ' + label)
	# print('List of yTrue ' + ','.join(str(x) for x in yTrue[label]))
	# print('List of yPred1 ' + ','.join(str(x) for x in yPred1[label]))
	# print('List of yPred2 ' + ','.join(str(x) for x in yPred2[label]))
	cmTopLabel = confusion_matrix(yTrue[label], yPred1[label])
	cmTop2Labels = confusion_matrix(yTrue[label], yPred2[label])	
   	labelMetrics[label].append( getAccuracy(cmTopLabel) )
	labelMetrics[label].append( getPrecision(cmTopLabel) )
	labelMetrics[label].append( getRecall(cmTopLabel) )
	labelMetrics[label].append( getAccuracy(cmTop2Labels) )
	labelMetrics[label].append( getPrecision(cmTop2Labels) )
	labelMetrics[label].append( getRecall(cmTop2Labels) )
	# print('---------------------------------------------------------------')
    	# print('---------------------------------------------------------------')

    # check-point results   
    writeDictToFile("/nlp/data/agshash/statistics/cm_"+labelCategory+"_acc_prec_recall.txt", labelMetrics)
    pickle.dump(yPred1, open("/nlp/data/agshash/statistics/yPred1.pkl","wb"))
    pickle.dump(yTrue, open("/nlp/data/agshash/statistics/yTrue.pkl", "wb"))
    pickle.dump(yPred2, open("/nlp/data/agshash/statistics/yPred2.pkl","wb"))
    pickle.dump(label1Predictions, open("/nlp/data/agshash/statistics/label1Predictions.pkl", "wb"))
    pickle.dump(label2Predictions, open("/nlp/data/agshash/statistics/label2Predictions.pkl","wb"))

    # print('Len of Labels - ' + labelCategory + ' is : ' + str(len(label1Predictions)))
    return label1Predictions 
    # writeDictToFile(l("/nlp/data/agshash/cm_coarse_cooccurence.txt", label1AccPredictions)

def getAccuracy(npMat):
    return (npMat[0][0] + npMat[1][1]) / ((npMat[0][0] + npMat[0][1] + npMat[1][0] + npMat[1][1]) * 1.0)	

def getPrecision(npMat):
    return npMat[0][0] / ((npMat[0][0] + npMat[1][0]) * 1.0)

def getRecall(npMat):
    return npMat[0][0] / ((npMat[0][0] + npMat[0][1]) *1.0) 
	
def create_all_cm(picoDir, picoLabels, picoInvertedIndex, coarseDir, coarseLabels, coarseInvertedIndex):
    picoPred1 = create_cm(picoDir, picoLabels, picoInvertedIndex, "pico")
    coarsePred1 = create_cm(coarseDir, coarseLabels, coarseInvertedIndex, "coarse")
    print 'Len of picoPred1 : ' + str(len(picoPred1))
    print 'Len of coarsePred1 : ' + str(len(coarsePred1))
    # plot_cm("/nlp/data/agshash/cm_coarse_pico_co_occurence", "Co-occurence of top pico and coarse Labels", picoPred1, coarsePred1, coarseLabels + picoLabels)


# write dict to file
# save to file:
def writeDictToFile(outFile, dict_count):
    with open(outFile, 'w') as f:
	for key in dict_count.keys():
		f.write(str(key) + " : " + str(dict_count[key]) + "\n")

def plot_cm(outFile, title, yTrue, yPred, labels=[1,0]):
    cm = confusion_matrix(yTrue, yPred, labels)
    np.set_printoptions(precision=2)
    print('Confusion matrix, without normalization '+ title)
    print(cm)
    plt.figure()
    plot_confusion_matrix(cm, labels, title=title)

    # Normalize the confusion matrix by row (i.e by the number of samples
    # in each class)
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    print('Normalized confusion matrix '+ title)
    print(cm_normalized)
    plt.figure()
    plot_confusion_matrix(cm_normalized, labels, title=title)
    fig = plt.gcf()
    fig.savefig(outFile)
    # plt.show()


def plot_confusion_matrix(cm, labels, title='Confusion matrix', cmap=plt.cm.Blues,):
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(labels))
    plt.xticks(tick_marks, labels, rotation=45)
    plt.yticks(tick_marks, labels)
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


def read_or_new_pickle(path, default):
    try:
        foo = pickle.load(open(path, "rb"))
    except StandardError:
        foo = default
        pickle.dump(foo, open(path, "wb"))
    return foo

def main():
    coarseLabels = ["BACKGROUND", "CONCLUSIONS",
                    "METHODS", "RESULTS", "OBJECTIVE", "OTHERS"]
    picoLabels = ["STUDY DESIGN","INTERVENTION","OTHER","OUTCOME MEASURES","PATIENTS", "OTHER_METHOD"]
    argv = sys.argv[1].split()
    print len(argv)
    print argv
    if len(argv) == 3:
	inDir = argv[0]
    	# outPlotFile = argv[1]
    	jsonObj = argv[1] 
    	labelCategory = argv[2]
	inverted_dict = invertJsonObj(jsonObj)
    	# fileConfig(BIN_DIR + "/logging_config.ini")
    	# logger = logging.getLogger()
	if labelCategory == "pico":
		create_cm(inDir, picoLabels, inverted_dict, "pico")
	else:
		create_cm(inDir, coarseLabels, inverted_dict, "coarse")
    elif len(argv) == 4:
	picoDir = argv[0]
   	picoJsonObj = argv[1]
	picoInvertedDict = invertJsonObj(picoJsonObj)
	coarseDir = argv[2]
	coarseJsonObj = argv[3]
	coarseInvertedDict = invertJsonObj(coarseJsonObj)
	create_all_cm(picoDir, picoLabels, picoInvertedDict, coarseDir, coarseLabels, coarseInvertedDict)
    else:
	print "usage: inputDir labelConfigJson [inputDir labelConfigJson]"

if __name__ == "__main__":
    main()








