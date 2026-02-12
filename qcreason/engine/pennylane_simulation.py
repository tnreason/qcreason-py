import pennylane as qml

import matplotlib.pyplot as plt
import pandas as pd

gate_map = {"H": qml.Hadamard,
            "X": qml.PauliX,
            "Y": qml.PauliY,
            "Z": qml.PauliZ,
            "RZ": qml.RZ,
            "RY": qml.RY}


def extract_qubit_colors(operationsList):
    colors = set()
    for op in operationsList:
        colors.update(op.get("target", []))
        colors.update(op.get("control", {}).keys())
    return list(colors)


class PennyLaneSimulator:
    def __init__(self, operations, qubit_colors=None, measured_qubits=None):
        self.operations = operations
        self.qubit_colors = qubit_colors if qubit_colors is not None else extract_qubit_colors(self.operations)
        self.measured_qubits = measured_qubits if measured_qubits is not None else self.qubit_colors

    #def set_measurement(self, measured_qubits):
    #    self.measured_qubits = measured_qubits

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

                if op["unitary"].startswith("MC"):  ## Only to handle the old unitary names
                    op["unitary"] = op["unitary"][2:]

                if len(controls) == 0:

                    if not "parameters" in op or len(
                            op["parameters"]) == 0:  ## Should avoid empty parameter dictionaries
                        gate_map[op["unitary"]](wires=op["target"][0])
                    #                        qml.ctrl(gate_map[op["unitary"]], control=controls.keys())(wires=op["target"][0])
                    elif "angle" in op["parameters"]:
                        gate_map[op["unitary"]](op["parameters"]["angle"], wires=op["target"][0])
                        #qml.ctrl(lambda wires: gate_map[op["unitary"]](op["parameters"]["angle"], wires=wires),
                        #         control=controls.keys())(
                        #    wires=op["target"][0])
                    else:
                        raise ValueError(f"Unitary {op} not understood!")
                else:
                    if not "parameters" in op or len(
                            op["parameters"]) == 0:  ## Should avoid empty parameter dictionaries
                        qml.ctrl(gate_map[op["unitary"]], control=controls.keys())(wires=op["target"][0])
                    elif "angle" in op["parameters"]:
                        qml.ctrl(lambda wires: gate_map[op["unitary"]](op["parameters"]["angle"], wires=wires),
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

    def run(self, shots=1024):
        """Execute the circuit and return measurement results."""
        circuit = self._build_qnode()
        samples = circuit(shots=shots)
        return pd.DataFrame(samples, columns=self.measured_qubits)
