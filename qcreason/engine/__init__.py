from qcreason.engine.helpers import extract_qubit_colors

defaultCircuitType = "PennyLaneCircuit"

def get_circuit(circuitType=None):
    if circuitType is None:
        circuitType = defaultCircuitType
    if circuitType == "PennyLaneSimulator":
        from qcreason.engine import pennylane_simulation as ps
        return ps.PennyLaneSimulator

    ## OLD to be adjusted
    if circuitType == "QiskitCircuit":
        from qcreason.engine import qiskit_circuits as qkc
        return qkc.QiskitCircuit
    elif circuitType == "PennyLaneCircuit":
        from qcreason.engine import pennylane_circuits as pkc
        return pkc.PennyLaneCircuit
    else:
        raise ValueError(f"Unknown circuit type: {circuitType}")
