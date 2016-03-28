from lxml import etree
import xmltodict

# extracts MedlineCitation element from file
# returns dict representing the XML element
def extractXML(filepath, pmid):
    with open(filepath, 'r') as f:
        inCitation = False
        pmidMatch = False
        citString = ""

        context = etree.iterparse(f, events=("start", "end"))
        context = iter(context)
        event, root = context.next()
            
        for event, elem in context:
            if elem.tag == "MedlineCitation" and event == "start":
                citString = etree.tostring(elem)

            if elem.tag == "PMID" and event == "start" and elem.text == str(pmid):
                root.clear()
                break

            elem.clear()

    return xmlStringToDict(citString)

def xmlStringToDict(xmlString):
    return xmltodict.parse(xmlString)

def getAbstractTexts(filepath, pmid):
    # print "getting abstract text: {}, {}".format(pmid, filepath)
    ab = extractXML(filepath, pmid)
    texts = ab.get("MedlineCitation",{}).get("Article",{}).get("Abstract",{})
    if texts == None:
        return []

    if "AbstractText" in texts:
        textList = texts["AbstractText"]
        return [(t["#text"], t["@Label"]) for t in textList \
                if "#text" in t and "@Label" in t]
    else:
        return []

def getLabelSequence(filepath, pmid):
    ab = extractXML(filepath, pmid)
    texts = ab.get("MedlineCitation",{}).get("Article",{}).get("Abstract",{})
    if texts == None:
        return []

    if "AbstractText" in texts:
        textList = texts["AbstractText"]
        textList = [t["@Label"] for t in textList \
                    if "#text" in t and "@Label" in t]
        return ["_START_"] + textList + ["_END_"]
    else:
        return []
    
