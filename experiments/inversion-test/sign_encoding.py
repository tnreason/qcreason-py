from qcreason import representation, engine

## Preparing a sign encoding state (function in the sign of the phase, but uniform)
testFormula = ["imp", "A", "B"]
startOperations = [{"unitary" : "H", "targetQubits" : ["A"]},
                   {"unitary" : "H", "targetQubits" : ["B"]},
                   {"unitary" : "X", "targetQubits" : ["(imp_A_B)"]},
                   {"unitary" : "H", "targetQubits" : ["(imp_A_B)"]}]
operations = startOperations + representation.generate_formula_operations(testFormula)

circuit = engine.get_circuit()(specDict={"operations": operations})
#circuit.visualize()
print(circuit.run(10))

## Preparing a basis encoding state (function as constraint in support)
startOperations = [{"unitary" : "H", "targetQubits" : ["A"]},
                   {"unitary" : "H", "targetQubits" : ["B"]}]
operations = startOperations + representation.generate_formula_operations(testFormula)

circuit = engine.get_circuit()(specDict={"operations": operations})
#circuit.visualize()
print(circuit.run(10))