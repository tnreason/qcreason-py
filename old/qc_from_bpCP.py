import qiskit as qk

from qcreason.representation import get_formula_string, get_bpCP


def formula_to_circuits(qc, qubitDict, formula):
    """
    Recursively convert a logical formula into a quantum circuit using mod2-basis+ CP decomposition of each connective.
    :param qc:
    :param qubitDict:
    :param formula:
    :return:
    """
    if isinstance(formula, str):
        return qc, qubitDict
    else:
        for subFormula in formula[1:]:
            qc, qubitDict = formula_to_circuits(qc, qubitDict, subFormula)

        connective = formula[0]
        inColors = [get_formula_string(subf) for subf in formula[1:]]

        import qc_from_bpCP as qcfb
        return qcfb.add_directed_block(qc, qubitDict, get_bpCP(connective, inColors), get_formula_string(formula))


## To constructor of circuit
def initialize_circuit(inColors):
    registers = [qk.QuantumRegister(1, name=c) for c in inColors]
    qc = qk.QuantumCircuit(*registers)
    qubitDict = {**{inColors[i]: qc.qubits[i] for i in range(len(inColors))}}

    for inColor in inColors:
        qc.h(qubitDict[inColor])

    return qc, qubitDict


def add_directed_block(qc, qubitDict, basPlusCP, headColor):
    if headColor not in qubitDict:
        qc.add_register(qk.QuantumRegister(1, name=headColor))
        qubitDict[headColor] = qc.qubits[-1]

    for posDict in basPlusCP:
        add_slice(qc, qubitDict, posDict, headColor)

    return qc, qubitDict


def add_slice(qc, qubitDict, posDict, headColor):
    if len(posDict) == 0:
        qc.x(qubitDict[headColor])
        return

    for inColor in posDict:
        if posDict[inColor] == 0:
            qc.x(qubitDict[inColor])

    qc.mcx([qubitDict[inColor] for inColor in posDict], qubitDict[headColor])

    for inColor in posDict:
        if posDict[inColor] == 0:
            qc.x(qubitDict[inColor])


def add_measurement(qc, qubitDict, tbMeasured):
    cr = qk.ClassicalRegister(len(tbMeasured), name="measure")
    qc.add_register(cr)
    qc.measure([qubitDict[c] for c in tbMeasured], range(len(tbMeasured)))


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    qc, qubitDict = initialize_circuit(["a", "b"])
    bpCP = [{"a": 1, "b": 0}, {"b": 1}]
    qc, qubitDict = add_directed_block(qc, qubitDict, bpCP, "c")
    add_measurement(qc, qubitDict, ["c", "a", "b"])

    qc, qubitDict = initialize_circuit(["a", "b", "c"])
    formula_to_circuits(qc, qubitDict, ["or", ["not", "b"], "c"])

    qc, qubitDict = initialize_circuit(["a", "b", "c", "d"])
    formula_to_circuits(qc, qubitDict, ["01100001", ["xor", "a", "b"], "c", "d"])

    qc.draw("mpl")
    plt.show()


