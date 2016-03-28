#!/bin/bash
#$ -wd /home1/c/channat/research/classifier/lang/modules
#$ -N extract_abstracts
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
        texts = getAbstractTexts(filepath, pmid)
        for t in texts:
            q.put(t)
    except Exception as e:
        logger.info("ERROR IN WORKER: {},\
                {},{}".format(mp.current_process().name, pmid, filepath))
        traceback.print_exc()
        # raise e
    return "done"

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def listener(q, outFile, labelOutFile):
    logger.info("{}: file write worker started".format(mp.current_process().name))
    f = open(outFile, 'w')
    labelF = open(labelOutFile, 'w')
    while 1:
        (text,label) = q.get()
        if text == "KILL":
            break
        f.write(removeNonAscii(text))
        f.write("\n")
        f.flush()
        labelF.write(label)
        labelF.write("\n")
        labelF.flush()
    logger.info("{}: file write worker closing".format(mp.current_process().name))
    f.close()
    labelF.close()

def main():
    argv = sys.argv[1].split()
    inFile = argv[0]
    outFile = argv[1]
    labelOutFile = argv[2]
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
    watcher = pool.apply_async(listener, (q, outFile,labelOutFile,))

    for filepath, pmid in abstracts:
        job = pool.apply_async(worker, (filepath, pmid, q))
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
