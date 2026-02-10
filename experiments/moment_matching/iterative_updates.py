from qcreason import engine as qcengine

from tnreason import representation as tnrepresentation
from tnreason import engine as tnengine
from tnreason.application import data_to_cores as dtc
from tnreason.application import formulas_to_cores as ftc

from experiments.moment_matching import circuit_preparation as cprep


def calculate_satisfaction(sampleDf, expression, coreType=None):
    return 1 / sampleDf.shape[0] * tnengine.contract(coreDict={**dtc.create_data_cores(sampleDf, coreType=coreType),
                                                               **ftc.create_cores_to_expressionsDict(
                                                                   {"formula": expression}),
                                                               **ftc.create_evidence_cores(
                                                                   {ftc.get_formula_headColor(expression): 1})},
                                                     openColors=[])[:]


def get_ancillaPreparationCircuit(ancillaColor="A"):
    return [{"unitary": "X", "targetQubits": [ancillaColor]}, {"unitary": "H", "targetQubits": [ancillaColor]}]


class QuantumMomentMatcher:
    def __init__(self, expressionsDict, targetSatisfactionDict, atomList=None):
        """

        :param expressionsDict:
        :param targetSatisfactionDict:
        :param atomList: List of colors to the distributed qubits
        """
        self.expressionsDict = expressionsDict
        self.targetSatisfactionDict = targetSatisfactionDict
        if atomList is not None:
            self.atomList = atomList
        else:
            self.atomList = []  # Implement: Extract atoms from expressionsDict
        self.circuitOperations = [{"unitary": "H", "targetQubits": [color]} for color in self.atomList]

    def estimate_means(self, shotNum=1000, expressionKeys=None):
        if expressionKeys is None:
            expressionKeys = list(self.expressionsDict.keys())
        testCircuit = qcengine.get_circuit()(
            specDict={"operations": get_ancillaPreparationCircuit() + self.circuitOperations})
        sampleDf = testCircuit.run(shotNum)
        return {expressionKey: calculate_satisfaction(sampleDf, self.expressionsDict[expressionKey]) for expressionKey
                in expressionKeys}

    def amplify_formula(self, formulaKey, currentMean, regFactor=1 / 20):
        rotNum = cprep.estimate_rotations(currentMean=currentMean, targetMean=self.targetSatisfactionDict[formulaKey],
                                          lossFunction=lambda x, i: regFactor * i + self.targetSatisfactionDict[
                                              formulaKey] - x)
        print(f"Rotations estimated: {rotNum}")
        self.circuitOperations = cprep.add_rotations(self.expressionsDict[formulaKey], rotNum,
                                                     oldDistPreparations=self.circuitOperations,
                                                     distributedQubits=self.atomList)

    def iterative_updates(self, maxIterations=3, precision=0.01):
        stop = False
        iterationNum = 0
        while not stop:
            iterationNum += 1
            currentMoments = self.estimate_means()
            momentDifs = {formulaKey: self.targetSatisfactionDict[formulaKey] - currentMoments[formulaKey] for
                          formulaKey in currentMoments}
            updateKey = max(momentDifs, key=momentDifs.get)
            if momentDifs[updateKey] <= precision:
                stop = True
            else:
                print(
                    f"##\nUpdate formula {updateKey} to match moment {self.targetSatisfactionDict[updateKey]} where currently {currentMoments[updateKey]}")
                self.amplify_formula(updateKey, currentMoments[updateKey])
                print(f"New Circuit length: {len(self.circuitOperations)}")
            if iterationNum >= maxIterations:
                stop = True


if __name__ == "__main__":
    atomList = ["X0", "X1", "X2"]
    expressionsDict = {"f1": ["and", "X0", ["and", "X1", "X2"]], "f2": ["imp", "X0", "X1"]}
    satisfactionDict = {"f1": 0.9, "f2": 0.8}

    mm = QuantumMomentMatcher(expressionsDict, satisfactionDict, atomList)
    mm.iterative_updates(maxIterations=10)
    #    mm.amplify_formula("f1", 0.25)

    print(mm.estimate_means())
