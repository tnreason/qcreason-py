from qcreason import engine


def get_adjoint_circuit(operationsList):
    return [get_adjoint_operation(op) for op in operationsList[::-1]]


def get_adjoint_operation(operationDict):
    """
    Prepares the adjoint of the operation, so far only accepting self-adjoint or rotations (angle gets a sign)
    :param operationDict:
    :return:
    """
    adjointOp = operationDict.copy()
    if "parameters" in adjointOp:
        if "angle" in adjointOp["parameters"]:
            adjointOp["parameters"] = {"angle": -adjointOp["parameters"]["angle"], **{key: adjointOp[key]
                                                                                      for key in adjointOp["parameters"] if
                                                                                      key != "angle"}}
    return adjointOp
    ### OLD CASE STUDY
    if operationDict["unitary"] in ["H", "X", "Z", "Y", "MCX", "MCZ", "MCY"]:  # Self-adjoint operations
        return operationDict
    elif operationDict["unitary"] in ["MCRX", "MCRY", "MCRZ", "RX", "RY",
                                      "RZ"]:  # Rotation operations: Angle negated to get the adjoint
        adjointOp = operationDict.copy()
        adjointOp["parameters"] = {"angle": -operationDict["parameters"]["angle"]}
        return adjointOp
    else:
        raise ValueError("Unknown unitary type for adjoint: {}".format(operationDict["unitary"]))


def get_groundstate_reflexion_operations(qubitColors):
    """
    Generate the list of JSON-style operations implementing
    reflection about the ground state |000...0⟩ using X → MCZ → X.
    """
    ops = [{"unitary": "MCX", "target": [color], "control": {}} for color in qubitColors]
    ops.append(
        {"unitary": "MCZ", "target": [qubitColors[-1]], "control": {color: 1 for color in qubitColors[:-1]}})
    ops += [{"unitary": "MCX", "target": [color], "control": {}} for color in qubitColors]
    return ops


def get_hadamard_gates(qubitColors):
    return [{"unitary": "H", "target": [color]} for color in qubitColors]


def amplify_ones_state(preparingOperations, amplificationColors, amplificationNum=1):
    """
    Construct amplitude amplification circuit targeting |111...1⟩.

    Args:
        preparingOperations (list[dict]): Operations preparing the initial superposition (A).
        amplificationColors (list[str]): Qubits involved in amplification.
        amplificationNum (int): Number of amplification iterations.

    Returns:
        list[dict]: JSON-style list of operations.
    """
    ops = []
    ops += preparingOperations
    for amplificationStep in range(amplificationNum):
        ops += [{"unitary": "MCZ", "target": [amplificationColors[-1]],
                 "control": {color: 1 for color in amplificationColors[:-1]}}]
        ops += get_adjoint_circuit(preparingOperations)
        ops += get_groundstate_reflexion_operations(engine.extract_qubit_colors(preparingOperations))
        ops += preparingOperations
    return ops
