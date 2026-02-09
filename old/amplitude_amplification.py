from qcreason import engine, representation
import  matplotlib.pyplot as plt

circuitProvider =  "PennyLaneCircuit"

disVariables = ["sledz", "jaszczur", "kaczka", "jaskuka", "pstrag"]
weightedFormulas = {"f1": ["imp", "sledz", "jaszczur", -3],
                    "f2": ["id", "kaczka", False],
                    "f3": ["id", "jaskuka", 10],
                    "f4": ["id", "pstrag", 0.5]}

def acceptanceRate(results):
    return sum([result[-1] for result in results])/len(results)


amplificationNumbers = range(20)
acceptanceRates = []
for amiplitNum in amplificationNumbers:
    circ = engine.get_circuit(circuitProvider)(disVariables)
    circ = representation.compute_and_activate(circ, weightedFormulas, atomColors=disVariables)
    circ = representation.amplify(circ, weightedFormulas, amiplitNum, atomColors=disVariables)
    circ.add_measurement(disVariables + ["samplingAncilla"])
    #circ.visualize()
    shotNum = 10000
    results = circ.run(shots=shotNum)
    acceptanceRates.append(acceptanceRate(results))
    print(amiplitNum, acceptanceRate(results))
#    print("With {} amplifications we have a {} acceptance rate{}".format(amiplitNum, acceptanceRate(results)))

plt.scatter(range(len(amplificationNumbers)), acceptanceRates, marker="+")
plt.ylim(0, 1)
plt.title("Amplitude Amplification on the Ancilla Qubit")
plt.xlabel("Number of Amplifications")
plt.ylabel("Acceptance Rate")
plt.show()
    #print(results)

    #for result in results: ## Check the first formula: Needs to be hard!
    #    assert not result[-1] or (result[0] and not result[1])