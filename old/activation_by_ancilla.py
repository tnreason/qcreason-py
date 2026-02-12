from qcreason.preparation import m2bp_formulas as mf

import numpy as np

## To be dropped, use activation_circuits and operations_transform instead

def probability_to_angle(prob):
    """
    Calculates an angle alpha, such that R_y(alpha) rotates (1,0) to (sqrt(1-prob), sqrt(prob))
    :param prob:
    :return:
    """
    return 2 * np.arccos(np.sqrt(1 - prob))

def calculate_angles(canParamDict):
    """
    ! For ancilla encoding of the product of activation tensors
    Calculate the angles for controlled rotations implementing a given exponential family distribution.
    :param canParamDict: specifies the distribution by canonical parameters, keys: statistic qubit colors to formulas, values: canonical parameters
    :return:
    """

    controlVariables = list(canParamDict.keys())
    maxValue = np.exp(sum([par for par in canParamDict.values() if par > 0 and not isinstance(par, bool)]))

    angleSlices = []

    for vals in np.ndindex(*(2,) * len(controlVariables)):
        if any([isinstance(canParamDict[controlVariables[i]], bool) and bool(vals[i]) != canParamDict[
            controlVariables[i]] for i in range(len(controlVariables))]):
            ## Then the distribution has no support
            angleSlices.append((0, {var: vals[i] for i, var in enumerate(controlVariables)}))
        else:
            ## Then the sampling probability is the quotient to the maxValue
            angleSlices.append((probability_to_angle(
                np.exp(sum([canParamDict[controlVariables[i]] * val for i, val in enumerate(vals) if
                            not isinstance(canParamDict[controlVariables[i]], bool)])) / maxValue),
                                {var: vals[i] for i, var in enumerate(controlVariables)}))

    return angleSlices

def compute_and_activate(circuit, weightedFormulaDict, atomColors, ancillaColor="samplingAncilla", adjoint=False):

    angleTuples = calculate_angles(get_color_param_dict(weightedFormulaDict))

    if adjoint:
        for angleTuple in angleTuples[::-1]:
            circuit.add_controlled_rotation((-angleTuple[0],angleTuple[1]), ancillaColor)
        for formulaKey in list(weightedFormulaDict.keys())[::-1]:
            circuit = mf.add_formula_to_circuit(circuit, weightedFormulaDict[formulaKey][:-1], adjoint=True)
        circuit.add_hadamards(atomColors)
        return circuit

    circuit.add_hadamards(atomColors)
    ## Compute the statistic formulas
    for formulaKey in weightedFormulaDict:
        circuit = mf.add_formula_to_circuit(circuit, weightedFormulaDict[formulaKey][:-1])

    ## Compute the sampling ancilla for activation
    for angleTuple in angleTuples:
        circuit.add_controlled_rotation(angleTuple, ancillaColor)
    return circuit

def get_color_param_dict(weightedFormulas):
    return {mf.get_formula_string(weightedFormulas[formulaKey][:-1]): weightedFormulas[formulaKey][-1] for formulaKey in
            weightedFormulas}

def reflect_groundstate(circuit):
    ## Reflect on ground state: X, multi-controlled Z, X
    for color in circuit.colors:
        circuit.add_slice(posDict={}, headColor=color)

    ## Phase flip of the all-one state
    if len(circuit.colors) == 1:
        circuit.add_PauliZ(circuit.colors[0])
    else:
        circuit.add_controlled_PauliZ({color : 1 for color in circuit.colors[:-1]}, circuit.colors[-1])

    for color in circuit.colors:
        circuit.add_slice(posDict={}, headColor=color)

    return circuit

def amplify(circuit, weightedFormulaDict, amplificationNum, atomColors, ancillaColors=["samplingAncilla"]):
    for amplificationStep in range(amplificationNum):
        ## Reflect on ancilla: Pauli-Z
        circuit.add_PauliZ(ancillaColors[-1])

        ## Reflect on the ground state -> Missing Hadamard gates?
        circuit = compute_and_activate(circuit, weightedFormulaDict, atomColors, ancillaColors[-1], adjoint=True)
        circuit = reflect_groundstate(circuit)
        circuit = compute_and_activate(circuit, weightedFormulaDict, atomColors, ancillaColors[-1], adjoint=False)

    return circuit