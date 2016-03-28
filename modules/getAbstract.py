from extract_abstract import getAbstractTexts
import sys

results = getAbstractTexts(sys.argv[2], sys.argv[1])
for text, label in results:
    print text
    print label
