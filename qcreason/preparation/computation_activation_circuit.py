from qcreason.preparation import m2bp_formulas as mf
from qcreason.preparation import activation_circuits as ac
from qcreason.preparation import operations_transform as ot

def extract_atoms_from_formula(formula):
    if isinstance(formula, str):
        return {formula}
    else:
        return set.union(*[extract_atoms_from_formula(subf) for subf in formula[1:]])

def get_atoms_from_weightedFormulasDict(weightedFormulaDict):
    return set.union(*[extract_atoms_from_formula(weightedFormulaDict[formulaKey][:-1]) for formulaKey in weightedFormulaDict])

def get_hln_ca_operations(weightedFormulaDict, ancillaPrefix="ancilla_"):
    """
    Gets the circuit preparing the ancilla augmentation of a Hybrid Logic Network
    :param weightedFormulaDict:
    :param ancillaPrefix:
    :return:
    """
    ops = ot.get_hadamard_gates(get_atoms_from_weightedFormulasDict(weightedFormulaDict))
    for formulaKey in weightedFormulaDict:
        ops += mf.generate_formula_operations(weightedFormulaDict[formulaKey][:-1])
        ops += ac.single_canParam_to_activation_circuit(canParam=weightedFormulaDict[formulaKey][-1],
                                              statisticColor=mf.get_formula_string(
                                                  weightedFormulaDict[formulaKey][:-1]),
                                              ancillaColor=ancillaPrefix + mf.get_formula_string(
                                                  weightedFormulaDict[formulaKey][:-1]))
    return ops


