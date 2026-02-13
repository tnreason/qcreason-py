

def get_atoms(formulaDict):
    return set.union(*[extract_atoms_from_formula(formulaDict[formulaKey]) for formulaKey in formulaDict])


