import math
from experiments.moment_matching import circuit_preparation as cp
from qcreason import representation as qcrep

PHASE_PREFIX = "P"


def get_fourier_circuit(transQubitList):
    """
    Prepares the Fourier Circuit as in [Nielsen, Chuang Section 5.1]
    :param transQubitList: Color of the qubits to be transformed, order is important
    :return: list of operations for the transform
    """

    ops = []
    for k, transQubit in enumerate(transQubitList):
        ops.append({"unitary": "H", "target": [transQubit]})
        for l, controlQubit in enumerate(transQubitList[k + 1:]):
            ops.append({"unitary": "RZ", "target": [transQubit], "control": {controlQubit: 1},
                        "parameters": {"angle": math.pi / 2 ** (l + 1)}})
    return ops


def add_controll(operation, addControlDict):
    extendedControlDict = operation.get("control", {})
    extendedControlDict.update(**addControlDict)
    return {**{key: operation[key] for key in operation if key != "control"}, "control": extendedControlDict}


def add_controll_to_ops(ops, addControlDict):
    return [add_controll(op, addControlDict) for op in ops]


def prepare_phase_registers(operator, precision):
    """
    Prepares the Fourier transform of the
    :param operator:
    :param precision:
    :return:
    """
    ops = [{"unitary": "H", "target": [PHASE_PREFIX + f"_{j}"]} for j in range(precision)]
    for j in range(precision):
        ops += add_controll_to_ops(operator, addControlDict={PHASE_PREFIX + f"_{j}": 1}) * (2 ** j)
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
    return initOps + prepare_phase_registers(operator, precision) + qcrep.get_adjoint_circuit(
        get_fourier_circuit([PHASE_PREFIX + f"_{j}" for j in range(precision)]))


def get_prob_f_grover_phase_estimator(probPrep, formula, precision, distributedQubits=None, ancillaQubit="A"):
    return get_phase_estimator(
        operator=cp.get_prep_f_grover(prepOps=probPrep, formula=formula, distributedQubits=distributedQubits,
                                      ancillaQubit=ancillaQubit), precision=precision,
        distributedQubits=distributedQubits)


# def get_controlled_prob_f_grover(qPrepCircuit, formula, distributedQubits, ancillaQubit, controllQubit):
#    return [add_controll(gate, addControlDict={controllQubit: 1}) for gate in
#            cp.get_prep_f_grover(prepOps=qPrepCircuit, formula=formula, distributedQubits=distributedQubits,
#                                 ancillaQubit=ancillaQubit)]


if __name__ == "__main__":
    for d in range(3):
        assert len(get_fourier_circuit([f"X_{i}" for i in range(d)])) == (d * (d + 1)) / 2

    precision = 3
    dOrder = 2

    distributedQubits = [f"X_{j}" for j in range(dOrder)]
    propPrep = [{"unitary": "H", "target": [distributedQubit]} for distributedQubit in distributedQubits]
    ops = get_prob_f_grover_phase_estimator(propPrep, formula=["and", "X_0", "X_1"], precision=precision,
                                            distributedQubits=distributedQubits)

    for op in ops:
        print(op)

    ## NEW CIRCUIT SIMULATION EXAMPLE
    from qcreason.engine import pennylane_simulation as ps

    simulation = ps.PennyLaneSimulator(ops, measured_qubits=[PHASE_PREFIX+f"_{j}" for j in range(precision)])
#    simulation.visualize()
    print(simulation.run(10))