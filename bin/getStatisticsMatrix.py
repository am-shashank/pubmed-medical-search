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
import pickle
import numpy as np
import sys
import os
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

def get_statistics(inDir, labelset, inverted_index, numLabels=2):
    # create dictionary for labelset
    statistic_dict = {}
    statistic_dict["TOTAL"] = 0
    statistic_dict["STRUCTURED"] = 0
    for label in labelset:
	statistic_dict[label] = 0

    statistic_dict["UNUSED"] = 0

    for predFilePath in absoluteFilePaths(inDir):
        predFile = open(predFilePath)
        for line in predFile:
	    statistic_dict["TOTAL"] += 1
            lineSplit = line.split(":")
            actual = lineSplit[0]
	    # print actual        
	    pred1, pred2 = lineSplit[1].split(",")
            if actual != " ":
		# check which label it maps
		statistic_dict["STRUCTURED"] += 1
		if inverted_index.has_key(actual):
			statistic_dict[inverted_index[actual]] += 1
		else:
			statistic_dict["UNUSED"] += 1

    return statistic_dict

def main():
    argv = sys.argv[1].split()
    inDir = argv[0]
    outFile = argv[1]
    jsonObj = argv[2]

    coarseLabels = ["BACKGROUND", "CONCLUSIONS", "METHODS", "RESULTS", "OBJECTIVE", "OTHERS"]
    picoLabels = ["STUDY DESIGN","INTERVENTION","OTHER","OUTCOME MEASURES","PATIENTS", "OTHER_METHOD"]

    inverted_dict = invertJsonObj(jsonObj)
    statistic_dict = get_statistics(inDir, picoLabels, inverted_dict)
    
    # write dict to file
    # save to file:
    with open(outFile, 'w') as f:
	json.dump(statistic_dict, f)


if __name__ == "__main__":
    main()
