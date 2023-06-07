import os
import numpy as np
from Constants.constants import UNDER_SCOPE, DOT, MIN_ONE


def getModelPath(noiseFilterModelDir):
    fileList = os.listdir(noiseFilterModelDir)
    accList = []

    for fileName in fileList:
        fileAbsPath = os.path.join(noiseFilterModelDir, fileName)
        if not os.path.isfile(fileAbsPath):
            continue
        acc = float(fileName.split(UNDER_SCOPE)[1])
        accList.append(acc)

    return os.path.join(noiseFilterModelDir, fileList[np.argmax(accList)])


def filterFileListBySuffix(list, suffix):
    resultList = []
    for element in list:
        elementSuffix = element.split(DOT)[MIN_ONE]
        if elementSuffix == suffix:
            resultList.append(element)
    return resultList
