#!/bin//bash
#$ -wd /home1/a/agshash/Spring_2016/Independent_Study/nate/modules
#$ -N combine_labels 
#$ -pe parallel-onenode 1
#$ -j y -o /home1/a/agshash/Spring_2016/Independent_Study/nate/output/LOGS
#$ -m eas
#$ -M agshash@seas.upenn.edu

starting_line=$(grep -m2 -n -i python-code-start "$0"|tail -1|awk -F: '{print $1}')
tail -n +$starting_line "$0" | exec python - "$*"
exit

# python-code-start
import sys
sys.path.insert(0, '../modules')
import os
import json

def combineLabels(inDir, outDir, labelConfig):

	for mainLabel in labelConfig:
		try:
			resultFile = open(os.path.join(outDir, mainLabel+".txt"),"w")
			mainFile = open(os.path.join(inDir, mainLabel + ".txt"), "r")
			resultFile.write(mainFile.read())
			for sameLabel in labelConfig[mainLabel]:
				try:
					toCombine = open(os.path.join(inDir, sameLabel + ".txt"),"r")
					resultFile.write(toCombine.read())
				except:
					continue
		except:
			continue
			

def main():
	argv = sys.argv[1].split()
        inDir = argv[0]
        outDir = argv[1]
        jsonConfigFile = argv[2]
        jsonFd = open(jsonConfigFile)
        combineLabels(inDir, outDir, json.load(jsonFd))
	

if __name__ == "__main__":
        main()

