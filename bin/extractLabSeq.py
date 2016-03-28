#!/bin/bash
#$ -wd /home1/c/channat/research/classifier/lang/modules
#$ -N extract_labSeq
#$ -pe parallel-onenode 60
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
from extract_abstract import getLabelSequence
import os
import multiprocessing as mp
import logging
from logging.config import fileConfig
import traceback

BIN_DIR = "/home1/c/channat/research/classifier/lang/bin"

fileConfig(BIN_DIR + "/logging_config.ini")
logger = logging.getLogger()

def worker(filepath, pmid, q):
    try:
        logger.info("{}: {}, {}".format(mp.current_process().name, pmid, filepath))
        labels = getLabelSequence(filepath, pmid)
        q.put(labels)
        return "done"
    except Exception as e:
        logger.info("ERROR IN WORKER: {},\
                {},{}".format(mp.current_process().name, pmid, filepath))
        traceback.print_exc()
        return "error"
        # raise e

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def getTuples(tokens):
    ngrams = []
    for i in range(0, len(tokens) - 1):
        ngrams.append((tokens[i], tokens[i+1]))
    return ngrams

def listener(q, outFile):
    try:
        logger.info("{}: file write worker started".format(mp.current_process().name))
        allLabels = {}
        while 1:
            labels = q.get()
            logger.info(labels)
            if len(labels) == 1 and labels[0] == "KILL":
                with open(outFile, 'w') as f:
                    json.dump(allLabels, f, sort_keys=True, indent=1)
                break
            for l1,l2 in getTuples(labels):
                if l1 not in allLabels:
                    allLabels[l1] = {}
                
                if l2 in allLabels[l1]:
                    allLabels[l1][l2] = allLabels[l1][l2] + 1
                else:
                    allLabels[l1][l2] = 1
        logger.info("{}: file write worker closing".format(mp.current_process().name))
    except Exception as e:
        logger.info("ERROR IN WRITER WORKER")
        traceback.print_exc()
        raise e

def main():
    argv = sys.argv[1].split()
    inFile = argv[0]
    outDir = argv[1]
    cpu_count = int([node.split()[1] for node in open(os.environ['PE_HOSTFILE'])][0])
    pool = mp.Pool(cpu_count)
    logger.info("using no. of CPUs: {0}...".format(cpu_count))
    manager = mp.Manager()
    q = manager.Queue()

    abstracts = []
    with open(inFile, 'r') as data:
        objs = ijson.items(data, "item")
        for abstract in objs:
            abstracts.append((abstract["filepath"], abstract["pmid"]))

    logger.info("extracting text from {} abstracts...".format(len(abstracts)))
    jobs = []
    watcher = pool.apply_async(listener, (q, outDir,))

    for filepath, pmid in abstracts:
        job = pool.apply_async(worker, (filepath, pmid, q))
        jobs.append(job)

    for job in jobs:
        job.get()

    logger.info("adding kill to queue...")
    q.put(["KILL"])
    pool.close()
    pool.join()
    logger.info("Job complete.")

if __name__ == "__main__":
    main()
