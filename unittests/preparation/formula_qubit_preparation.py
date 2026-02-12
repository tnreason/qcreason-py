import math
import unittest

from qcreason import preparation, simulation

CIRCUIT_PROVIDER = "PennyLaneSimulator"


class PreparationTest(unittest.TestCase):
    def test_statistic_preparation_amplification_free(self):
        operations = preparation.get_hadamard_gates(["a", "b", "c"]) + preparation.generate_formula_operations(
            ["and", ["imp", "b", "c"], ["not", "a"]])
        circ = simulation.get_circuit(CIRCUIT_PROVIDER)(operations=operations)
        samples = circ.run(shots=100)
        for idx, row in samples.iterrows():
            self.assertTrue(row["(not_a)"] ^ row["a"])
            self.assertTrue(row["(imp_b_c)"] == (not row["b"] or row["c"]))
            self.assertTrue(row["(and_(imp_b_c)_(not_a))"] == (row["(imp_b_c)"] and row["(not_a)"]))

    def test_statistic_preparation_with_amplification(self):
        weightedFormulaDict = {"f1": ["and", ["imp", "b", "c"], ["not", "a"], True]}
        for amplificationNum in [0, 1, 5]:
            operations = preparation.amplify_ones_state(
                preparation.get_hln_ca_operations(weightedFormulaDict),
                amplificationColors=["ancilla_(and_(imp_b_c)_(not_a))"], amplificationNum=amplificationNum
            )
            circ = simulation.get_circuit(CIRCUIT_PROVIDER)(operations=operations)
            samples = circ.run(shots=10)
            for idx, row in samples.iterrows():
                self.assertTrue(row["(not_a)"] ^ row["a"])
                self.assertTrue(row["(imp_b_c)"] == (not row["b"] or row["c"]))
                self.assertTrue(row["(and_(imp_b_c)_(not_a))"] == (row["(imp_b_c)"] and row["(not_a)"]))

    def test_hard_formulas(self):
        weightedFormulas = {
            "f1": ["imp", "sledz", "jaszczur", True],
            "f2": ["and", "jaszczur", "kaczka", False],
            "f3": ["or", "sledz", "kaczka", -1]
        }
        operations = preparation.amplify_ones_state(
            preparation.get_hln_ca_operations(weightedFormulas),
            amplificationColors=["ancilla_(and_(imp_b_c)_(not_a))"], amplificationNum=0
        )
        ancillaVariables = ['ancilla_(or_sledz_kaczka)', 'ancilla_(imp_sledz_jaszczur)',
                            'ancilla_(and_jaszczur_kaczka)']
        circ = simulation.get_circuit(CIRCUIT_PROVIDER)(operations=operations,
                                                        measured_qubits=["(imp_sledz_jaszczur)",
                                                                         "(and_jaszczur_kaczka)"] + ancillaVariables)

        shotNum = 100
        samples = circ.run(shots=shotNum)

        for idx, row in samples.iterrows():
            ## Hard formulas need to be satisfied when sampling ancillas are 1
            self.assertTrue(not all([row[ancilla] for ancilla in ancillaVariables]) or (
                    row["(imp_sledz_jaszczur)"] and not row["(and_jaszczur_kaczka)"]))

    def test_single_soft_formula(self):
        canParam = 0.5
        shotNum = 1000
        tolerance = 0.1
        amplificationNum = 2

        weightedFormulas = {
            "f3": ["and", "sledz", "kaczka", canParam]
        }
        """
        Probability before normalization:
        1 & 1
        1 & exp[canParam]
        """
        operations = preparation.amplify_ones_state(
            preparation.get_hln_ca_operations(weightedFormulas),
            amplificationColors=["ancilla_(and_sledz_kaczka)"],
            amplificationNum=amplificationNum)
        circ = simulation.get_circuit(CIRCUIT_PROVIDER)(operations=operations,
                                                        measured_qubits=["(and_sledz_kaczka)",
                                                                         "ancilla_(and_sledz_kaczka)"])
        samples = circ.run(shots=shotNum)
        formulaTrue = len(samples[samples[["(and_sledz_kaczka)", "ancilla_(and_sledz_kaczka)"]].eq(1).all(axis=1)])
        accepted = len(samples[samples[["ancilla_(and_sledz_kaczka)"]].eq(1).all(axis=1)])

        self.assertTrue(abs(formulaTrue / accepted - (math.e) ** canParam / (3 + (math.e) ** canParam)) < tolerance)

    def test_multiple_frustrated_soft_formulas(self):
        canParam = 0.5
        shotNum = 1000
        tolerance = 0.05
        amplificationNum = 2

        weightedFormulas = {
            "f3": ["and", "sledz", "kaczka", canParam],
            "f4": ["not", "sledz", canParam]
        }
        """
        Probability before normalization:
        exp[canParam] & 1
        exp[canParam] & exp[canParam]
        """
        operations = preparation.amplify_ones_state(
            preparation.get_hln_ca_operations(weightedFormulas),
            amplificationColors=["ancilla_(and_sledz_kaczka)", "ancilla_(not_sledz)"],
            amplificationNum=amplificationNum)
        circ = simulation.get_circuit(CIRCUIT_PROVIDER)(operations=operations, measured_qubits=["(and_sledz_kaczka)",
                                                                                                "ancilla_(and_sledz_kaczka)",
                                                                                                "ancilla_(not_sledz)"])
        samples = circ.run(shots=shotNum)
        formulaTrue = len(samples[
                              samples[["(and_sledz_kaczka)", "ancilla_(and_sledz_kaczka)", "ancilla_(not_sledz)"]].eq(
                                  1).all(axis=1)])
        accepted = len(samples[samples[["ancilla_(and_sledz_kaczka)", "ancilla_(not_sledz)"]].eq(1).all(axis=1)])

        self.assertTrue(abs(formulaTrue / accepted - (math.e) ** canParam / (1 + 3 * (math.e) ** canParam)) < tolerance)

    def test_wolfram_codes(self):
        operations = preparation.get_hadamard_gates(["a", "b", "c"]) + preparation.generate_formula_operations(
            ["8", ["11", "a", "c"], ["1", "b"]])
        circ = simulation.get_circuit(CIRCUIT_PROVIDER)(operations = operations)
        shotNum = 10
        results = circ.run(shots=shotNum)
        for idx, row in results.iterrows():
            self.assertTrue(row["b"] == (not row["(1_b)"]))  # 1 is not
            self.assertTrue(row["(11_a_c)"] == (not row["a"] or row["c"]))  # 11 is imp
            self.assertTrue(row["(8_(11_a_c)_(1_b))"] == (row["(11_a_c)"] and row["(1_b)"]))  # 8 is and
