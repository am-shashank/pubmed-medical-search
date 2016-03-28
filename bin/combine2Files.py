#!/usr/bin/env python

import sys
sys.path.insert(0, '../modules')
import texts
import os

def main():
    f1 = sys.argv[1]
    f2 = sys.argv[2]
    output = sys.argv[3]

    texts.combine(f1, f2, output)

if __name__ == "__main__":
    main()
