#!/usr/bin/env python

import sys
sys.path.insert(0, '../modules')
import texts
import os

def main():
    inDir = sys.argv[1]
    output = sys.argv[2]

    texts.combineDir(inDir, output)

if __name__ == "__main__":
    main()
