def createProbMatrix(probDict):
    labelList = []
    for l1, d in probDict.items():
        labelList.append(l1)
        for l2 in d:
            labelList.append(l2)
    labelList = set(labelList)

    probMatrix = {}
    for l1 in labelList:
        probMatrix[l1] = {}
        # probMatrix[l1][l1] = 0.0
        for l2 in labelList:
            probMatrix[l1][l2] = probDict[l1][l2] \
                                    if l1 in probDict and l2 in probDict[l1] \
                                    else 0.0
    # for l,d in probMatrix.items():
        # for l2 in d:
            # print "{} -> {} : {}".format(l, l2, probMatrix[l][l2])

    return probMatrix
