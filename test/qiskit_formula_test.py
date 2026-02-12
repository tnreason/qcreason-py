from qcreason import simulation
from qcreason import preparation

import matplotlib.pyplot as plt

circ = simulation.get_circuit()(["a", "b", "c"])

circ = preparation.add_formula_to_circuit(circ, ["0100", ["imp", "a", "c"], ["not", "b"]])
circ.circuitOperations.draw("mpl")
plt.show()