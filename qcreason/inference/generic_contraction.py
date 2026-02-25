from qcreason import preparation
from qcreason import simulation

from qcreason.inference import rejection_sampling as rs

from tnreason import engine


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
        operations = preparation.amplify_ones_state(
            preparingOperations=preparation.tn_to_circuit(self.coreDict, ancillaPrefix="ancilla_"),
            amplificationColors=["ancilla_" + coreKey for coreKey in self.coreDict],
            amplificationNum=self.specDict.get("amplificationNum", 0))
        circuit = simulation.get_circuit(
            self.specDict.get("circuitProvider", preparation.standardCircuitProvider))(operations=operations,
                                                                                       measured_qubits=self.openColors + [
                                                                                              "ancilla_" + coreKey for
                                                                                              coreKey in self.coreDict])
        filteredResults = rs.filter_results(circuit.run(shotNum=self.specDict.get("shots", 1000)),
                                            ancillaColors=["ancilla_" + coreKey for coreKey in self.coreDict],
                                            keepColors=self.openColors)
        return engine.get_core("PandasCore")(colors=self.openColors,
                                               shape=[get_and_check_shape_dict(self.coreDict)[color] for color in
                                                      self.openColors],
                                               values=filteredResults)


def get_and_check_shape_dict(coreDict):
    """
    Extracts the colors and checks whether all leg dimensions are 2
    :param coreDict: tnreason tensor network, i.e. a dictionary of tensor cores
    :return: shapes
    """
    shapeDict = {}
    for coreKey in coreDict:
        for color, dim in zip(coreDict[coreKey].colors, coreDict[coreKey].values.shape):
            shapeDict[color] = dim
            if not dim == 2:
                raise ValueError(
                    "Only leg dimension 2 is supported so far, but core '{}' has leg '{}' with dimension {}.".format(
                        coreKey, color, dim))
    return shapeDict
