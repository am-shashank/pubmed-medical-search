# !/bin/bash
# $ -wd /home1/c/channat/research/classifier/lang/modules
# $ -N extract_abstracts
# $ -pe parallel-onenode 60
# $ -j y -o /home1/c/channat/research/output/LOGS
# $ -m eas
# $ -M channat@seas.upenn.edu

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

def worker(filepath, pmid, q, labels):
    try:
        logger.info("{}: {}, {}".format(mp.current_process().name, pmid, filepath))
        texts = getAbstractTexts(filepath, pmid)
        for text,label in texts:
            if label in labels:
                q.put((text,label))
        return "done"
    except Exception as e:
        logger.info("ERROR IN WORKER: {},\
                {},{}".format(mp.current_process().name, pmid, filepath))
        traceback.print_exc()
        return "error"
        # raise e

def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)

def listener(q, outDir):
    try:
        logger.info("{}: file write worker started".format(mp.current_process().name))
        files = {}
        while 1:
            (text,label) = q.get()
            # logger.info(label)
            if text == "KILL":
                break
            if label not in files:
                label = label.replace("/", "_")
                # logger.info(os.path.join(outDir, label + ".txt"))
                files[label] = os.path.join(outDir, label + ".txt")
            with open(files[label], 'a') as f:
                f.write(removeNonAscii(text))
                f.write("\n")
                f.flush()
        logger.info("{}: file write worker closing".format(mp.current_process().name))
    except Exception as e:
        logger.info("ERROR IN WRITER WORKER")
        traceback.print_exc()
        raise e

def main():
    argv = sys.argv[1].split()
    inFile = argv[0]
    outDir = argv[1]
    validLabels = argv[2]
    cpu_count = int([node.split()[1] for node in open(os.environ['PE_HOSTFILE'])][0])
    pool = mp.Pool(cpu_count)
    logger.info("using no. of CPUs: {0}...".format(cpu_count))
    manager = mp.Manager()
    q = manager.Queue()

    labels = []
    with open(validLabels, 'r') as data:
        objs = ijson.items(data, "item")
        for l in objs:
            labels.append(l)

    abstracts = []
    with open(inFile, 'r') as data:
        objs = ijson.items(data, "item")
        for abstract in objs:
            abstracts.append((abstract["filepath"], abstract["pmid"]))

    logger.info("extracting text from {} abstracts...".format(len(abstracts)))
    jobs = []
    watcher = pool.apply_async(listener, (q, outDir,))

    for filepath, pmid in abstracts:
        job = pool.apply_async(worker, (filepath, pmid, q, labels))
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
