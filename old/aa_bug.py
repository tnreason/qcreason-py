from qcreason import representation, engine, reasoning
import pandas as pd

circuitProvider = "PennyLaneCircuit"  # "QiskitCircuit"

disVariables = ["sledz"]
weightedFormulas = {
    "f1": ["not", "sledz", 1],
    #"f2": ["and", "jaszczur", "kaczka", False],
    #"f3": ["or", "sledz", "kaczka", -1]
}

circ = engine.get_circuit(circuitProvider)(disVariables)
circ = representation.compute_and_activate(circ, weightedFormulas, atomColors=disVariables)
circ = representation.amplify(circ, weightedFormulas, 1, atomColors=disVariables)
circ.add_measurement(disVariables + ["(not_sledz)"] + ["samplingAncilla"] )
circ.visualize()

shotNum = 1000
results = circ.run(shots=shotNum)
results = reasoning.filter_results(results)
print(len(results))
df = pd.DataFrame(results,
                  columns=disVariables + ["(not_sledz)"])

empSat = reasoning.compute_satisfaction(df, weightedFormulas)

import math
print(math.e/(math.e+1))
print(empSat)
#assert empSat["f1"] == 1