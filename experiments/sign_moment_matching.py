from qcreason import representation, engine



## Do the rotations
def add_rotations(formula, repNum, oldDistPreparations):
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

def prepare_formulaList_rotations(formulaList, startCircuit):
    """
    Iterate through the formulas and prepare
    :param formulaList: List of pairs, the rotation number and the formula in nested list syntax
    :param startCircuit: Preparation of the initial q-sample / base measure (choose as default Hadamard gates on the distributed qubits)
    :return:
    """
    distPreparations = startCircuit.copy()
    for repNum, formula in formulaList:
        distPreparations = add_rotations(formula, repNum, distPreparations)
    return distPreparations

if __name__ == "__main__":

    dOrder = 3
    distributedQubits = ["X" + str(i) for i in range(dOrder)]
    ancillaQubit = "A"

    ancillaPreparation = [
        {"unitary": "MCX", "targetQubits": [ancillaQubit], "control": {}}, {"unitary": "H", "targetQubits": [ancillaQubit]}]
    startCircuit = [{"unitary": "H", "targetQubits": [color]} for color in distributedQubits]


    allDistPreparations=prepare_formulaList_rotations([(2,["and","X0","X1"]),(1,["not","X0"])], startCircuit)
    circ = engine.get_circuit()(specDict={"operations": ancillaPreparation + allDistPreparations})
    circ.visualize()


