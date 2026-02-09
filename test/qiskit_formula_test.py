from qcreason import engine
from qcreason import representation

import matplotlib.pyplot as plt

circ = engine.get_circuit()(["a", "b", "c"])

circ = representation.add_formula_to_circuit(circ, ["0100", ["imp", "a", "c"], ["not", "b"]])
circ.circuit.draw("mpl")
plt.show()