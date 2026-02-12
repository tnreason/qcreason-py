from qcreason import representation
from qcreason import engine

from qcreason.reasoning import rejection_sampling as rs

from tnreason import engine as tnengine


class QCReasonParticleContractor:
    """
    Implements a particle-based approximative and scale-ignoring contractor based on computational basis measurements of a quantum circuit constructed from the activation circuits.
    Possible improvement: Filter for directed and acyclic subset of cores, and prepare them without ancillas.
    """

    def __init__(self, coreDict={}, openColors=[], specDict={}):
        self.coreDict = {key: coreDict[key].clone() for key in coreDict}
        self.openColors = openColors
        self.specDict = specDict

    def contract(self):
        operations = representation.amplify_ones_state(
            preparingOperations=representation.tn_to_circuit(self.coreDict, ancillaPrefix="ancilla_"),
            amplificationColors=["ancilla_" + coreKey for coreKey in self.coreDict],
            amplificationNum=self.specDict.get("amplificationNum", 0))
        circuit = engine.get_circuit(
            self.specDict.get("circuitProvider", representation.standardCircuitProvider))(operations=operations,
                                                                                          measured_qubits=self.openColors + [
                                                                                              "ancilla_" + coreKey for
                                                                                              coreKey in self.coreDict])
        #circuit.add_measurement()
        filteredResults = rs.filter_results(circuit.run(shots=self.specDict.get("shots", 1000)),
                                            ancillaColors=["ancilla_" + coreKey for coreKey in self.coreDict],
                                            keepColors=self.openColors)
        return tnengine.get_core("PandasCore")(colors=self.openColors,
                                               shape=[get_shape_dict(self.coreDict)[color] for color in
                                                      self.openColors],
                                               values=filteredResults)


def get_shape_dict(coreDict):
    # ! So far only working for leg dimension 2
    shapeDict = {}
    for coreKey in coreDict:
        for color, dim in zip(coreDict[coreKey].colors, coreDict[coreKey].values.shape):
            shapeDict[color] = dim
            if not dim == 2:
                raise ValueError(
                    "Only leg dimension 2 is supported so far, but core '{}' has leg '{}' with dimension {}.".format(
                        coreKey, color, dim))
    return shapeDict
