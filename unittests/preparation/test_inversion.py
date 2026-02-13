import unittest

from qcreason import preparation, simulation


class InversionTest(unittest.TestCase):
    """
    Implements the Inversion Test on basis encoding states
    """

    def test_same_formula(self):
        self.same_formula_template(formula=["eq", "A", "B"], distributedQubits=["A", "B"])
        self.same_formula_template(formula=["xor", ["not", "sledz"], "jaszczur"],
                                   distributedQubits=["jaszczur", "sledz"])

    def test_syntactically_equal(self):
        ## Need to have same subformulas, otherwise need to construct surrogates for that states.
        self.syntactically_equal_template(formula1=["or", "A", "B"], formula2=["14", "A", "B"],
                                          distributedQubits=["A", "B"])

    def test_equal_surrogate(self):
        formula1 = ["or", ["not", "A"], "B"]
        formula2 = ["imp", "A", "B"]
        distributedQubits = ["A", "B"]
        hadamardOperations = [{"unitary": "H", "target": [dQubit]} for dQubit in distributedQubits]
        operations = (hadamardOperations
                      + preparation.generate_formula_operations(formula1, headColor="Y")
                      + preparation.generate_formula_operations(formula2, adjoint=True, headColor="Y")
                      + preparation.generate_formula_operations(["not", "A"], adjoint=True)
                      + hadamardOperations
                      )
        circuit = simulation.get_circuit("PennyLaneSimulator")(operations=operations)
        samples = circuit.run(10)
        for i, row in samples.iterrows():
            self.assertTrue(all([row[dQubit] == 0 for dQubit in distributedQubits]))

    def same_formula_template(self, formula, distributedQubits):
        self.syntactically_equal_template(formula1=formula, formula2=formula, distributedQubits=distributedQubits)

    def syntactically_equal_template(self, formula1, formula2, distributedQubits, shotNum=10):
        hadamardOperations = [{"unitary": "H", "target": [dQubit]} for dQubit in distributedQubits]
        operations = (hadamardOperations
                      + preparation.generate_formula_operations(formula1, headColor="Y")
                      + preparation.generate_formula_operations(formula2, adjoint=True, headColor="Y")
                      + hadamardOperations
                      )
        circuit = simulation.get_circuit("PennyLaneSimulator")(operations=operations)
        samples = circuit.run(shotNum)
        for i, row in samples.iterrows():
            self.assertTrue(all([row[dQubit] == 0 for dQubit in distributedQubits]))
