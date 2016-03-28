#!/bin/bash
#$ -wd /home1/c/channat/research/classifier/lang/modules
#$ -N split_abstract_list
#$ -pe parallel-onenode 40
#$ -j y -o /home1/c/channat/research/output/LOGS
#$ -m eas
#$ -M channat@seas.upenn.edu

starting_line=$(grep -m2 -n -i python-code-start "$0"|tail -1|awk -F: '{print $1}')
tail -n +$starting_line "$0" | exec python - "$*"
exit

#python-code-start

import sys
import ijson
import json
from extract_abstract import extractXML
from extract_abstract import getAbstractTexts
import os
import multiprocessing as mp
import logging
from logging.config import fileConfig
import traceback

BIN_DIR = "/home1/c/channat/research/classifier/lang/bin"

fileConfig(BIN_DIR + "/logging_config.ini")
logger = logging.getLogger()

def main():
    argv = sys.argv[1].split()
    inFile = argv[0]
    outDir = argv[1]
    absPerFile = 100000

    count = 0
    fileCount = 1
    abstracts = []
    with open(inFile, 'r') as data:
        objs = ijson.items(data, "item")
        for abstract in objs:
            count += 1
            obj = {"pmid": abstract["pmid"], "filepath": abstract["filepath"], \
                    "labels": abstract["labels"]}
            abstracts.append(obj)
            # abstracts.append((abstract["filepath"], abstract["pmid"], \
                # abstract["labels"]))

            if count % absPerFile == 0:
                filename = os.path.join(outDir, "absList_{}.json".format(fileCount))
                logger.info("writing {} abstracts to {}...".format(
                    len(abstracts), filename))
                with open(filename, 'w') as writeTo:
                    json.dump(abstracts, writeTo, indent=1)
                fileCount += 1
                abstracts = []

    filename = os.path.join(outDir, "absList_{}.json".format(fileCount))
    with open(filename, 'w') as writeTo:
        json.dump(abstracts, writeTo, indent=1)

    logger.info("Job complete.")

if __name__ == "__main__":
    main()
