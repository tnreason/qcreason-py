from qcreason.inference.hln_forward_inference import HLNForwardCircuitSampler

import numpy as np


class HLNBackwardCircuitAlternator:
    """
    Does Iterative Proportional Fitting on Hybrid Logic Netowrks using the ForwardCircuitSampler as a subroutine.
    """

    def __init__(self, formulaDict, targetMeanDict, canParamDict=None, **infereneSpecDict):
        self.formulaDict = formulaDict
        self.targetMeanDict = targetMeanDict

        if canParamDict is None:
            self.canParamDict = {formulaKey: 0 for formulaKey in formulaDict}
            self.canParamDict.update({
                **{formulaKey: True for formulaKey in targetMeanDict if targetMeanDict[formulaKey] == 1},
                **{formulaKey: False for formulaKey in targetMeanDict if targetMeanDict[formulaKey] == 0}})
        else:
            self.canParamDict = canParamDict

        self.circuitProvider = infereneSpecDict.get("circuitProvider", "PennyLaneSimulator")
        self.amplificationNum = infereneSpecDict.get("amplificationNum", 2)
        self.shotNum = infereneSpecDict.get("shotNum", 1000)

    def alternate(self, iterationNum=10, optimizationKeys=None, verbose=False):
        if optimizationKeys is None:
            optimizationKeys = list(self.formulaDict.keys())
        for iteration in range(iterationNum):
            if verbose:
                print("### Iteration {} ###".format(iteration + 1))
            for formulaKey in optimizationKeys:
                if not isinstance(self.canParamDict[formulaKey], bool):
                    self.update_canParam(formulaKey, verbose=verbose)

    def update_canParam(self, formulaKey, verbose=False):
        forwardInferer = HLNForwardCircuitSampler(self.formulaDict, self.canParamDict,
                                                  amplificationNum=self.amplificationNum, shotNum=self.shotNum,
                                                  circuitProvider=self.circuitProvider)
        currentMean = forwardInferer.infer_meanParam([formulaKey], verbose=verbose)[formulaKey]

        if currentMean in [0,1] or np.isnan(currentMean):
            # Can happen due to limitations in the rejection sampling. Do nothing in this case.
            print("Cannot update formula {}: current mean is {}.".format(formulaKey, currentMean))
        else:
            if verbose:
                print("Updating formula {}, mean from {} to {}.".format(formulaKey, currentMean,
                                                                        self.targetMeanDict[formulaKey]))
            self.canParamDict[formulaKey] += np.log(
                self.targetMeanDict[formulaKey] / (1 - self.targetMeanDict[formulaKey]) * (
                        1 - currentMean) / currentMean)
