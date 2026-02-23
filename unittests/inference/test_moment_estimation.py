import unittest

from qcreason import inference

class MomentEstimationTest(unittest.TestCase):
    def test_extract_moment(self):
        """
        Checks the moment extraction from the grover phase estimation
        :return:
        """
        from qcreason.inference import moment_estimation as me

        self.assertEqual(me.extract_moment([1, 0]), 0)
        self.assertEqual(me.extract_moment([0, 0]), 1)

        self.assertTrue(abs(me.extract_moment([0, 1, 0])-0.5) < 0.01)

    def test_contradiction(self):
        estimator = inference.MomentEstimator(qSamplePrep=[{"unitary": "H", "target": ["X_0"]}],
                                              circuitProvider="PennyLaneSimulator")
        for formula in [["0", "X_0"], ["and", "X_0", ["not", "X_0"]]]:
            estMom = estimator.estimate_moment(formula, precision=2, distributedQubits=["X_0"])
            self.assertEqual(estMom, 0)

    def test_tautology(self):
        estimator = inference.MomentEstimator(qSamplePrep=[{"unitary": "H", "target": ["X_0"]}],
                                              circuitProvider="PennyLaneSimulator")
        for formula in [["3", "X_0"], ["or", "X_0", ["not", "X_0"]]]:
            estMom = estimator.estimate_moment(formula, precision=2, distributedQubits=["X_0"])
            self.assertEqual(estMom, 1)

    def test_half_moment(self):
        estimator = inference.MomentEstimator(qSamplePrep=[{"unitary": "H", "target": ["X_0"]}],
                                              circuitProvider="PennyLaneSimulator")

        for formula in [["not","X_0"], ["2","X_0"]]:
            estMom = estimator.estimate_moment(formula, precision=3, distributedQubits=["X_0"])
            self.assertTrue(abs(estMom-0.5) < 0.01)