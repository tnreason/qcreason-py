from qcreason.simulation.helpers import extract_qubit_colors

DEFAULT_CIRCUIT_TYPE = "PennyLaneSimulator"

def get_circuit(circuitType=None):
    if circuitType is None:
        circuitType = DEFAULT_CIRCUIT_TYPE
    if circuitType == "PennyLaneSimulator":
        from qcreason.simulation import pennylane_simulation as ps
        return ps.PennyLaneSimulator
    else:
        raise ValueError(f"Unknown circuit type: {circuitType}")