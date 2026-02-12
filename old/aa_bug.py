from qcreason import preparation, simulation, inference
import pandas as pd

circuitProvider = "PennyLaneCircuit"  # "QiskitCircuit"

disVariables = ["sledz"]
weightedFormulas = {
    "f1": ["not", "sledz", 1],
    #"f2": ["and", "jaszczur", "kaczka", False],
    #"f3": ["or", "sledz", "kaczka", -1]
}

circ = simulation.get_circuit(circuitProvider)(disVariables)
circ = preparation.compute_and_activate(circ, weightedFormulas, atomColors=disVariables)
circ = preparation.amplify(circ, weightedFormulas, 1, atomColors=disVariables)
circ.add_measurement(disVariables + ["(not_sledz)"] + ["samplingAncilla"] )
circ.visualize()

shotNum = 1000
results = circ.run(shotNum=shotNum)
results = inference.filter_results(results)
print(len(results))
df = pd.DataFrame(results,
                  columns=disVariables + ["(not_sledz)"])

empSat = inference.compute_satisfaction(df, weightedFormulas)

import math
print(math.e/(math.e+1))
print(empSat)
#assert empSat["f1"] == 1