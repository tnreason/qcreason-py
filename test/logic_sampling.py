
from qcreason import simulation
from qcreason import preparation

circ = simulation.get_circuit("PennyLaneCircuit")(["a", "b", "c"])
circ.add_hadamards(["a", "b", "c"])
circ = preparation.add_formula_to_circuit(circ, ["0100", ["imp", "a", "c"], ["not", "b"]])
circ.add_measurement(["b","(not_b)"])
#circ.visualize()

# Run the circuit
shotNum = 100
results = circ.run(shots=shotNum).values

for i in range(shotNum):
    ## Check whether the b not_b logic is satisfied at each sample
    assert (results[i][0] == 1 and results[i][1] == 0) or (results[i][0] == 0 and results[i][1] == 1)