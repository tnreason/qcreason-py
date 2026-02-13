import unittest

from qcreason import inference


class RejectionBackwardTest(unittest.TestCase):
    def test_backward_inference(self):
        formulaDict = {
            "f1": ["imp", "a", "b"],
            "f2": ["not", "d"],
            "f3": ["or", "a", "c"]
        }

        satisfactionDict = {
            "f1": 0.7,
            "f2": 1,
            "f3": 0.5
        }

        backwardInferer = inference.HLNBackwardCircuitAlternator(formulaDict, targetMeanDict=satisfactionDict,
                                                                 shotNum=1000, amplificationNum=2)
        backwardInferer.alternate(10)

        testInferer = inference.HLNForwardCircuitSampler(formulaDict, backwardInferer.canParamDict, shotNum=10000,
                                                         amplificationNum=2)
        matchedDict = testInferer.infer_meanParam(["f1", "f2", "f3"])

        self.assertTrue(matchedDict["f2"] == 1)
        self.assertTrue(abs(matchedDict["f1"] - 0.7) < 0.1)
        self.assertTrue(abs(matchedDict["f3"] - 0.5) < 0.1)
