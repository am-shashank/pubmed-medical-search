#!/usr/bin/env python

import sys
sys.path.insert(0, '../modules')
import viterbi
import math
import json
import os
import logging
from logging.config import fileConfig
import srilm
from decimal import Decimal

BIN_DIR = "/home1/c/channat/research/classifier/lang/bin"
START = "_START_"
END = "_END_"

fileConfig(BIN_DIR + "/logging_config.ini")
logger = logging.getLogger()

def emit_prob(models, labelString, text):
    if labelString == "OTHER" \
            or labelString == START or labelString == "_END_":
        return 1
    return Decimal(srilm.srilm_prob(models[labelString], text))


def main():
    tranProbFile = sys.argv[1]
    modelDir = sys.argv[2]
    textFile = sys.argv[3]
    w = Decimal(sys.argv[4])
    w2 = Decimal(sys.argv[5])

    logger.info("reading transition probabilities: {}".format(tranProbFile))
    probs = {}
    with open(tranProbFile, 'r') as data:
        probs = json.loads(data.read())
    A = viterbi.createProbMatrix(probs)
    for l in A:
        print l
        print A[l]
    N = len(A)
    logger.info("no. of MC states: {}".format(N))

    lmap = {}
    for s, l in enumerate(A):
        lmap[l] = s

    logger.info("loading LM from: {}".format(modelDir))
    models = {}
    for m in os.listdir(modelDir):
        modelName = m.split(".")[0]
        models[modelName] = os.path.join(modelDir, m)
    B = emit_prob
    logger.info("no. of LM's: {}".format(len(models)))
    logger.info("note: LMs do not include 'OTHER', '{}' and '{}'".format(START, END))

    if N != len(models) + 2:
        raise ValueError('MC states should be equal number of models + 3')

    logger.info("reading text snippets from: {}".format(textFile))
    with open(textFile, 'r') as data:
        texts = data.read().splitlines()
        T = len(texts)
    logger.info("no. of lines: {}".format(T))

    V = [[None for _ in range(T+1)] for _ in range(N)]
    backPointers = [[None for _ in range(T+1)] for _ in range(N)]
    
    TWOPLACES = Decimal(10) ** -4

    # initialization
    for label in A:
        s = lmap[label]
        a = A['_START_'][label]
        b = B(models, label, texts[0]) if a > 0 else Decimal(0)
        V[s][0] = (w * Decimal(a)) + ((1 - w) * b)
        backPointers[s][0] = START
        print "{} <- {}, {}".format(label, START, V[s][0].quantize(TWOPLACES))

    for s, label in enumerate(A):
        print V[s],
        print label

    # recursion step
    for t, text in enumerate(texts):
        print "\n\n{}: {}\n".format(t, text)
        if t == 0:
            continue
        for label in A:
            if label == START or label == END:
                continue
            s = lmap[label]
            vVals = []
            b = B(models, label, text)
            print "\n\n{}".format(label)
            for labelFrom in A:
                if labelFrom == START or labelFrom == END:
                    continue
                sFrom = lmap[labelFrom]
                a = Decimal(A[labelFrom][label])
                vCurr = (w * a) + (w2 * V[sFrom][t-1]) + ((1-w-w2)* b)
                print "{}, a: {}, V: {}, vCurr: {}".format(labelFrom, \
                        Decimal(a).quantize(TWOPLACES), \
                        V[sFrom][t-1].quantize(TWOPLACES), vCurr.quantize(TWOPLACES))
                vVals.append((labelFrom, vCurr))
            (prev, v) = max(vVals, key=lambda x:x[1])
            print "{} <- {}, {}".format(label, prev, v.quantize(TWOPLACES))
            V[s][t] = v
            backPointers[s][t] = prev


        for s, label in enumerate(A):
            print V[s],
            print label
        for s, label in enumerate(A):
            print backPointers[s],
            print label


    # termination step
    qF = lmap[END]
    for labelFrom in A:
        if labelFrom == START or labelFrom == END:
            continue
        sFrom = lmap[labelFrom]
        a = Decimal(A[labelFrom][END])
        vCurr = (w * a) + ((1 - w) * V[sFrom][t-1])
        # print "{} -> {}, a: {}, V: {}, vCurr: {}".format(labelFrom, \
                # label, a, V[sFrom][t-1], vCurr)
        vVals.append((labelFrom, vCurr))
    (prev, v) = max(vVals, key=lambda x:x[1])
    print "{} <- {}, {}\n".format(END, prev, v.quantize(TWOPLACES))
    V[qF][T] = v
    backPointers[qF][T] = prev

    # retrieve best path
    path = []
    curr = END
    for t in reversed(range(T+1)):
        s = lmap[curr]
        prev = backPointers[s][t]
        path = [prev] + path
        curr = prev
        print t, curr

    for s, label in enumerate(A):
        print V[s],
        print label
    for s, label in enumerate(A):
        print backPointers[s],
        print label

    print "\n\nbest path: {}\n\n".format(path)




if __name__ == "__main__":
    main()
