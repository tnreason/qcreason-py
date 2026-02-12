from qcreason.preparation import m2bp_connectives as mc


def get_formula_string(formula):
    """
    Generate a string representation of a formula, used for qubit coloring.
    :param formula:
    :return:
    """
    if isinstance(formula, str):
        return formula
    else:
        return "(" + formula[0] + "_" + "_".join(get_formula_string(subf) for subf in formula[1:]) + ")"


def generate_formula_operations(formula, adjoint=False, headColor=None):
    """
    Generate the list of operations (connectives) in a formula in order of application.
    :param formula:
    :return:
    """
    if headColor is None:
        headColor = get_formula_string(formula)
    if isinstance(formula, str):
        return []

    elif not adjoint:
        ops = []
        for subFormula in formula[1:]:
            ops = ops + generate_formula_operations(subFormula, headColor=None)

        ops += mc.get_connective_operations(formula[0], [get_formula_string(subf) for subf in formula[1:]],
                                            headColor)
        return ops
    else:  # If adjoint, then reverse the list
        return generate_formula_operations(formula=formula, adjoint=False, headColor=headColor)[::-1]
