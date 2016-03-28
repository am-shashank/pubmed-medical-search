import shutil
import os

def combine(f1, f2, output):
    with open(output, 'w') as outFile:
        with open(f1, 'r') as readFile:
            shutil.copyfileobj(readFile, outFile)
        with open(f2, 'r') as readFile:
            shutil.copyfileobj(readFile, outFile)



def combineDir(inDir, output):
    with open(output, 'w') as outFile:
        for f in os.listdir(inDir):
            with open(os.path.join(inDir, f), 'r') as readFile:
                shutil.copyfileobj(readFile, outFile)
