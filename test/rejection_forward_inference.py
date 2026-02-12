from qcreason import preparation, simulation, inference

import math

circuitProvider = "PennyLaneCircuit"

disVariables = ["sledz", "jaszczur", "kaczka"]
weightedFormulas = {
    "f1": ["imp", "sledz", "jaszczur", True],
    "f2": ["and", "jaszczur", "kaczka", False],
    "f3": ["or", "sledz", "kaczka", -1]
}

inferer = inference.HLNForwardCircuitSampler(
    formulaDict={formulaKey: weightedFormulas[formulaKey][:-1] for formulaKey in weightedFormulas},
    canParamDict={formulaKey: weightedFormulas[formulaKey][-1] for formulaKey in weightedFormulas},
    circuitProvider=circuitProvider, amplificationNum=2, shotNum=1000)
empSat = inferer.old_infer_meanParam(["f1", "f2", "f3"])
print(empSat)
assert empSat["f1"] == 1
assert empSat["f2"] == 0
assert abs(empSat["f3"] - 1 / (math.e + 1)) < 0.1