#!/usr/bin/env python

import sys
sys.path.insert(0, '../modules')
import srilm
import os

def main():
    model = sys.argv[1]
    testString = sys.argv[2]
    print "calculating probability for: {}".format(testString)

    prob = srilm.srilm_prob(model, testString)
    print prob

if __name__ == "__main__":
    main()
