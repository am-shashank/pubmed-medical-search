# !/bin/bash
#$ -wd /home1/a/agshash/Spring_2016/Independent_Study/nate/modules
#$ -N create_confusion_matrix
#$ -pe parallel-onenode 1
#$ -j y -o /nlp/data/agshash/LOGS
#$ -m eas
#$ -m n
starting_line=$(grep -m2 -n -i python-code-start "$0"|tail -1|awk -F: '{print $1}')
tail -n +$starting_line "$0" | exec python - "$*"
exit


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
    yPred1 = {}
    yTrue = {}
    yPred2 = {}
    labelMetrics = {}
    label1Predictions = []
    label2Predictions = []
    actualLabels = []

    for label in labels:
	yPred1[label] = [] # for checking only top label
	yTrue[label] = []
	yPred2[label] = [] # for checking top 2 labels
	labelMetrics[label] = [] # maintain accuracy, precision, recall in the list for each label

    for predFilePath in absoluteFilePaths(inDir):

        predFile = open(predFilePath)
        for line in predFile:
            lineSplit = line.split(":")
            actual = lineSplit[0].strip()
            
            
	    if actual != " ":
		 pred1, pred2 = lineSplit[1].split(",")
	    	 pred1 = pred1.strip()
	    	 pred2 = pred2.strip() 
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
			if pred1 == label or pred2 == label:
				yPred2[label].append(1)
			else:
				yPred2[label].append(0)


		 # print "Actual : " + actual + " Pred1 : " + pred1 + " Pred2 : " + pred2		 
    plot_cm("/nlp/data/agshash/cm_"+labelCategory+"_co_occurence", "Co-occurence of "+labelCategory+" Labels", label1Predictions, label2Predictions, labels)
    for label in labels:
	cmTopLabel = confusion_matrix(yTrue[label], yPred1[label])
	cmTop2Labels = confusion_matrix(yTrue[label], yPred2[label])	
   	labelMetrics[label].append( getAccuracy(cmTopLabel) )
	labelMetrics[label].append( getPrecision(cmTopLabel) )
	labelMetrics[label].append( getRecall(cmTopLabel) )
	labelMetrics[label].append( getAccuracy(cmTop2Labels) )
	labelMetrics[label].append( getPrecision(cmTop2Labels) )
	labelMetrics[label].append( getRecall(cmTop2Labels) )
    writeDictToFile("/nlp/data/agshash/cm_"+labelCategory+"_acc_prec_recall.txt", labelMetrics)
    return yPred1
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
    plot_cm("/nlp/data/agshash/cm_coarse_pico_co_occurence", "Co-occurence of top pico and coarse Labels", picoPred1, coarsePred1, coarseLabels + picoLabels)


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








