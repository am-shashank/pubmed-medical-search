# !/bin/bash
#$ -wd /home1/a/agshash/Spring_2016/Independent_Study/nate/modules
#$ -N create_confusion_matrix
#$ -pe parallel-onenode 1
#$ -j y -o /home1/a/agshash/Spring_2016/Independent_Study/nate/output/LOGS
#$ -m eas
#$ -M agshash@seas.upenn.edu
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
    Create a a confusion matrix usibng sklearn
    parameters:
    inDir contains files in the following format
        trueLabel: label1, label2
'''
def create_cm(inDir, labels, inverted_index, numLabels=2):
    label1Predictions = []
    label2Predictions = []
    label2AccPredictions = []
    labelActual = []
    for predFilePath in absoluteFilePaths(inDir):

        predFile = open(predFilePath)
        for line in predFile:
            lineSplit = line.split(":")
            actual = lineSplit[0]
            pred1, pred2 = lineSplit[1].split(",")

	    if actual != " ":
		 if inverted_index.has_key(actual):
           	 	actual = inverted_index[actual]
		 
		 labelActual.append(actual)
           	 label1Predictions.append(pred1)
		 label2Predictions.append(pred2)
 
		 # print "Actual : " + actual + " Pred1 : " + pred1 + " Pred2 : " + pred2		 

		 if (actual == pred1):
           	 	label2AccPredictions.append(pred1)
		 else:
			label2AccPredictions.append(pred2)

    # plot_cm("/nlp/data/agshash/cm_pico_cooccurence", "Cooccurence of Pico Labels - Confusion Matrix", label1Predictions, label2Predictions, labels)
    # plot_cm("/nlp/data/agshash/cm_pico_accuracy1", "Accuracy1 Pico - Confusion Matrix", labelActual, label1Predictions, labels)
    # plot_cm("/nlp/data/agshash/cm_pico_accuracy2", "Accuracy2 Pico - Confusion Matrix", labelActual, label2AccPredictions, labels)
 
    createStatsDict("/nlp/data/agshash/cm_pico_cooccurence.txt", label1Predictions, label2Predictions, labels)
    createStatsDict("/nlp/data/agshash/cm_pico_accuracy1.txt", labelActual, label1Predictions, labels)
    createStatsDict("/nlp/data/agshash/cm_pico_accuracy2.txt", labelActual, label2AccPredictions, labels)
    

def createStatsDict(outFile, x_label, y_label, labels):
    dict_count = {};
    for label in labels:
	for label2 in labels:
		tup = (label.strip(), label2.strip())
		dict_count[tup] = 0

    print dict_count

    for index in range(len(x_label)):
    	tup = (x_label[index].strip(), y_label[index].strip())
	if tup in dict_count.keys():
		dict_count[tup] += 1
	
    # write dict to file
    # save to file:
    with open(outFile, 'w') as f:
	for key in dict_count.keys():
		f.write(str(key) + " : " + str(dict_count[key]) + "\n")

def plot_cm(outFile, title, yTrue, yPred, labels):
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
    argv = sys.argv[1].split()
    inDir = argv[0]
    # outPlotFile = argv[1]
    jsonObj = argv[1]
    # fileConfig(BIN_DIR + "/logging_config.ini")
    # logger = logging.getLogger()

    coarseLabels = ["BACKGROUND", "CONCLUSIONS",
                    "METHODS", "RESULTS", "OBJECTIVE", "OTHERS"]
    picoLabels = ["STUDY DESIGN","INTERVENTION","OTHER","OUTCOME MEASURES","PATIENTS", "OTHER_METHOD"]

    inverted_dict = invertJsonObj(jsonObj)
    
    create_cm(inDir, picoLabels, inverted_dict)


if __name__ == "__main__":
    main()








