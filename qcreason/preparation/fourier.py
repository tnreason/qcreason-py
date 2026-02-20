import math
import copy

from qcreason.preparation import operations_transform as ot

PHASE_PREFIX = "P_"  # Not to confuse with the phase gate


def get_fourier_circuit(qubits):
    """
    Prepares the Fourier Circuit in bit-reversed version of [Nielsen, Chuang Section 5.1]
    :param qubits: List of qubit names/colors. Order: [MSB, ..., LSB]
    :return: List of operation dictionaries
    """
    ops = []
    for i, target_q in enumerate(qubits):
        ops.append({"unitary": "H", "target": [target_q]})

        # Subsequent qubits provide the control phases
        for l, control_q in enumerate(qubits[i + 1:]):
            angle = math.pi / (2 ** (l + 1))
            ops.append({
                "unitary": "P",
                "target": [target_q],
                "control": {control_q: 1},
                "parameters": {"angle": angle}
            })
    return ops


def prepare_phase_registers(operator, precision):
    """
    Prepares the Quantum Fourier Transform (QFT) of the phases to an operator
    :param operator: operationsList representing the operator
    :param precision: size of phase register
    :return: operationsList to prepare the phase register for inverse QFT
    """
    ops = []

    # 1. Initialize the phase register with Hadamards
    for j in range(precision):
        ops.append({"unitary": "H", "target": [f"{PHASE_PREFIX}{j}"]})

    # 2. Apply controlled-U^(2^j)
    for j in range(precision):
        control_wire = f"{PHASE_PREFIX}{j}"

        # We need to add the operator 2^j times
        num_applications = 2 ** j

        # Get the operator with the control added
        # Ensure 'add_control_to_ops' returns a NEW list of dicts
        controlled_op_unit = ot.add_control_to_ops(operator, addControlDict={control_wire: 1})

        for _ in range(num_applications):
            # Use copy.deepcopy to ensure every gate is a unique object
            ops.extend(copy.deepcopy(controlled_op_unit))

    return ops


def get_phase_estimator(operator, precision, initOps=None, distributedQubits=None):
    """
    Prepares the Quantum Phase Estimation circuit
    :param operator:
    :param precision:
    :param initOps: Preparation
    :return:
    """
    if initOps is None:
        initOps = [{"unitary": "H", "target": [disQubit]} for disQubit in distributedQubits]
    return initOps + prepare_phase_registers(operator, precision) + ot.get_adjoint_circuit(
        get_fourier_circuit([PHASE_PREFIX + str(j) for j in range(precision)]))
