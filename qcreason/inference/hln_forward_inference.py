from qcreason import preparation
from qcreason import simulation

from qcreason.inference.rejection_sampling import filter_results


class HLNForwardCircuitSampler:

    def __init__(self, formulaDict, canParamDict, circuitProvider=preparation.standardCircuitProvider,
                 amplificationNum=2, shotNum=1000):
        self.formulaDict = formulaDict
        self.canParamDict = canParamDict

        self.circuitProvider = circuitProvider
        self.amplificationNum = amplificationNum
        self.shotNum = shotNum

    def infer_meanParam(self, formulaKeys, verbose=False):
        operations = preparation.amplify_ones_state(
            preparingOperations=preparation.get_hln_ca_operations(
                {formulaKey: self.formulaDict[formulaKey] + [self.canParamDict[formulaKey]] for formulaKey in
                 self.formulaDict}),
            amplificationColors=["ancilla_" + preparation.get_formula_string(self.formulaDict[formulaKey]) for
                                 formulaKey in
                                 self.formulaDict],
            amplificationNum=self.amplificationNum
        )
        circuit = simulation.get_circuit(self.circuitProvider)(
            operations=operations,
            measured_qubits=[preparation.get_formula_string(self.formulaDict[formulaKey]) for formulaKey in
                             formulaKeys] +
                            ["ancilla_" + preparation.get_formula_string(self.formulaDict[formulaKey]) for formulaKey
                             in self.formulaDict])
        #circuit.add_measurement(
        #)  # ! Need to measure all ancilla, not only those infered
        samples = filter_results(circuit.run(shots=self.shotNum), ancillaColors=[
            "ancilla_" + preparation.get_formula_string(self.formulaDict[formulaKey]) for formulaKey in
            self.formulaDict])

        if verbose:
            print("Out of {} shots, {} samples have been accepted.".format(self.shotNum, len(samples)))

        return {formulaKey: samples[preparation.get_formula_string(self.formulaDict[formulaKey])].mean() for
                formulaKey in formulaKeys}

    # def old_infer_meanParam(self, formulaKeys, verbose=False):
    #     # OLD method using the sngle ancilla amplification procedure
    #     circuit = representation.get_amplified_circuit(
    #         {formulaKey: self.formulaDict[formulaKey] + [self.canParamDict[formulaKey]] for formulaKey in
    #          self.formulaDict}, self.amplificationNum, atomColors=representation.get_atoms(self.formulaDict),
    #         circuitProvider=self.circuitProvider)
    #     circuit.add_measurement(
    #         [representation.get_formula_string(self.formulaDict[formulaKey]) for formulaKey in formulaKeys] + [
    #             representation.standardAncillaColor])
    #     samples = filter_results(circuit.run(shots=self.shotNum))
    #
    #     if verbose:
    #         print("Out of {} shots, {} samples have been accepted.".format(self.shotNum, len(samples)))
    #
    #     return {formulaKey: samples[representation.get_formula_string(self.formulaDict[formulaKey])].mean() for
    #             formulaKey in formulaKeys}
