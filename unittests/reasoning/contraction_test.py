import unittest

from qcreason import reasoning

from tnreason import engine as tnengine

import numpy as np


class ContractionTest(unittest.TestCase):
    def test_two_numpy_cores(self):
        testCoreDict = {
            "c1": tnengine.get_core("NumpyCore")(
                values=np.random.rand(2, 2),
                colors=["red", "blue"]
            ),
            "c2": tnengine.get_core("NumpyCore")(
                values=np.random.rand(2, 2),
                colors=["sledz", "blue"]
            )}

        pandasCore = reasoning.QCReasonParticleContractor(coreDict=testCoreDict,
                                                          openColors=["red", "sledz"],
                                                          specDict={"shots": 10000,
                                                                    "circuitProvider": "PennyLaneSimulator",
                                                                    "amplificationNum": 1}).contract()
        converted = tnengine.convert(pandasCore, "NumpyCore")
        self.assertTrue(converted.values.shape == (2, 2))

        compareContraction = tnengine.contract(coreDict=testCoreDict,
                                               openColors=["red", "sledz"])

        tolerance = 0.1

        self.assertTrue(abs((converted[0, 0] / converted[0, 1]) - (
                compareContraction[0, 0] / compareContraction[0, 1])) < tolerance)

        self.assertTrue(abs((converted[1, 0] / converted[1, 1]) - (
                compareContraction[1, 0] / compareContraction[1, 1])) < tolerance)
