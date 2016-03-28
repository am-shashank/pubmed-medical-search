#!/bin/bash
#$ -wd /home1/a/agshash/Spring_2016/Independent_Study/nate/modules
#$ -N gen_models
#$ -pe parallel-onenode 1
#$ -j y -o /home1/a/agshash/Spring_2016/Independent_Study/nate/output/LOGS
#$ -m eas
#$ -M agshash@seas.upenn.edu

starting_line=$(grep -m2 -n -i python-code-start "$0"|tail -1|awk -F: '{print $1}')
tail -n +$starting_line "$0" | exec python - "$*"
exit

# python-code-start
import srilm
import sys
import os
import logging
from logging.config import fileConfig

BIN_DIR = "/home1/a/agshash/Spring_2016/Independent_Study/nate/bin"

def main():
    argv = sys.argv[1].split()
    inDir = argv[0]
    outDir = argv[1]
    fileConfig(BIN_DIR + "/logging_config.ini")
    logger = logging.getLogger()

    for f in os.listdir(inDir):
        path = os.path.join(inDir, f)
        logger.info("generating models for: {}".format(path))
        srilm.srilm_bigram_models(path, outDir)
    
    logger.info("Done.")

if __name__ == "__main__":
    main()
