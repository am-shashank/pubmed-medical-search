from srilm import srilm_ppl
from operator import itemgetter

def lm_predict(models, test_file, pred_file, top_labels=1):
    with open(pred_file, 'w') as pred:
        with open(test_file, 'r') as test:
            for line in test:
                print "PREDICTING FOR LINE:"
                print line
                ppls = []
                for label, modelFile in models:
                    print label, modelFile
                    try:
                        ppl = srilm_ppl(modelFile, line)
                    except Exception as e:
                        print "error in calculating ppl"
                        ppl = 1000000
                    print ppl
                    ppls.append((label, ppl))
                ppls.sort(key=lambda tup: tup[1])
                # bestLabel = min(ppls, key=itemgetter(1))[0]
                for i in range(0, top_labels):
                    pred.write(ppls[i][0])
                    print "predicted: ", ppls[i][0]
                    if i < top_labels - 1:
                        pred.write(",")
                pred.write("\n")

def lm_predict_string(models, s):
    ppls = []
    for label, modelFile in models:
        ppl = srilm_ppl(modelFile, s)
        ppls.append((label, ppl))
    bestLabel = min(ppls, key=itemgetter(1))[0]
    return (bestLabel, ppls)
