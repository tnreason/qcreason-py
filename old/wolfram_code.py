from qcreason import preparation, simulation

import numpy as np

connectiveKey = "7"
inColors = ["A","B"]
binDigits = bin(int(connectiveKey))[2:]  # Since have a prefix 0b for binary variables
print(binDigits)
order = len(inColors)
if len(binDigits) != 2 ** order:
    binDigits = "0" * (2 ** order - len(binDigits)) + binDigits  # Fill length of digits to 2 ** order

print(str(int("1110",2)))
firstFormula = [str(int("1110",2)), "A", "B"]
hadamardOperations = [{"unitary": "H", "target": ["A"]},
                      {"unitary": "H", "target": ["B"]}]
operations = (hadamardOperations
              + preparation.generate_formula_operations(firstFormula, headColor="Y")
              )
for operation in operations:
    print(operation)
circuit = simulation.get_circuit()(specDict={"operations": operations})
circuit.visualize()
print(circuit.run(10))
exit()