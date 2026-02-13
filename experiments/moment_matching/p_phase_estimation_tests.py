from qcreason import simulation, preparation


def get_samples(dOrder, precision, shotNum, angle):
    testOperator = [{"unitary": "P", "target": [f"X_{j}"], "parameters": {"angle": angle}} for j in range(dOrder)]
    ops = preparation.get_phase_estimator(testOperator, precision,
                                      distributedQubits=[f"X_{j}" for j in range(dOrder)])

    simulator = simulation.get_circuit()(operations=ops, measured_qubits=[f"P_{j}" for j in range(precision)])
    return simulator.run(shotNum)

print(get_samples(1,3,100,2*0.375).value_counts())