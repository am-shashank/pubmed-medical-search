def getBigrams(tokens):
    return getNgrams(tokens, 2)

def getNgrams(tokens, n):
    ngrams = []
    for i in range(0, len(tokens) - (n-1)):
        s = ""
        for j in range (0,n):
            s += tokens[i+j]
            if j < n-1:
                s += " "
        ngrams.append(s)
    return ngrams
