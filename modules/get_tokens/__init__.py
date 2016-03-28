import nltk
import sys

def tokenizeString(s):
    try:
        tokens = nltk.word_tokenize(s)
        return tokens
    except:
        print sys.exc_info()[0]
        print "string that caused issue: {0}".format(s)
        return []

def getSentences(s):
    return nltk.sent_tokenize(s)
