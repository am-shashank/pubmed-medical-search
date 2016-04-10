from srilm import srilm_ppl
from operator import itemgetter
import pickle
# from sklearn.metric import confusion_matrix

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

def lm_predict_xml(models, test_file, pred_file, top_labels=1):
    # labelPredictions = []
    # for i in range(top_labels):
    #	labelPredictions.append([])
    with open(pred_file, 'w') as pred:
        with open(test_file, 'r') as test:
	    abstract = pickle.load(test)
	    allAbstractText = abstract.findall("AbstractText")
            for abstractText in allAbstractText:
		line = abstractText.text
		actualLabel = None
		# print abstractTest.attrib
		if "Label" in abstractText.attrib:
			actualLabel = abstractText.attrib["Label"]
			print actualLabel
                print "PREDICTING FOR LINE:"
                print line.encode("utf-8","ignore")
                ppls = []
                for label, modelFile in models:
                    print label, modelFile
                    try:
                        ppl = srilm_ppl(modelFile, line.encode("utf-8","ignore"))
                    except Exception as e:
                        print "error in calculating ppl"
                        ppl = 1000000
                    print ppl
                    ppls.append((label, ppl))
                ppls.sort(key=lambda tup: tup[1])
                # bestLabel = min(ppls, key=itemgetter(1))[0]
		if actualLabel is not None:
			pred.write(actualLabel + ":")
		else:
			pred.write(" :")
                for i in range(0, top_labels):
		    # labelPredictions[i].append(ppls[i][0])
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

def lm_predict_full_text(model_file, test_file, pred_file, top_labels=1):
    ppls = []
    paragraphs = []
    with open(pred_file, 'w') as pred:
        with open(test_file, 'r') as test:
            for line in test:
		paragraphs.append(line)
		try:
                    ppl = srilm_ppl(model_file, line)
                except Exception as e:
                    print "error in calculating ppl"
                    ppl = 1000000
		ppls.append(ppl)
	sorted_idx = [i[0] for i in sorted(enumerate(ppls), key=lambda x:x[1])] # sorted list of ppls
	for i in range(top_labels):
	    pred.write(paragraphs[sorted_idx[i]])
	    pred.write("\n")
		
	
	
		
		
		
