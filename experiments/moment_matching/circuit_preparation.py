from qcreason import preparation, simulation
import math


## Do the rotations
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
    return oldDistPreparations + get_prep_f_grover(oldDistPreparations, formula, distributedQubits,
                                                   ancillaQubit) * repNum

def uncompute_auxiliary(operationList, headColor):
    """
    Removes the qubits shaping the head operations - those do not have to be uncomputed!
    :param operationList:
    :param headColor:
    :return:
    """
    return [operation for operation in operationList if headColor not in operation["target"]]

def get_prep_f_grover(prepOps, formula, distributedQubits, ancillaQubit):
    """
    Prepare the effective grover (when acting on anti-symmetric ancilla qubit state), by
    - decomposed computation circuit
    - uncomputation of the auxiliar statistic qubits (using filter_headOperations to drop ancilla target unitaries)
    - reflection on the prepared state (prepOps^T circ reflection on groundstate circ prepOps)
    :param prepOps: ope
    :param formula:
    :param disQubits:
    :param ancillaQubit:
    :return:
    """
    return preparation.generate_formula_operations(formula, headColor=ancillaQubit) + uncompute_auxiliary(
        preparation.generate_formula_operations(formula, adjoint=True, headColor=ancillaQubit),
        headColor=ancillaQubit) + prepOps[::-1] + preparation.get_groundstate_reflexion_operations(
        distributedQubits) + prepOps


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


if __name__ == "__main__":
    testOperations = preparation.generate_formula_operations(["or", ["and", "sledz", "jaszczur"], ["not", "slimak"]],
                                                             headColor="Ancilla")
    assert len(uncompute_auxiliary(testOperations, "Ancilla")) == len(testOperations) - 2

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

    # ## Example for a circuit preparation
    # dOrder = 3
    # distributedQubits = ["X" + str(i) for i in range(dOrder)]
    # ancillaQubit = "A"
    #
    # ancillaPreparation = [
    #     {"unitary": "X", "target": [ancillaQubit]}, {"unitary": "H", "target": [ancillaQubit]}]
    # startCircuit = [{"unitary": "H", "target": [color]} for color in distributedQubits]
    #
    # allDistPreparations = prepare_formulaList_rotations([(2, ["and", "X0", "X1"]), (1, ["not", "X0"])], startCircuit, distributedQubits)
    # circ = engine.get_circuit()(specDict={"operations": ancillaPreparation + allDistPreparations})
    # # circ.visualize()
