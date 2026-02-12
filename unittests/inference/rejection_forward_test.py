import unittest

from qcreason import inference

import math


class RejectionForwardTest(unittest.TestCase):
    def test_forward_inference(self):
        circuitProvider = "PennyLaneSimulator"
        weightedFormulas = {
            "f1": ["imp", "sledz", "jaszczur", True],
            "f2": ["and", "jaszczur", "kaczka", False],
            "f3": ["or", "sledz", "kaczka", -1]
        }
        for amplificationNum in [0,1,5]: # For 2: No samples accepted
            inferer = inference.HLNForwardCircuitSampler(
                formulaDict={formulaKey: weightedFormulas[formulaKey][:-1] for formulaKey in weightedFormulas},
                canParamDict={formulaKey: weightedFormulas[formulaKey][-1] for formulaKey in weightedFormulas},
                circuitProvider=circuitProvider, amplificationNum=amplificationNum, shotNum=1000)
            empSat = inferer.infer_meanParam(["f1", "f2", "f3"], verbose=False)
            self.assertEqual(empSat["f1"], 1)
            self.assertEqual(empSat["f2"], 0)
            self.assertTrue(abs(empSat["f3"] - 1 / (math.e + 1)) < 0.1)
