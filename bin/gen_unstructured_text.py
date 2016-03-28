# !/bin/bash
#$ -wd /home1/a/agshash/Spring_2016/Independent_Study/nate/modules
#$ -N predict_labels
#$ -pe parallel-onenode 1
#$ -j y -o /home1/a/agshash/Spring_2016/Independent_Study/nate/output/LOGS
#$ -m eas
#$ -M agshash@seas.upenn.edu

starting_line=$(grep -m2 -n -i python-code-start "$0"|tail -1|awk -F: '{print $1}')
tail -n +$starting_line "$0" | exec python - "$*"
exit

#python-code-start
import predict
import sys
import os
import logging
from logging.config import fileConfig
import time
import json

BIN_DIR = "/home1/a/agshash/Spring_2016/Independent_Study/nate/bin"

def main():
    start = time.time()
    argv = sys.argv[1].split()
    unstructuredFiles = argv[0]
    outFile = argv[1]

    fileConfig(BIN_DIR + "/logging_config.ini")
    logger = logging.getLogger()

    logger.info("getting models from: {}".format(modelDir))

    jsonFile= open(unstructuredFiles)
    jsonObject = json.loads(jsonFile)
    
    for abstract in jsonObject["articles"]:
	
	
    logger.info("predicting lines of text for: {}".format(inFile))
    predict.lm_predict(models, inFile, outFile, top_labels=2)
    logger.info("PREDICTION COMPLETE.")
    logger.info("TIME TAKEN: {}".format(time.time() - start))

if __name__ == "__main__":
"predictLines.py" 45L, 1270C

