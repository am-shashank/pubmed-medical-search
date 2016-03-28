#!/bin/bash
#$ -wd /home1/c/channat/research/classifier/lang/modules
#$ -N calc_HMM
#$ -pe parallel-onenode 50
#$ -j y -o /home1/c/channat/research/output/LOGS
#$ -m eas
#$ -M channat@seas.upenn.edu

starting_line=$(grep -m2 -n -i python-code-start "$0"|tail -1|awk -F: '{print $1}')
tail -n +$starting_line "$0" | exec python - "$*"
exit

#python-code-start

import sys
import multiprocessing as mp
# sys.path.insert(0, '../modules')
import viterbi
import math
import json
import os
import logging
from logging.config import fileConfig
import srilm
from decimal import Decimal
import traceback

BIN_DIR = "/home1/c/channat/research/classifier/lang/bin"
START = "_START_"
END = "_END_"
TEXT = "_abtext"
LABSEQ = "_labsequence"

TEXT_DIR = "text/"
EXPECTED_DIR = "expected/"

TWOPLACES = Decimal(10) ** -4

fileConfig(BIN_DIR + "/logging_config.ini")
logger = logging.getLogger()

def load_label_index(A):
    lmap = {}
    for s, l in enumerate(A):
        lmap[l] = s
    return lmap


def load_transition_matrix(tranProbFile):
    logger.info("reading transition probabilities: {}".format(tranProbFile))
    probs = {}
    with open(tranProbFile, 'r') as data:
        probs = json.loads(data.read())

    A = viterbi.createProbMatrix(probs)
    # for l in A:
        # print l
        # print A[l]
    logger.info("no. of MC states: {}".format(len(A)))
    return A


def load_models(modelDir):
    logger.info("loading LM from: {}".format(modelDir))
    models = {}
    for m in os.listdir(modelDir):
        modelName = m.split(".")[0]
        models[modelName] = os.path.join(modelDir, m)
    logger.info("no. of LM's: {}".format(len(models)))
    logger.info("note: LMs do not include 'OTHER', '{}' and '{}'".format(START, END))
    return models


def get_text_lines(textFile):
    logger.info("reading text snippets from: {}".format(textFile))
    with open(textFile, 'r') as data:
        texts = data.read().splitlines()
    logger.info("no. of lines: {}".format(len(texts)))
    return texts

def emit_prob(models, labelString, text):
    if labelString == "OTHER" \
            or labelString == START or labelString == "_END_":
        return 1
    return Decimal(srilm.srilm_prob(models[labelString], text))

def retrieve_path(V, A, T, backPointers, lmap, last_label):
    path = []
    curr = last_label
    for t in reversed(range(T+1)):
        s = lmap[curr]
        prev = backPointers[s][t]
        path = [prev] + path
        curr = prev
        # print t, curr

    # for s, label in enumerate(A):
        # print V[s],
        # print label
    # for s, label in enumerate(A):
        # print backPointers[s],
        # print label

    return path


def get_lab_seq(lmap, models, A, B, texts, w, w2):
    logger.info("getting best label sequence...")
    T = len(texts)
    N = len(A)

    if N != len(models) + 2:
        raise ValueError('MC states should be equal number of models + 2')

    V = [[None for _ in range(T+1)] for _ in range(N)]
    backPointers = [[None for _ in range(T+1)] for _ in range(N)]

    # initialization
    for label in A:
        s = lmap[label]
        a = A['_START_'][label]
        b = B(models, label, texts[0]) if a > 0 else Decimal(0)
        # V[s][0] = Decimal(a) * b
        V[s][0] = (w * Decimal(a)) + ((1 - w) * b)
        backPointers[s][0] = START
        # print "{} <- {}, {}".format(label, START, V[s][0].quantize(TWOPLACES))

    # for s, label in enumerate(A):
        # print V[s],
        # print label

    # recursion step
    for t, text in enumerate(texts):
        if t == 0:
            continue
        # print "\n\n{}: {}\n".format(t, text)
        for label in A:
            if label == START or label == END:
                continue
            s = lmap[label]
            vVals = []
            b = B(models, label, text)
            # print "\n\n{}".format(label)
            for labelFrom in A:
                if labelFrom == START or labelFrom == END:
                    continue
                sFrom = lmap[labelFrom]
                a = Decimal(A[labelFrom][label])
                # vCurr = a * V[sFrom][t-1] * b
                vCurr = (w * a) + (w2 * V[sFrom][t-1]) + ((1-w-w2)* b)
                # print "{}, a: {}, V: {}, vCurr: {}".format(labelFrom, \
                        # Decimal(a).quantize(TWOPLACES), \
                        # V[sFrom][t-1].quantize(TWOPLACES), vCurr.quantize(TWOPLACES))
                vVals.append((labelFrom, vCurr))
            (prev, v) = max(vVals, key=lambda x:x[1])
            # print "{} <- {}, {}".format(label, prev, v.quantize(TWOPLACES))
            V[s][t] = v
            backPointers[s][t] = prev


        # for s, label in enumerate(A):
            # print V[s],
            # print label
        # for s, label in enumerate(A):
            # print backPointers[s],
            # print label


    # termination step
    qF = lmap[END]
    vVals = []
    for labelFrom in A:
        if labelFrom == START or labelFrom == END:
            continue
        sFrom = lmap[labelFrom]
        a = Decimal(A[labelFrom][END])
        # vCurr = a * V[sFrom][T-1]
        vCurr = (w * a) + ((1 - w) * V[sFrom][T-1])
        # print "{} -> {}, a: {}, V: {}, vCurr: {}".format(labelFrom, \
                # label, a, V[sFrom][t-1], vCurr)
        vVals.append((labelFrom, vCurr))
    (prev, v) = max(vVals, key=lambda x:x[1])
    # print "{} <- {}, {}\n".format(END, prev, v.quantize(TWOPLACES))
    V[qF][T] = v
    backPointers[qF][T] = prev

    bestPath = retrieve_path(V, A, T, backPointers, lmap, END)
    logger.info(("best path found"))
    return bestPath

def load_path(expectedFile):
    with open(expectedFile, 'r') as data:
        path = data.read().splitlines()
    return path

def calc_path_accuracy(path, expected_path):
    logger.info("calculating path accuracy...")
    logger.info("expected path: {}".format(expected_path))
    logger.info("actual path: {}".format(path))
    if len(path) != len(expected_path):
        logger.error("path lengths not equal")
        return -1

    errCount = 0
    for i, l in enumerate(path):
        expected = expected_path[i]
        if l != expected:
            errCount += 1
    return (len(path) - errCount) / float(len(path))

def worker(A, B, models, lmap, inDir, inputFile, w, w2, q):
    try:
        logger.info("{}: {}".format(mp.current_process().name, inputFile))
        pmid = inputFile.replace(TEXT, "").replace(".txt", "")
        labSeq = []
        expectedSeq = []

        textArr = get_text_lines(os.path.join(inDir + TEXT_DIR, inputFile))
        labSeq = get_lab_seq(lmap, models, A, B, textArr, w, w2)
        labSeq = [l for l in labSeq if l != START]

        expectedFileName = inputFile.replace(TEXT, LABSEQ)
        expectedSeq = load_path(os.path.join(inDir + EXPECTED_DIR, expectedFileName))

        accuracy = calc_path_accuracy(labSeq, expectedSeq)
        logger.info("path accuracy: {}\n".format(accuracy))

        q.put((pmid, accuracy, expectedSeq, labSeq))
        return "done"
    except Exception as e:
        q.put((pmid, -1, labSeq, expectedSeq))
        logger.info("ERROR IN WORKER: {},\
                {}".format(mp.current_process().name, inputFile))
        traceback.print_exc()
        return "error"


def listener(q, outputFile):
    logger.info("{}: file write worker started".format(mp.current_process().name))
    output = open(outputFile, 'w')
    output.write("{}, {}, {}, {}\n".format("pmid", "accuracy", "expected", "actual"))

    allAcc = []
    while 1:
        (pmid, acc, expectedSeq, actualSeq) = q.get()
        if pmid == "KILL":
            break

        if acc != -1:
            allAcc.append(acc)
        output.write("{}, {}, {}, {}\n".format(pmid, acc, expectedSeq, actualSeq))
        output.flush()

    avg = sum(allAcc) / float(len(allAcc))
    output.write("{}, {}\n".format("total_average", avg))

    logger.info("{}: file write worker closing".format(mp.current_process().name))
    output.close()


def main():
    argv = sys.argv[1].split()

    tranProbFile = argv[0]
    modelDir = argv[1]
    inDir = argv[2]
    outputFile = argv[3]
    w = Decimal(argv[4])
    w2 = Decimal(argv[5])

    cpu_count = int([node.split()[1] for node in open(os.environ['PE_HOSTFILE'])][0])
    pool = mp.Pool(cpu_count)
    logger.info("using no. of CPUs: {0}...".format(cpu_count))
    manager = mp.Manager()
    q = manager.Queue()

    A = load_transition_matrix(tranProbFile)
    B = emit_prob
    models = load_models(modelDir)
    lmap = load_label_index(A)

    jobs = []
    watcher = pool.apply_async(listener, (q, outputFile,))

    textDir = inDir + TEXT_DIR
    for t in os.listdir(textDir):
        job = pool.apply_async(worker, (A, B, models, lmap, inDir, t, \
                 w, w2, q,))
        jobs.append(job)

    for job in jobs:
        job.get()

    logger.info("adding kill to queue...")
    q.put(("KILL", "KILL"))
    pool.close()
    pool.join()
    logger.info("Job complete.")


    

if __name__ == "__main__":
    main()
