import unittest

from qcreason import preparation, simulation

import numpy as np


class PhaseEstimationTest(unittest.TestCase):
    """
    Checks the phase estimation
    """

    def phaseShift_template(self, phaseList, shotNum):
        """
        Tests whether the PhaseShift operator gets the phases 0.000 and 0.phaseList estimated
        :param phaseList: List of 0 and 1 giving the bits of the phase
        :param shotNum: Number of samples to verify
        :return:
        """
        precision = len(phaseList)
        angle = np.sum([phaseBit * 2 ** (-i) for i, phaseBit in enumerate(phaseList)]) * np.pi
        testOperator = [{"unitary": "P", "target": ["X_0"], "parameters": {"angle": angle}}]
        ops = preparation.get_phase_estimator(testOperator, precision, distributedQubits=["X_0"])
        simulator = simulation.get_circuit()(operations=ops, measured_qubits=[f"P_{j}" for j in range(precision)])
        counted = simulator.run(shotNum).value_counts()
        if np.sum(phaseList) == 0:
            self.assertEqual(counted.shape[0], 1)
        else:
            self.assertEqual(counted.shape[0], 2)
        self.assertEqual(set(counted.index.tolist()),
                         {tuple(0 for _ in range(precision)), tuple(phaseB for phaseB in phaseList)})

    def test_phaseShift(self):
        """Test various precisions and qubit counts."""
        test_cases = [
            ([0, 0], 100),
            ([0, 1, 0], 100),
            ([1, 0, 1], 100)
        ]
        for p, s in test_cases:
            self.phaseShift_template(p, s)

    def hadamard_template(self, dOrder, precision, shotNum):
        """
        Checks wheter the phase estimator of the Hadamard reproduces either 0.00... or 0.10... (phases of 0 and 0.5 of Hadamard eigenvalues)
        :param dOrder: Number of
        :param precision:
        :param shotNum:
        :return:
        """
        testOperator = [{"unitary": "H", "target": [f"X_{j}"]} for j in range(dOrder)]
        ops = preparation.get_phase_estimator(testOperator, precision,
                                              distributedQubits=[f"X_{j}" for j in range(dOrder)])

        simulator = simulation.get_circuit()(operations=ops, measured_qubits=[f"P_{j}" for j in range(precision)])
        df = simulator.run(shotNum)
        self.assertFalse(df[f"P_{0}"].value_counts()[0] in [0, shotNum])
        for j in range(1, precision):
            self.assertEqual(df[f"P_{j}"].value_counts()[0], shotNum)

    def test_hadamard_phases(self):
        """Test various precisions and qubit counts."""
        test_cases = [
            (2, 2, 100),
            (1, 1, 100),
            (1, 3, 100)
        ]
        for d, p, s in test_cases:
            self.hadamard_template(d, p, s)
