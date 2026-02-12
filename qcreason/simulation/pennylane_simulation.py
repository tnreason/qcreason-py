import pennylane as qml

import matplotlib.pyplot as plt
import pandas as pd

from qcreason.simulation import helpers as hp

GATE_MAP = {"H": qml.Hadamard,
            "X": qml.PauliX,
            "Y": qml.PauliY,
            "Z": qml.PauliZ,
            "RZ": qml.RZ,
            "RY": qml.RY}
STANDARD_GATES = {qml.CNOT, qml.PauliX, qml.PauliY, qml.RZ, qml.RY, qml.RZ, qml.H}


class PennyLaneSimulator:
    def __init__(self, operations, qubit_colors=None, measured_qubits=None):
        self.operations = operations
        self.qubit_colors = qubit_colors if qubit_colors is not None else hp.extract_qubit_colors(self.operations)
        self.measured_qubits = measured_qubits if measured_qubits is not None else self.qubit_colors

    def _build_qnode(self):
        """Build a QNode dynamically from the stored operations."""
        dev = qml.device("default.qubit", wires=self.qubit_colors)

        @qml.qnode(dev)
        def circuit():
            for op in self.operations:
                controls = op.get("control", dict())
                zeroControls = [zQ for zQ in controls if op["control"][zQ] == 0]
                # Compute the control
                for zQ in zeroControls:
                    qml.PauliX(wires=zQ)

                if len(controls) == 0:
                    # Control free gates
                    if not "parameters" in op or len(
                            op["parameters"]) == 0:  ## Should avoid empty parameter dictionaries
                        GATE_MAP[op["unitary"]](wires=op["target"][0])
                    elif "angle" in op["parameters"]:
                        GATE_MAP[op["unitary"]](op["parameters"]["angle"], wires=op["target"][0])
                    else:
                        raise ValueError(f"Unitary {op} not understood!")
                else:
                    # Control free gates, need qml.ctrl
                    if not "parameters" in op or len(
                            op["parameters"]) == 0:  ## Should avoid empty parameter dictionaries
                        qml.ctrl(GATE_MAP[op["unitary"]], control=controls.keys())(wires=op["target"][0])
                    elif "angle" in op["parameters"]:
                        qml.ctrl(lambda wires: GATE_MAP[op["unitary"]](op["parameters"]["angle"], wires=wires),
                                 control=controls.keys())(
                            wires=op["target"][0])
                    else:
                        raise ValueError(f"Unitary {op} not understood!")

                # Uncompute the control
                for zQ in zeroControls:
                    qml.PauliX(wires=zQ)

            return qml.sample(wires=self.measured_qubits)

        return circuit

    def visualize(self):
        """Draw the current circuit using PennyLane's drawer."""
        circuit = self._build_qnode()

        # ASCII version (printed to console)
        print(qml.draw(circuit)())

        # Matplotlib version (optional, prettier)
        fig, ax = qml.draw_mpl(circuit)()
        plt.show()

    def get_decomposed_circuit(self, gate_set=None):
        if gate_set is None:
            gate_set = STANDARD_GATES
        circuit = self._build_qnode()
        return qml.transforms.decompose(circuit, gate_set=gate_set)

    def estimate_resources(self, transform=False, allowed_gate_set=None):
        if transform:
            if allowed_gate_set is None:
                allowed_gate_set = STANDARD_GATES
            circuit = self.get_decomposed_circuit(gate_set=allowed_gate_set)
        else:
            circuit = self._build_qnode()

        # 2. Get the specs (qml.specs returns a function)
        # Since circuit() takes no args, we call specs(circuit)()
        specs_data = qml.specs(circuit)()

        # 3. Extract the 'resources' key for the most relevant info
        return specs_data["resources"]

    def run(self, shotNum=1024, transform=False, allowed_gate_set=None):
        """
        Builds a circuit, sets the shot number, and computes shots many samples
        :param shotNum:
        :return: pd.DataFrame of the samples
        """
        if transform:
            if allowed_gate_set is None:
                allowed_gate_set = {qml.CNOT, qml.PauliX, qml.PauliY, qml.RZ, qml.RY, qml.RZ, qml.H}
            circuit = self.get_decomposed_circuit(gate_set=allowed_gate_set)
        else:
            circuit = self._build_qnode()
        samples = qml.set_shots(circuit, shots=shotNum)()
        return pd.DataFrame(samples, columns=self.measured_qubits)
