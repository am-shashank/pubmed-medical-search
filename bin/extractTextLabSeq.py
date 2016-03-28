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
from extract_abstract import getAbstractTexts
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
        results = getAbstractTexts(filepath, pmid)
        texts = [t for (t,l) in results]
        labels = [l for (t,l) in results]
        q.put((pmid, texts, labels))
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

def listener(q, outDir, labelMap):
    try:
        logger.info("{}: file write worker started".format(mp.current_process().name))
        allLabels = {}
        LABSEQ = "_labsequence.txt"
        TEXT = "_abtext.txt"
        while 1:
            (pmid, texts, labels) = q.get()
            if pmid == "KILL":
                break
            logger.info("printing text for: {}".format(pmid))

            # newL = labels
            newL = []
            for l in labels:
                if l in labelMap:
                    newL.append(labelMap[l])
                else:
                    logger.info("not all labels in required set")
                    newL = []
                    break
            if len(newL) == 0:
                continue

            fname = os.path.join(outDir, pmid + LABSEQ)
            with open(fname, 'w') as f:
                for l in newL:
                    f.write(l.encode('utf-8'))
                    f.write("\n")
            fname = os.path.join(outDir, pmid + TEXT)
            with open(fname, 'w') as f:
                for t in texts:
                    f.write(t.encode('utf-8'))
                    f.write("\n")

        logger.info("{}: file write worker closing".format(mp.current_process().name))
    except Exception as e:
        logger.info("ERROR IN WRITER WORKER")
        traceback.print_exc()
        raise e

def main():
    argv = sys.argv[1].split()
    inFile = argv[0]
    outDir = argv[1]
    labMapFile = argv[2]
    cpu_count = int([node.split()[1] for node in open(os.environ['PE_HOSTFILE'])][0])
    pool = mp.Pool(cpu_count)
    logger.info("using no. of CPUs: {0}...".format(cpu_count))
    manager = mp.Manager()
    q = manager.Queue()

    labelMap = {}
    with open(labMapFile, 'r') as data:
        labelMap = json.load(data)

    abstracts = []
    with open(inFile, 'r') as data:
        objs = ijson.items(data, "item")
        for abstract in objs:
            abstracts.append((abstract["filepath"], abstract["pmid"]))

    logger.info("extracting text from {} abstracts...".format(len(abstracts)))
    jobs = []
    watcher = pool.apply_async(listener, (q, outDir, labelMap,))

    for filepath, pmid in abstracts:
        job = pool.apply_async(worker, (filepath, pmid, q))
        jobs.append(job)

    for job in jobs:
        job.get()

    logger.info("adding kill to queue...")
    q.put(("KILL", "KILL", "KILL"))
    pool.close()
    pool.join()
    logger.info("Job complete.")

if __name__ == "__main__":
    main()
