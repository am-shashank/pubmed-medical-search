# !/bin/bash
#$ -wd /home1/a/agshash/Spring_2016/Independent_Study/nate/modules
#$ -N predict_full_text
#$ -pe parallel-onenode 1
#$ -j y -o /home1/a/agshash/Spring_2016/Independent_Study/nate/output/Predict_Full_textLOGS
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

BIN_DIR = "/home1/a/agshash/Spring_2016/Independent_Study/nate/bin"

def main():
    start = time.time()
    argv = sys.argv[1].split()
    lmFile = argv[0]
    inFile = argv[1]
    outFile = argv[2]

    fileConfig(BIN_DIR + "/logging_config.ini")
    logger = logging.getLogger()

    logger.info("predicting lines of text for: {}".format(inFile))
    predict.lm_predict_full_text(lmFile, inFile, outFile, top_labels=3)
    logger.info("PREDICTION COMPLETE.")
    logger.info("TIME TAKEN: {}".format(time.time() - start))

if __name__ == "__main__":
    main()
