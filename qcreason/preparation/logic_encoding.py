def get_atoms_from_weightedFormulasDict(weightedFormulaDict):
    return set.union(*[extract_atoms_from_formula(weightedFormulaDict[formulaKey][:-1]) for formulaKey in weightedFormulaDict])

def get_atoms(formulaDict):
    return set.union(*[extract_atoms_from_formula(formulaDict[formulaKey]) for formulaKey in formulaDict])

def extract_atoms_from_formula(formula):
    if isinstance(formula, str):
        return {formula}
    else:
        return set.union(*[extract_atoms_from_formula(subf) for subf in formula[1:]])
