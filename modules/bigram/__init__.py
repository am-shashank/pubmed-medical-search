import get_tokens
import clean_tokens
import ngram
from collections import Counter
import math

class BigramModel:
    def __init__(self, trainfiles):
        self.unigrams = Counter()
        self.bigrams = Counter()

        for f in trainfiles:
            print f
            with open(f, 'r') as data:
                lines = data.readlines()
                for l in lines:
                    print l
                    for s in get_tokens.getSentences(l):
                        tokens = get_tokens.tokenizeString(s)
                        tokens = clean_tokens.cleanTokens(tokens)
                        tokens = ["<s>"] + tokens + ["</s>"]
                        self.unigrams.update(tokens)
                        self.bigrams.update(ngram.getNgrams(tokens, 2))

        unk = "<UNK>"
        unkCount = 0;
        removed = []
        for word in self.unigrams.keys():
            if self.unigrams[word] == 1:
                unkCount += 1
                del self.unigrams[word]
                removed.append(word)

        self.unigrams[unk] = unkCount
        for b in self.bigrams.keys():
            split = b.split(" ")
            count = self.bigrams[b]
            updateVal = ""
            if split[0] in removed and split[1] in removed:
                updateVal = "{} {}".format(unk, unk)
            elif split[0] in removed:
                updateVal = "{} {}".format(unk, split[1])
            elif split[1] in removed:
                updateVal = "{} {}".format(split[0], unk)
            self.bigrams.update({updateVal: count})
            if updateVal != "":
                del self.bigrams[b]

        self.N = len(self.unigrams)

    def logprob(self, priorContext, targetWord):
        if targetWord not in self.unigrams:
            return 0

        tokens = get_tokens.tokenizeString(priorContext)
        if len(tokens) == 0:
            return 0

        prevWord = tokens[-1]
        bigram = "{} {}".format(prevWord, targetWord)
        prob = self.bigrams[bigram] / float(self.unigrams[prevWord])
        return math.log(prob, 2) if prob != 0.0 else prob


    def printWords(self):
        print "-- UNIGRAMS --"
        for w in self.unigrams:
            print w
        print "\n-- BIGRAMS --"
        for b in self.bigrams:
            print b


