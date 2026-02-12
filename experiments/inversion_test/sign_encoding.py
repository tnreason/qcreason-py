from qcreason import preparation, simulation

## Preparing a sign encoding state (function in the sign of the phase, but uniform)
testFormula = ["imp", "A", "B"]
startOperations = [{"unitary" : "H", "target" : ["A"]},
                   {"unitary" : "H", "target" : ["B"]},
                   {"unitary" : "X", "target" : ["(imp_A_B)"]},
                   {"unitary" : "H", "target" : ["(imp_A_B)"]}]
operations = startOperations + preparation.generate_formula_operations(testFormula)

circuit = simulation.get_circuit()(operations=operations)
#circuit.visualize()
print(circuit.run(10))

## Preparing a basis encoding state (function as constraint in support)
startOperations = [{"unitary" : "H", "target" : ["A"]},
                   {"unitary" : "H", "target" : ["B"]}]
operations = startOperations + preparation.generate_formula_operations(testFormula)

circuit = simulation.get_circuit()(operations=operations)
#circuit.visualize()
print(circuit.run(10))