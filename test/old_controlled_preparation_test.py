import unittest

from qcreason import preparation, simulation

circuitProvider = "PennyLaneCircuit"


class PreparationTest(unittest.TestCase):
    def test_statistic_preparation_amplification_free(self):

        circ = simulation.get_circuit(circuitProvider)(["a", "b", "c"])
        circ = preparation.add_formula_to_circuit(circ, ["and", ["imp", "b", "c"], ["not", "a"]])
        circ.add_measurement(["a", "b", "c", "(not_a)", "(imp_b_c)", "(and_(imp_b_c)_(not_a))"])

        samples = circ.run(shots=100)

        for idx, row in samples.iterrows():
            self.assertTrue(row["(not_a)"] ^ row["a"])
            self.assertTrue(row["(imp_b_c)"] == (not row["b"] or row["c"]))
            self.assertTrue(row["(and_(imp_b_c)_(not_a))"] == (row["(imp_b_c)"] and row["(not_a)"]))

    def test_statistic_preparation_with_amplification(self):
        weightedFormulaDict = {"f1": ["and", ["imp", "b", "c"], ["not", "a"], True]}
        circ = simulation.get_circuit(circuitProvider)(["a", "b", "c"])
        circ = preparation.compute_and_activate(
            circ, weightedFormulaDict, atomColors=["a", "b", "c"]
        )
        for amplificationNum in [0, 1, 5]:
            circ = preparation.amplify(circ, weightedFormulaDict, amplificationNum=amplificationNum,
                                       atomColors=["a", "b", "c"])
            circ.add_measurement(["a", "b", "c", "(not_a)", "(imp_b_c)", "(and_(imp_b_c)_(not_a))", "samplingAncilla"])
            samples = circ.run(shots=10)
            for idx, row in samples.iterrows():
                self.assertTrue(row["(not_a)"] ^ row["a"])
                self.assertTrue(row["(imp_b_c)"] == (not row["b"] or row["c"]))
                self.assertTrue(row["(and_(imp_b_c)_(not_a))"] == (row["(imp_b_c)"] and row["(not_a)"]))

    def test_statistic_ancilla(self):

        disVariables = ["sledz", "jaszczur", "kaczka"]
        weightedFormulas = {
            "f1": ["imp", "sledz", "jaszczur", True],
            "f2": ["and", "jaszczur", "kaczka", False],
            "f3": ["or", "sledz", "kaczka", -1]
        }

        circ = simulation.get_circuit(circuitProvider)(disVariables)
        circ = preparation.compute_and_activate(circ, weightedFormulas, atomColors=disVariables)
        circ.add_measurement(disVariables + ["(imp_sledz_jaszczur)", "(and_jaszczur_kaczka)"] + ["samplingAncilla"])

        shotNum = 100
        samples = circ.run(shots=shotNum)

        for idx, row in samples.iterrows():
            self.assertTrue(not row["samplingAncilla"] or row["(imp_sledz_jaszczur)"])
            self.assertTrue(not row["samplingAncilla"] or not row["(and_jaszczur_kaczka)"])

    def test_wolfram_codes(self):
        circ = simulation.get_circuit("PennyLaneCircuit")(["a", "b", "c"])
        circ.add_hadamards(["a", "b", "c"])
        circ = preparation.add_formula_to_circuit(circ, ["8", ["11", "a", "c"], ["1", "b"]])
        circ.add_measurement(["a", "b", "c", "(1_b)", "(11_a_c)", "(8_(11_a_c)_(1_b))"])

        # Run the circuit
        shotNum = 10
        results = circ.run(shots=shotNum)
        for idx, row in results.iterrows():
            self.assertTrue(row["b"] == (not row["(1_b)"]))  # 1 is not
            self.assertTrue(row["(11_a_c)"] == (not row["a"] or row["c"]))  # 11 is imp
            self.assertTrue(row["(8_(11_a_c)_(1_b))"] == (row["(11_a_c)"] and row["(1_b)"]))  # 8 is and
