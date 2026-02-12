from qcreason import preparation, simulation

## Inversion Test
firstFormula = ["or", ["not", "A"], "B"]
#secFormula = ["or", ["not", "A"], "B"]
secFormula = ["imp", "A", "B"]
hadamardOperations = [{"unitary": "H", "target": ["A"]},
                      {"unitary": "H", "target": ["B"]}]
operations = (hadamardOperations
              + preparation.generate_formula_operations(firstFormula, headColor="Y")
              + preparation.generate_formula_operations(secFormula, adjoint=True, headColor="Y")
              + hadamardOperations
              )

circuit = simulation.get_circuit()(specDict={"operations": operations})
circuit.visualize()
print(circuit.run(10))
