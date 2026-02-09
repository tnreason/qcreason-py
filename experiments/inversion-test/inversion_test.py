from qcreason import representation, engine

## Inversion Test
firstFormula = ["or", ["not", "A"], "B"]
#secFormula = ["or", ["not", "A"], "B"]
secFormula = ["imp", "A", "B"]
hadamardOperations = [{"unitary": "H", "targetQubits": ["A"]},
                      {"unitary": "H", "targetQubits": ["B"]}]
operations = (hadamardOperations
              + representation.generate_formula_operations(firstFormula, headColor="Y")
              + representation.generate_formula_operations(secFormula, ajoint=True, headColor="Y")
              + hadamardOperations
              )

circuit = engine.get_circuit()(specDict={"operations": operations})
circuit.visualize()
print(circuit.run(10))
