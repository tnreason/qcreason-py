from qcreason import representation, engine
import math


## Do the rotations
def add_rotations(formula, repNum, oldDistPreparations, distributedQubits, ancillaQubit="A"):
    """
    Addes Grover rotations to a circuit, when the ancilla is disentangled with the distributedQubits and in the antisymmetric state
    :param formula: Formula to be amplified
    :param repNum:
    :param oldDistPreparations: current state preparating circuit (without ancilla preparation, which has to)
    :param distributedQubits:
    :param ancillaQubit:
    :return:
    """
    ## Start with preparing the old distribution
    newDistPreparations = oldDistPreparations.copy()
    for repPos in range(repNum):
        ## Reflection on the models of the formula
        newDistPreparations += representation.generate_formula_operations(formula, headColor=ancillaQubit)
        ## Reflection on the previously prepared state
        newDistPreparations += oldDistPreparations[::-1]  ## Adjoint! Here assumed that we have self-adjoint gates only
        newDistPreparations += representation.get_groundstate_reflexion_operations(distributedQubits)
        newDistPreparations += oldDistPreparations
    return newDistPreparations


def prepare_formulaList_rotations(formulaList, startCircuit, distributedQubits):
    """
    Iterate through the formulas and prepare
    :param formulaList: List of pairs, the rotation number and the formula in nested list syntax
    :param startCircuit: Preparation of the initial q-sample / base measure (choose as default Hadamard gates on the distributed qubits)
    :return:
    """
    distPreparations = startCircuit.copy()
    for repNum, formula in formulaList:
        distPreparations = add_rotations(formula, repNum, distPreparations, distributedQubits)
    return distPreparations


def get_achievable_means(currentMean, maxRotations):
    """
    Computes the means which are achievable by Grover rotations. Prevents overrotation by demanding that the angle is less than pi/2.
    :param currentMean:
    :param maxRotations:
    :return:
    """
    return [(math.sin((1 + 2 * rotNum) *  math.asin(math.sqrt(currentMean)))) ** 2 for rotNum in
            range(maxRotations + 1) if (1 + 2 * rotNum) *  math.asin(math.sqrt(currentMean)) <= math.pi/2]


def estimate_rotations(currentMean, targetMean, maxRotations=10, lossFunction=None):
    """
    Computes the number of rotations such that the absolute difference to the target mean is minimized
    :param currentMean:
    :param targetMean:
    :param maxRotations:
    :return:
    """
    if lossFunction is None:
        lossFunction = lambda x, i: abs(targetMean - x)

    if targetMean <= currentMean or currentMean == 0:
        return 0
    else:
        meanDifs = [lossFunction(aMean, i) for i, aMean in enumerate(get_achievable_means(currentMean, maxRotations))]
        return meanDifs.index(min(meanDifs))


if __name__ == "__main__":
    # Check overrotation prevention
    assert len(get_achievable_means(0.98123,100))==1
    assert len(get_achievable_means(0.04,100))==4

    testMean = 0.2131
    assert abs(get_achievable_means(testMean,35)[0] - testMean)<0.000001

    assert all([mean <= 1 and mean >= 0 for mean in get_achievable_means(0.23412, 35)])
    assert estimate_rotations(0.5, 0.1231) == 0
    assert estimate_rotations(0.123, 0.123) == 0
    assert estimate_rotations(0.001, 0.54, 10) == 10

    targetM = 0.234
    regLossFunction = lambda x, i: i / 100 + abs(targetM - x)
    assert estimate_rotations(0.01231, targetMean=targetM, lossFunction=regLossFunction) == 2

    # ## Example for a circuit preparation
    # dOrder = 3
    # distributedQubits = ["X" + str(i) for i in range(dOrder)]
    # ancillaQubit = "A"
    #
    # ancillaPreparation = [
    #     {"unitary": "X", "targetQubits": [ancillaQubit]}, {"unitary": "H", "targetQubits": [ancillaQubit]}]
    # startCircuit = [{"unitary": "H", "targetQubits": [color]} for color in distributedQubits]
    #
    # allDistPreparations = prepare_formulaList_rotations([(2, ["and", "X0", "X1"]), (1, ["not", "X0"])], startCircuit, distributedQubits)
    # circ = engine.get_circuit()(specDict={"operations": ancillaPreparation + allDistPreparations})
    # # circ.visualize()
