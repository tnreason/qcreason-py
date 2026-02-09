import qiskit as qk

from qcreason import engine

from qiskit.circuit.library import RYGate

import matplotlib.pyplot as plt

import numpy as np

## Into qiskit circuit in engine
def add_rotation_slices(sliceList, headColor):
    for angle, posDict in sliceList:
        if len(posDict) == 0:
            circ.circuit.ry(angle, circ.qubitDict[headColor])
            continue

        for inColor in posDict:
            if posDict[inColor] == 0:
                circ.circuit.x(circ.qubitDict[inColor])

        control_qubits = [circ.qubitDict[inColor] for inColor in posDict]
        target_qubit = circ.qubitDict[headColor]

        ry_gate = RYGate(angle)
        cry_gate = ry_gate.control(len(control_qubits))

        circ.circuit.append(cry_gate, control_qubits + [target_qubit])

        for inColor in posDict:
            if posDict[inColor] == 0:
                circ.circuit.x(circ.qubitDict[inColor])





if __name__ == "__main__":

    circ = engine.get_circuit()(["a", "b", "c"])

    from math import pi

    sliceList = [
        (pi / 4, {"a": 1, "b": 0}),
        (pi / 3, {"b": 0}),
        (pi / 6, {})
    ]
    add_rotation_slices(sliceList, "c")
    circ.circuit.draw("mpl")
    plt.show()
