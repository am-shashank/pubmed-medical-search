def removePunctuation(tokens):
    import string
    return [t.strip(string.punctuation) for t in tokens 
            if t not in string.punctuation 
                 and t.strip(string.punctuation) != ""]

def toLowercase(tokens):
    return [t.lower() for t in tokens]
