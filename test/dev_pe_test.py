from qcreason import preparation, simulation

import numpy as np

def phase_template(precision, shotNum, phaseList):

    preAngle = np.sum([phaseBit * 2**(-i) for i, phaseBit in enumerate(phaseList)])
    angle = preAngle * np.pi
    print(preAngle, angle)
    testOperator = [{"unitary": "P", "target": ["X_0"], "parameters" : {"angle" : angle}}]
    ops = preparation.get_phase_estimator(testOperator, precision,
                                          distributedQubits=["X_0"])
#    for op in ops:
#        print(op)

    simulator = simulation.get_circuit()(operations=ops, measured_qubits=[f"P_{j}" for j in range(precision)])
#    simulator.visualize()
    return simulator.run(shotNum)


def hadamard_template(dOrder, precision, shotNum):
    testOperator = [{"unitary": "H", "target": [f"X_{j}"]} for j in range(dOrder)]
    ops = preparation.get_phase_estimator(testOperator, precision,
                                          distributedQubits=[f"X_{j}" for j in range(dOrder)])

    simulator = simulation.get_circuit()(operations=ops, measured_qubits=[f"P_{j}" for j in range(precision)])
    return simulator.run(shotNum)

df = phase_template(3,10, [0,0,1])
print(df.value_counts().shape[0])
print(df.value_counts().index.tolist())
#print(hadamard_template(1, 3, 10))
