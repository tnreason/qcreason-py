import pennylane as qml

import matplotlib.pyplot as plt
import pandas as pd

from qcreason.simulation import helpers as hp

def get_operation_from_unitaryDict(unitaryDict):
    if unitaryDict["unitary"] == "H":
        return [("H", [unitaryDict["target"]])]
    elif unitaryDict["unitary"] == "X":
        return [("X", [unitaryDict["target"]])]
    elif unitaryDict["unitary"] == "Z":
        return [("Z", [unitaryDict["target"]])]
    elif unitaryDict["unitary"] == "MCZ":
        return [("X", [controlKey]) for controlKey in unitaryDict["control"] if
                unitaryDict["control"][controlKey] == 0] + [
            ("MCZ", unitaryDict["control"].keys(), unitaryDict["target"][0])] + [("X", [controlKey]) for
                                                                                       controlKey
                                                                                       in unitaryDict["control"] if
                                                                                       unitaryDict["control"][
                                                                                           controlKey] == 0]
    elif unitaryDict["unitary"] == "MCX":
        if len(unitaryDict["control"]) == 0:
            return [("X", [unitaryDict["target"][0]])]
        return [("X", [controlKey]) for controlKey in unitaryDict["control"] if
                unitaryDict["control"][controlKey] == 0] + [
            ("MCX", unitaryDict["control"].keys(), unitaryDict["target"][0])] + [("X", [controlKey]) for
                                                                                       controlKey
                                                                                       in unitaryDict["control"] if
                                                                                       unitaryDict["control"][
                                                                                           controlKey] == 0]
    elif unitaryDict["unitary"] == "MCRY":
        return [("X", [controlKey]) for controlKey in unitaryDict["control"] if unitaryDict["control"][controlKey] == 0] + [
            ("CRot", unitaryDict["control"].keys(), unitaryDict["target"][0],
             unitaryDict["parameters"]["angle"])] + [("X", [controlKey]) for controlKey
                                                     in unitaryDict["control"] if
                                                     unitaryDict["control"][controlKey] == 0]
    else:
        raise ValueError("Unknown unitary type: {}".format(unitaryDict["unitary"]))

def read_specDict(specDict):
    operationsDict = specDict.get("operations", [])
    operations = []
    for unitaryDict in operationsDict:
        ops = get_operation_from_unitaryDict(unitaryDict)
        operations += ops
    colors = specDict.get("qubitColors", hp.extract_qubit_colors(operationsDict))
    return colors, operations


class PennyLaneCircuit:
    def __init__(self, colors=None, specDict=None):
        if specDict is not None:
            colors, operations = read_specDict(specDict)
            self.colors = list(colors)
            self.operations = operations

        else:  ## OLD, TO BE DROPPED
            """Initialize a PennyLane circuit."""
            self.colors = list(colors)

            # Store operations to apply later
            self.operations = []

        # Create a PennyLane device: Starts in the ground state 0...0
        self.dev = qml.device("default.qubit", wires=self.colors, shots=1000)
        self.qubitDict = {color: i for i, color in enumerate(self.colors)}
        # Initialize each input qubit with Hadamard
        self.tbMeasured = list(self.colors)
        self.num_qubits = len(self.colors)

    def add_hadamards(self, colors):
        for color in colors:
            self.operations.append(("H", [color]))

    def add_qubit(self, color):
        """Add a new qubit (wire) if it doesn't exist."""
        if color not in self.qubitDict:
            self.colors.append(color)
            self.qubitDict[color] = len(self.qubitDict)
            # Device cannot be changed dynamically; will rebuild on run
            # We'll recreate the device in run()

    def add_slice(self, posDict, headColor):
        """Add a multi-controlled X gate (like Qiskit mcx)."""
        ops = []

        if len(posDict) == 0:
            ops.append(("X", [headColor]))
        else:
            # Apply X to zero-controls (flip them)
            for inColor, val in posDict.items():
                if val == 0:
                    ops.append(("X", [inColor]))

            # Apply multi-controlled X (Toffoli generalization)
            control_colors = list(posDict.keys())
            target_color = headColor
            ops.append(("MCX", control_colors, target_color))

            # Undo the zero-controls
            for inColor, val in posDict.items():
                if val == 0:
                    ops.append(("X", [inColor]))

        self.operations.extend(ops)

    def add_directed_block(self, basPlusCP, headColor):
        """Add a block of multiple conditional control patterns."""
        if headColor not in self.qubitDict:
            self.add_qubit(headColor)

        for posDict in basPlusCP:
            self.add_slice(posDict, headColor)

    def add_measurement(self, tbMeasured):
        """Mark which qubits will be measured."""
        self.tbMeasured = tbMeasured

    def add_controlled_rotation(self, sliceTuple, headColor):
        """
        Add a controlled rotation gate to the circuit.
        :param sliceTuple: A tuple containing (control_colors, angle).
                           control_colors is a list of control qubits.
                           angle is the rotation angle.
        :param headColor: The target qubit for the rotation.
        """
        angle, controlDict = sliceTuple
        if angle == 0:
            return
        control_colors = list(controlDict.keys())

        # Ensure all control qubits and the target qubit exist
        for color in control_colors:
            if color not in self.qubitDict:
                self.add_qubit(color)
        if headColor not in self.qubitDict:
            self.add_qubit(headColor)

        # Add the gates realizing the controlled rotation
        for inColor, val in controlDict.items():
            if val == 0:
                self.operations.append(("X", [inColor]))
        self.operations.append(("CRot", control_colors, headColor, angle))
        for inColor, val in controlDict.items():
            if val == 0:
                self.operations.append(("X", [inColor]))

    def _build_qnode(self, shots=1000):
        """Build a QNode dynamically from the stored operations."""
        dev = qml.device("default.qubit", wires=self.colors, shots=shots)

        @qml.qnode(dev)
        def circuit():
            for op in self.operations:
                ## Can drop the MC and give the option of empty control dict
                if op[0] == "H":
                    qml.Hadamard(wires=op[1][0])
                elif op[0] == "X":
                    qml.PauliX(wires=op[1][0])
                elif op[0] == "Z":
                    qml.PauliZ(wires=op[1][0])
                elif op[0] == "MCZ":
                    controls, target = op[1], op[2]
                    qml.ctrl(qml.PauliZ, control=controls)(wires=target)
                elif op[0] == "MCX":
                    controls, target = op[1], op[2]
                    qml.ctrl(qml.PauliX, control=controls)(wires=target)
                elif op[0] == "CRot": ##
                    controls, target, angle = op[1], op[2], op[3]
                    #                qml.ctrl(qml.RZ(angle), control=controls)(wires=target)
                    qml.ctrl(lambda wires: qml.RY(angle, wires=wires), control=controls)(wires=target)
            return qml.sample(wires=self.tbMeasured)

        return circuit

    def visualize(self):
        """Draw the current circuit using PennyLane's drawer."""
        circuit = self._build_qnode()

        # ASCII version (printed to console)
        print(qml.draw(circuit)())

        # Matplotlib version (optional, prettier)
        fig, ax = qml.draw_mpl(circuit)()
        plt.show()

    def run(self, shots=1024):
        """Execute the circuit and return measurement results."""
        circuit = self._build_qnode(shots=shots)
        samples = circuit()
        return pd.DataFrame(samples, columns=self.tbMeasured)

    def add_controlled_PauliZ(self, controlDict, headColor):
        """Add a Pauli-Z gate to the specified qubit."""
        control_colors = list(controlDict.keys())

        # Ensure all control qubits and the target qubit exist
        for color in control_colors:
            if color not in self.qubitDict:
                self.add_qubit(color)
        if headColor not in self.qubitDict:
            self.add_qubit(headColor)

        # Add the gates realizing the controlled rotation
        for inColor, val in controlDict.items():
            if val == 0:
                self.operations.append(("X", [inColor]))

        self.operations.append(("MCZ", control_colors, headColor))

    def add_PauliZ(self, color):
        """Add a Pauli-Z gate to the specified qubit."""
        if color not in self.qubitDict:
            self.add_qubit(color)
        self.operations.append(("Z", [color]))


if __name__ == "__main__":
    colors = ["red", "blue", "yellow"]
    qc = PennyLaneCircuit(colors)

    # Add a controlled operation
    qc.add_directed_block(
        basPlusCP=[{"red": 1}, {"yellow": 0, "red": 0}],
        headColor="blue"
    )

    # Measure both qubits
    qc.add_measurement(["red", "blue"])

    qc.visualize()

    # Run the circuit
    results = qc.run(shots=10000)
    print(results[:10])
