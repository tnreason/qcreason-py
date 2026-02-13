from qcreason import preparation

dOrder = 2
precision = 3
testOperator = [{"unitary": "H", "target": [f"X_{j}"]} for j in range(dOrder)]
ops = preparation.get_phase_estimator(testOperator, precision, distributedQubits=[f"X_{j}" for j in range(dOrder)])

from qcreason import simulation

simulator = simulation.get_circuit()(operations=ops, measured_qubits=[f"P_{j}" for j in range(precision)])
shotNum = 10000
df = simulator.run(shotNum)

#p0_distribution = df["P_0"].value_counts()
#print(df.value_counts().sort_index())

#for j in range(dOrder):
assert df[f"P_{0}"].value_counts()[0] not in [0, shotNum]
for j in range(1, precision):
    assert df[f"P_{j}"].value_counts()[0] == shotNum
#assert df["P_2"].value_counts()[0] == shotNum
# for i, row in df.iterrows():
#    assert row["P_1"]==0
#    assert row["P_2"]==0
