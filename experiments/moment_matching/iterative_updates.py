import math

from qcreason import simulation
from qcreason import inference

from tnreason import engine
from tnreason.application import data_to_cores as dtc
from tnreason.application import formulas_to_cores as ftc

def calculate_satisfaction(sampleDf, expression, coreType=None):
    return 1 / sampleDf.shape[0] * engine.contract(coreDict={**dtc.create_data_cores(sampleDf, coreType=coreType),
                                                               **ftc.create_cores_to_expressionsDict(
                                                                   {"formula": expression}),
                                                               **ftc.create_evidence_cores(
                                                                   {ftc.get_formula_headColor(expression): 1})},
                                                     openColors=[])[:]


def get_ancillaPreparationCircuit(ancillaColor="A"):
    return [{"unitary": "X", "target": [ancillaColor]}, {"unitary": "H", "target": [ancillaColor]}]

def add_rotations(formula, repNum, oldDistPreparations, distributedQubits, ancillaQubit="A"):
    """
    Adds Grover rotations to a circuit, when the ancilla is disentangled with the distributedQubits and in the antisymmetric state
    :param formula: Formula to be amplified
    :param repNum: Number of repetitions of the rotation
    :param oldDistPreparations: current state preparating circuit (without ancilla preparation, which has to)
    :param distributedQubits:
    :param ancillaQubit:
    :return:
    """
    ## If the number of repetition is negative, then positive amplification of the negated formula
    if repNum < 0:
        repNum = -repNum
        formula = ["not", formula]
    return oldDistPreparations + inference.get_prep_f_grover(oldDistPreparations, formula, distributedQubits,
                                                   ancillaQubit) * repNum

def get_achievable_means(currentMean, maxRotations):
    """
    Computes the means which are achievable by Grover rotations. Prevents overrotation by demanding that the angle is less than pi/2.
    :param currentMean:
    :param maxRotations:
    :return:
    """
    return [(math.sin((1 + 2 * rotNum) * math.asin(math.sqrt(currentMean)))) ** 2 for rotNum in
            range(maxRotations + 1) if (1 + 2 * rotNum) * math.asin(math.sqrt(currentMean)) <= math.pi / 2]


def estimate_rotations(currentMean, targetMean, maxRotations=10, lossFunction=None):
    """
    Computes the number of rotations such that the absolute difference to the target mean is minimized
    :param currentMean:
    :param targetMean:
    :param maxRotations:
    :return:
    """
    if lossFunction is None:
        # Default the absolute difference, without regularization
        lossFunction = lambda x, i, tMean: abs(tMean - x)

    if currentMean == 0:
        return 0
    else:
        meanDifs = [lossFunction(aMean, i, targetMean) for i, aMean in
                    enumerate(get_achievable_means(currentMean, maxRotations))]
        negMeanDifs = [lossFunction(aMean, i, 1 - targetMean) for i, aMean in
                       enumerate(get_achievable_means(1 - currentMean, maxRotations))]
        if min(meanDifs) <= min(negMeanDifs):
            return meanDifs.index(min(meanDifs))
        else:
            return -negMeanDifs.index(min(negMeanDifs))


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
        self.circuitOperations = [{"unitary": "H", "target": [color]} for color in self.atomList]

    def estimate_means(self, shotNum=1000, formulaKeys=None):
        """
        Estimates the satisfaction rates based on samples of the circuit
        :param shotNum: Number of samples to be drawn for the estimation
        :param formulaKeys: Keys to the formulas to be estimated
        :return:
        """
        if formulaKeys is None:
            formulaKeys = list(self.expressionsDict.keys())
        testCircuit = simulation.get_circuit()(operations=get_ancillaPreparationCircuit() + self.circuitOperations)
        sampleDf = testCircuit.run(shotNum)
        return {expressionKey: calculate_satisfaction(sampleDf, self.expressionsDict[expressionKey]) for expressionKey
                in formulaKeys}

    def amplify_formula(self, formulaKey, currentMean, regFactor=1 / 20):
        """
        Adds Grover operations to the circuit operations
        :param formulaKey: Key of the formula to be amplified
        :param currentMean: (Estimation of) the current mean of the amplified formula
        :param regFactor: Regularization towards less rotations, to prevent overrotation
        :return:
        """
        rotNum = estimate_rotations(currentMean=currentMean, targetMean=self.targetSatisfactionDict[formulaKey],
                                          lossFunction=lambda x, i, tMean: regFactor * i + abs(tMean - x))
        print(f"Rotations estimated: {rotNum}")
        self.circuitOperations = add_rotations(self.expressionsDict[formulaKey], rotNum,
                                                     oldDistPreparations=self.circuitOperations,
                                                     distributedQubits=self.atomList)
        return rotNum

    def iterative_updates(self, maxIterations=3, precision=0.01):
        stop = False
        iterationNum = 0
        while not stop:
            iterationNum += 1
            currentMoments = self.estimate_means()
            momentDifs = {formulaKey: abs(self.targetSatisfactionDict[formulaKey] - currentMoments[formulaKey]) for
                          formulaKey in currentMoments}
            updateKey = max(momentDifs, key=momentDifs.get)
            if abs(momentDifs[updateKey]) <= precision:
                print(f"Precision of {precision} achieved on the moments.")
                stop = True
            else:
                print(
                    f"##\nUpdate {iterationNum} of formula {updateKey} to match moment {self.targetSatisfactionDict[updateKey]} where currently {currentMoments[updateKey]}")
                rotNum = self.amplify_formula(updateKey, currentMoments[updateKey])
                if rotNum == 0:
                    print(f"No further rotations improve the mean, aborting.")
                    stop=True
                print(f"New Circuit length: {len(self.circuitOperations)}")
            if iterationNum >= maxIterations:
                stop = True


if __name__ == "__main__":

    # Check overrotation prevention
    assert len(get_achievable_means(0.98123, 100)) == 1
    assert len(get_achievable_means(0.04, 100)) == 4

    testMean = 0.2131
    assert abs(get_achievable_means(testMean, 35)[0] - testMean) < 0.000001

    assert all([mean <= 1 and mean >= 0 for mean in get_achievable_means(0.23412, 35)])
    assert estimate_rotations(0.5, 0.1231) == 0
    assert estimate_rotations(0.123, 0.123) == 0
    assert estimate_rotations(0.001, 0.54, 10) == 10

    targetM = 0.234
    regLossFunction = lambda x, i, tM: i / 100 + abs(tM - x)
    assert estimate_rotations(0.01231, targetMean=targetM, lossFunction=regLossFunction) == 2

    atomList = ["X0", "X1", "X2"]
    expressionsDict = {"f1": ["and", "X0", ["and", "X1", "X2"]], "f2": ["imp", "X0", "X1"]}
    satisfactionDict = {"f1": 0.9, "f2": 0.8}
    #satisfactionDict = {"f1": 0.125, "f2": 0.001}

    mm = QuantumMomentMatcher(expressionsDict, satisfactionDict, atomList)
    mm.iterative_updates(maxIterations=10)
    #    mm.amplify_formula("f1", 0.25)

    print(mm.estimate_means())
