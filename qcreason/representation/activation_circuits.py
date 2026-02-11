import numpy as np


def probability_to_angle(prob):
    """
    Calculates an angle alpha, such that R_y(alpha) rotates (1,0) to (sqrt(1-prob), sqrt(prob))
    :param prob: probability value between 0 and 1
    :return: angle alpha
    """
    return 2 * np.arccos(np.sqrt(1 - prob))


def single_canParam_to_activation_circuit(canParam, statisticColor, ancillaColor, interpretationList=[0, 1]):
    """
    Prepares the activation circuit for an activation tensor of a SingleSoftFeature, such as those appearing in Hybrid Logic Networks.
    :param canParam: canonical parameter (float/int) or hard feature (bool)
    :param statisticColor: color of the qubit representing the statistic
    :param ancillaColor: color of the ancilla qubit to be used for activation
    :param interpretationList: interpretation vector of the statistic
    :return: operationsList implementing the activation circuit
    """

    if isinstance(canParam, bool):
        return [{"unitary": "MCX", "target": [ancillaColor], "control": {statisticColor: int(canParam)}}]
    else:
        maxValue = np.exp(max(0, canParam))
        return [{"unitary": "MCRY", "target": [ancillaColor], "control": {statisticColor: val},
                 "parameters": {"angle": probability_to_angle(np.exp(val * canParam) / maxValue)}} for val in
                interpretationList]


def activation_core_to_circuit(actCore, maxValue, ancillaColor="ancilla"):
    """

    :param actCore: tnreason tensor core (activation core of a feature)
    :param maxValue: maximum value (or upper bound) for the coefficients)
    :return:
    """
    return [{"unitary": "MCRY", "target": [ancillaColor],
             "control": {color: idx[i] for i, color in enumerate(actCore.colors)},
             "parameters": {"angle": probability_to_angle(
                 actCore[{color: idx[i] for i, color in enumerate(actCore.colors)}] / maxValue)}} for idx in
            np.ndindex(*actCore.shape)]


def tn_to_circuit(coresDict, ancillaPrefix="ancilla_"):
    """
    Convert a tnreason dictionary of tensor cores into a quantum circuit representation using ancilla qubits for each core.
    :param coresDict: Dictionary where keys are core names and values are tnreason tensor cores.
    :param ancillaPrefix: Prefix for naming ancilla qubits corresponding to each core.
    :return: List of operations implementing the quantum circuit.
    """
    operationsList = [{"unitary": "H", "target": [color]} for color in get_colors(coresDict)]
    for coreName, core in coresDict.items():
        operationsList += activation_core_to_circuit(core, maxValue=core[core.get_argmax()],
                                                     ancillaColor=f"{ancillaPrefix}{coreName}")
    return operationsList

def get_colors(coresDict):
    colors = set()
    for core in coresDict.values():
        colors.update(set(core.colors))
    return list(colors)