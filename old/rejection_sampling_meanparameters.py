from qcreason import representation, engine, reasoning

import math

circuitProvider = "PennyLaneCircuit"  # "QiskitCircuit"

disVariables = ["sledz", "jaszczur", "kaczka"]
weightedFormulas = {
    "f1": ["imp", "sledz", "jaszczur", True],
    "f2": ["and", "jaszczur", "kaczka", False],
    "f3": ["or", "sledz", "kaczka", -1]
}

circ = engine.get_circuit(circuitProvider)(disVariables)
circ = representation.compute_and_activate(circ, weightedFormulas, atomColors=disVariables)
circ = representation.amplify(circ, weightedFormulas, 1, atomColors=disVariables)
circ.add_measurement(disVariables + ["(imp_sledz_jaszczur)", "(and_jaszczur_kaczka)"] + ["samplingAncilla"])
#circ.visualize()

shotNum = 1000
results = circ.run(shots=shotNum)
results = reasoning.filter_results(results)
#df = pd.DataFrame(results,
#                  columns=disVariables + ["(imp_sledz_jaszczur)", "(and_jaszczur_kaczka)"])

empSat = reasoning.compute_satisfaction(results, weightedFormulas)
print("Empirical mean parameters are: {}".format(empSat))



## Check empirical mean parameters -> Could also be read of the respective columns!
assert empSat["f1"] == 1
assert empSat["f2"] == 0
assert abs(empSat["f3"] - 1/(math.e+1)) < 0.1