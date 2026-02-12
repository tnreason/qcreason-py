import qiskit as qk


class QiskitCircuit:

    def __init__(self, colors):
        registers = [qk.QuantumRegister(1, name=c) for c in colors]
        self.circuit = qk.QuantumCircuit(*registers)
        self.qubitDict = {**{colors[i]: self.circuit.qubits[i] for i in range(len(colors))}}

#        for inColor in colors:
#            self.circuit.h(self.qubitDict[inColor])

    def add_hadamards(self, colors):
        for color in colors:
            self.circuit.h(self.qubitDict[color])

    def add_qubit(self, color):
        if color not in self.qubitDict:
            self.circuit.add_register(qk.QuantumRegister(1, name=color))
            self.qubitDict[color] = self.circuit.qubits[-1]

    def add_slice(self, posDict, headColor):
        if len(posDict) == 0:
            self.circuit.x(self.qubitDict[headColor])
            return

        for inColor in posDict:
            if posDict[inColor] == 0:
                self.circuit.x(self.qubitDict[inColor])

        self.circuit.mcx([self.qubitDict[inColor] for inColor in posDict], self.qubitDict[headColor])

        for inColor in posDict:
            if posDict[inColor] == 0:
                self.circuit.x(self.qubitDict[inColor])

    def add_directed_block(self, basPlusCP, headColor):
        if headColor not in self.qubitDict:
            self.add_qubit(headColor)

        for posDict in basPlusCP:
            self.add_slice(posDict, headColor)

    def add_measurement(self, tbMeasured):
        cr = qk.ClassicalRegister(len(tbMeasured), name="measure")
        self.circuit.add_register(cr)
        self.circuit.measure([self.qubitDict[c] for c in tbMeasured], range(len(tbMeasured)))

    def add_controlled_rotation(self, sliceTuple, headColor):
        """
        Add a multi-controlled RY rotation.
        :param sliceTuple: specifies in a tuple (angle, controlDict), where controlDict stored in the keys the control variables and in the values on which states
        :param headColor: qubit color to the target qubit
        :return:
        """
        angle, controlDict = sliceTuple


        if headColor not in self.qubitDict:
            self.add_qubit(headColor)

        if len(controlDict) == 0:
            self.circuit.ry(angle, self.qubitDict[headColor])
            return
        elif angle == 0:
            return

        for inColor in controlDict:
            if controlDict[inColor] == 0:
                self.circuit.x(self.qubitDict[inColor])

        control_qubits = [self.qubitDict[inColor] for inColor in controlDict]
        target_qubit = self.qubitDict[headColor]

        ry_gate = qk.circuit.library.RYGate(angle)
        cry_gate = ry_gate.control(len(control_qubits))

        self.circuit.append(cry_gate, control_qubits + [target_qubit])

        for inColor in controlDict:
            if controlDict[inColor] == 0:
                self.circuit.x(self.qubitDict[inColor])

    def visualize(self):
        import matplotlib.pyplot as plt
        self.circuit.draw("mpl")
        plt.show()