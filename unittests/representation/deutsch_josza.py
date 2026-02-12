import unittest

from qcreason import representation, engine


class DeutschJoszaTest(unittest.TestCase):
    """
    Implements the Inversion Test on basis encoding states
    """

    def test_constant(self):
        ## When a formula is a tautology or unsatisfiable (Thing/Nothing), then Deutsch-Josza brings prob 1 of groundstate
        self.assertTrue(1 == self.deutsch_josza_template(formula=["3", "sledz"], distributedQubits=["sledz"]))
        self.assertTrue(1 == self.deutsch_josza_template(formula=["0", "sledz"], distributedQubits=["sledz"]))
        self.assertTrue(1 == self.deutsch_josza_template(formula=["31", "sledz", "jaszczur"],
                                                         distributedQubits=["sledz", "jaszczur"]))
        self.assertTrue(1 == self.deutsch_josza_template(formula=["0", "sledz", "jaszczur"],
                                                         distributedQubits=["sledz", "jaszczur"]))

    ## Does the auxiliary variable "(not_sledz)" manipulate the algorithm?
    # def test_satisfiable(self):
    #    ratio = self.deutsch_josza_template(formula=["and", "sledz", ["not", "sledz"]], distributedQubits=["sledz"],
    #                                        shotNum=100)
    # self.assertTrue(ratio==1)

    def deutsch_josza_template(self, formula, distributedQubits, shotNum=10, headColor="Y"):
        hadamardOperations = [{"unitary": "H", "target": [dQubit]} for dQubit in distributedQubits]
        operations = (hadamardOperations
                      + [{"unitary": "X", "target": [headColor]}, {"unitary": "H", "target": [headColor]}]
                      + representation.generate_formula_operations(formula, headColor=headColor)
                      + hadamardOperations
                      )
        circuit = engine.get_circuit("PennyLaneSimulator")(operations=operations, measured_qubits=distributedQubits)
        samples = circuit.run(shotNum)
        return sum(
            [1 for i, row in samples.iterrows() if all([row[dQubit] == 0 for dQubit in distributedQubits])]) / shotNum