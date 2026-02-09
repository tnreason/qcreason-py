import qcreason.representation.formulas_to_circuit
from qcreason import engine
from qcreason import representation

import matplotlib.pyplot as plt

circ = engine.get_circuit()(["a", "b", "c"])

circ = qcreason.representation.formulas_to_circuit.add_formula_to_circuit(circ, ["0100", ["imp", "a", "c"], ["not", "b"]])

import qiskit as qk
from qiskit_aer import AerSimulator
sim = AerSimulator()
tqc = qk.transpile(circ.circuit, sim)

# Run the transpiled circuit on the simulator
job = sim.run(tqc, shots=1000)
result = job.result()

# Get the counts of the results
counts = result.get_counts(tqc)
print("\nTotal counts are:", counts)