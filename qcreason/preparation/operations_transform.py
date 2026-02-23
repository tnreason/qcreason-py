import copy


def extract_qubit_colors(operationsList):
    colors = set()
    for op in operationsList:
        colors.update(op.get("target", []))
        colors.update(op.get("control", {}).keys())
    return list(colors)


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
                                                                                      for key in adjointOp["parameters"]
                                                                                      if
                                                                                      key != "angle"}}
    return adjointOp


def get_groundstate_reflexion_operations(qubitColors):
    """
    Generate the list of JSON-style operations implementing
    reflection about the ground state |000...0⟩ using X → MCZ → X.
    ! Global sign in addition to reflection, which can be ignored unless adding controls
    """
    ops = [{"unitary": "X", "target": [color], "control": {}} for color in qubitColors]
    ops.append(
        {"unitary": "Z", "target": [qubitColors[-1]], "control": {color: 1 for color in qubitColors[:-1]}})
    ops += [{"unitary": "X", "target": [color], "control": {}} for color in qubitColors]
    return ops


def add_control(operation, addControlDict):
    extendedControlDict = copy.deepcopy(operation.get("control", {}))
    extendedControlDict.update(**addControlDict)
    return {**{key: operation[key] for key in operation if key != "control"}, "control": extendedControlDict}


def add_control_to_ops(ops, addControlDict):
    return [add_control(op, addControlDict) for op in ops]


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
        ops += [{"unitary": "Z", "target": [amplificationColors[-1]],
                 "control": {color: 1 for color in amplificationColors[:-1]}}]
        ops += get_adjoint_circuit(preparingOperations)
        ops += get_groundstate_reflexion_operations(extract_qubit_colors(preparingOperations))
        ops += preparingOperations
    return ops
