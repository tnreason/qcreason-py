from experiments.moment_matching import circuit_preparation as cp
from qcreason import preparation

import numpy as np

ANCILLA_PREFIX = "A"
ANCILLA_PREPARATIONS = [{"unitary": "X", "target": [ANCILLA_PREFIX]}, {"unitary": "H", "target": [ANCILLA_PREFIX]}]


def get_prob_f_grover_phase_estimator(probPrep, formula, precision, distributedQubits=None,
                                      ancillaQubit=ANCILLA_PREFIX):
    return ANCILLA_PREPARATIONS + preparation.get_phase_estimator(
        operator=cp.get_prep_f_grover(prepOps=probPrep, formula=formula, distributedQubits=distributedQubits,
                                      ancillaQubit=ancillaQubit),
        precision=precision,
        distributedQubits=distributedQubits)


def extract_moment(groverPhaseBits):
    """
    Corrects the missing sign in the grover (flipping the first bit), and extracts the moment
    :param groverPhaseBits: Measured phase in list of booleans
    :return:
    """
    flipped = [1 - (groverPhaseBits[0])] + [b for b in groverPhaseBits[1:]]
    return np.square(np.sin(np.pi * np.sum([b * 2 ** (-(l + 1)) for l, b in enumerate(flipped)])))


if __name__ == "__main__":
    assert extract_moment([1, 0]) == 0
    assert extract_moment([0, 0]) == 1

    for d in range(3):
        assert len(preparation.get_fourier_circuit([f"X_{i}" for i in range(d)])) == (d * (d + 1)) / 2  # + d // 2

    PHASE_PREFIX = "P_"
    precision = 2
    dOrder = 1

    distributedQubits = [f"X_{j}" for j in range(dOrder)]
    propPrep = [{"unitary": "H", "target": [distributedQubit]} for distributedQubit in distributedQubits]

    from qcreason import simulation

    ## TEST CONTRADICTION 1
    formula = ["00", "X_0"]
    grover = cp.get_prep_f_grover(prepOps=propPrep, formula=formula, distributedQubits=distributedQubits,
                                  ancillaQubit=ANCILLA_PREFIX)
    ops = get_prob_f_grover_phase_estimator(propPrep, formula=formula, precision=precision,
                                            distributedQubits=distributedQubits)
    sim = simulation.get_circuit()(ops, measured_qubits=[PHASE_PREFIX + str(j) for j in range(precision)])
    samples = sim.run(1)
    assert extract_moment(samples.iloc[0].tolist()) == 0

    ## TEST CONTRADICTION 2 (with hidden)
    formula = ["and", "X_0", ["not", "X_0"]]
    grover = cp.get_prep_f_grover(prepOps=propPrep, formula=formula, distributedQubits=distributedQubits,
                                  ancillaQubit=ANCILLA_PREFIX)
    ops = get_prob_f_grover_phase_estimator(propPrep, formula=formula, precision=precision,
                                            distributedQubits=distributedQubits)
    sim = simulation.get_circuit()(ops, measured_qubits=[PHASE_PREFIX + str(j) for j in range(precision)])
    samples = sim.run(1)
    assert extract_moment(samples.iloc[0].tolist()) == 0

    ## TEST TAUTOLOGY
    formula = ["or", "X_0", ["not", "X_0"]]
    grover = cp.get_prep_f_grover(prepOps=propPrep, formula=formula, distributedQubits=distributedQubits,
                                  ancillaQubit=ANCILLA_PREFIX)
    ops = get_prob_f_grover_phase_estimator(propPrep, formula=formula, precision=precision,
                                            distributedQubits=distributedQubits)
    sim = simulation.get_circuit()(ops, measured_qubits=[PHASE_PREFIX + str(j) for j in range(precision)])
    samples = sim.run(1)
    assert extract_moment(samples.iloc[0].tolist()) == 1
