#!/usr/bin/env python

import sys
sys.path.insert(0, '../modules')
import predict
import os
import logging
from logging.config import fileConfig

BIN_DIR = "/home1/c/channat/research/classifier/lang/bin"

def main():
    argv = sys.argv
    modelDir = argv[1]
    inFile = argv[2]
    outFile = argv[3]

    fileConfig(BIN_DIR + "/logging_config.ini")
    logger = logging.getLogger()

    logger.info("getting models from: {}".format(modelDir))

    models = []
    for model in os.listdir(modelDir):
        modelName = model.split(".")[0]
        models.append((modelName, os.path.join(modelDir, model)))

    logger.info("predicting lines of text for: {}".format(inFile))
    predict.lm_predict(models, inFile, outFile, top_labels=2)
    logger.info("Prediction complete.")

if __name__ == "__main__":
    main()
