import numpy as np

"""
Implements the mod2-basis+ calculus for logical formulas in nested list representation.
"""


def get_bpCP_connective(connectiveKey, inColors):
    """
    Generate the basis plus connective decompositions for a given connective and input colors.
    :param connectiveKey: Same connective strings as in tnreason.representation.basisPlus_calculus
    :param inColors: List of input colors
    :return: Mod2-basis+ CP decomposition by a list of slices
    """
    aliases = {
        "xor": "neq",
        "lpas": "pas0",
        "id": "pas0",
        # "not": "npas0"
    }
    if connectiveKey in aliases:
        connectiveKey = aliases[connectiveKey]

    if connectiveKey == "and":
        return [{c: 1 for c in inColors}]
    elif connectiveKey == "or":
        return [{}, {c: 0 for c in inColors}]
    elif connectiveKey == "eq":
        return [{inColor: 1 for inColor in inColors}, {inColor: 0 for inColor in inColors}]
    elif connectiveKey == "imp":
        return [{}, {**{inColor: 1 for inColor in inColors[:-1]}, inColors[-1]: 0}]
    elif connectiveKey == "not":
        return [{inColors[0]: 0}]
    elif connectiveKey.startswith("pas"):
        pos = int(connectiveKey[3:])
        assert pos < len(inColors)
        return [{inColors[pos]: 1}]
    elif connectiveKey.startswith("n"):
        return [{}] + get_bpCP_connective(connectiveKey[1:], inColors)

    ## Then understood as a Wolfram number
    try:
        int(connectiveKey)
    except:
        raise ValueError("Function {} is not a Wolfram number".format(connectiveKey))

    binDigits = bin(int(connectiveKey))[2:]  # Since have a prefix 0b for binary variables
    order = len(inColors)
    if len(binDigits) != 2 ** order:
        binDigits = "0" * (2 ** order - len(binDigits)) + binDigits  # Fill length of digits to 2 ** order

    return [{inColor: indices[i] for i, inColor in enumerate(inColors)} for indices in
            np.ndindex(*[2 for _ in range(order)]) if
            int(binDigits[2 ** order - 1 - int("".join(map(str, indices)), 2)]) == 1]


def get_connective_operations(connectiveKey, inColors, outColor):
    """
    Generate the list of operations (slices) in the mod2-basis+ CP decomposition of a connective.
    :param connectiveKey:
    :param inColors:
    :param outColor:
    :return:
    """
    basPlusCP = get_bpCP_connective(connectiveKey, inColors)
    return [{"unitary": "MCX", "target": [outColor], "control": controlDict} for controlDict
            in basPlusCP]
