#!/usr/bin/env python

import sys
sys.path.insert(0, '../modules')
import predict
import os

def main():
    inDir = sys.argv[1]
    testString = sys.argv[2]
    print "predicting label for: {}".format(testString)

    models = []
    for model in os.listdir(inDir):
        modelName = model.split(".")[0]
        models.append((modelName, os.path.join(inDir, model)))

    label, ppls = predict.lm_predict_string(models, testString)
    print ppls
    print label

if __name__ == "__main__":
    main()
