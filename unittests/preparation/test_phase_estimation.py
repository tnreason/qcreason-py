import unittest

from qcreason import preparation, simulation


class PhaseEstimationTest(unittest.TestCase):
    """
    Checks the phase estimation
    """



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
