from experiments.moment_matching import circuit_preparation as cp
from qcreason import preparation

ANCILLA_PREFIX = "A"
ANCILLA_PREPARATIONS = [{"unitary" : "X", "target": [ANCILLA_PREFIX]}, {"unitary": "H", "target": [ANCILLA_PREFIX]}]

def get_prob_f_grover_phase_estimator(probPrep, formula, precision, distributedQubits=None, ancillaQubit=ANCILLA_PREFIX):
    return ANCILLA_PREPARATIONS + preparation.get_phase_estimator(
        operator=cp.get_prep_f_grover(prepOps=probPrep, formula=formula, distributedQubits=distributedQubits,
                                      ancillaQubit=ancillaQubit), precision=precision,
        distributedQubits=distributedQubits)


# def get_controlled_prob_f_grover(qPrepCircuit, formula, distributedQubits, ancillaQubit, controllQubit):
#    return [add_controll(gate, addControlDict={controllQubit: 1}) for gate in
#            cp.get_prep_f_grover(prepOps=qPrepCircuit, formula=formula, distributedQubits=distributedQubits,
#                                 ancillaQubit=ancillaQubit)]


if __name__ == "__main__":
    for d in range(3):
        assert len(preparation.get_fourier_circuit([f"X_{i}" for i in range(d)])) == (d * (d + 1)) / 2 #+ d // 2

    PHASE_PREFIX = "P_"
    precision = 1
    dOrder = 1

    distributedQubits = [f"X_{j}" for j in range(dOrder)]
    propPrep = [{"unitary": "H", "target": [distributedQubit]} for distributedQubit in distributedQubits]

    from qcreason import simulation

    print("CONTRADICTION")
    formula = ["and", "X_0", ["not","X_0"]]
    grover = cp.get_prep_f_grover(prepOps=propPrep, formula=formula, distributedQubits=distributedQubits, ancillaQubit=ANCILLA_PREFIX)
    for op in grover:
        print(op)
    ops = get_prob_f_grover_phase_estimator(propPrep, formula=formula, precision=precision,
                                            distributedQubits=distributedQubits)
    sim = simulation.get_circuit()(ops, measured_qubits=[PHASE_PREFIX + str(j) for j in range(precision)])
    #sim.visualize()
    samples = sim.run(100)
    print(samples.value_counts()) ## SHOULD BE 0, BUT IS 1

    print("TAUTOLOGY")
    formula = ["or", "X_0", ["not","X_0"]]
    grover = cp.get_prep_f_grover(prepOps=propPrep, formula=formula, distributedQubits=distributedQubits, ancillaQubit=ANCILLA_PREFIX)
    for op in grover:
        print(op)
    ops = get_prob_f_grover_phase_estimator(propPrep, formula=formula, precision=precision,
                                            distributedQubits=distributedQubits)
    sim = simulation.get_circuit()(ops, measured_qubits=[PHASE_PREFIX + str(j) for j in range(precision)])
    #sim.visualize()
    samples = sim.run(100)
    print(samples.value_counts()) ## SHOULD BE 1, BUT IS 0