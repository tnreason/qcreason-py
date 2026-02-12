from qcreason import preparation, simulation, inference

from qcreason.inference import backward_inference as bi

formulaDict = {
    "f1" : ["imp", "a", "b"],
    "f2" : ["not", "d"],
    "f3" : ["or", "a", "c"]
}

satisfactionDict = {
    "f1" : 0.7,
    "f2" : 1,
    "f3" : 0.5
}

inferer = bi.HLNBackwardCircuitAlternator(formulaDict, targetMeanDict=satisfactionDict, shotNum=10000, amplificationNum=2)
print(inferer.amplificationNum)
#print(inferer.canParamDict)

inferer.alternate(10, verbose=True)
