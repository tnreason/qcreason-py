from qcreason.preparation.m2bp_formulas import get_formula_string, generate_formula_operations

from qcreason.preparation.operations_transform import get_groundstate_reflexion_operations, \
    get_adjoint_circuit, amplify_ones_state, get_hadamard_gates

from qcreason.preparation.computation_activation_circuit import get_hln_ca_operations

from qcreason.preparation.activation_circuits import tn_to_circuit, activation_core_to_circuit

from qcreason.preparation.fourier import get_fourier_circuit, get_phase_estimator

standardCircuitProvider = "PennyLaneSimulator"
standardAncillaColor = "samplingAncilla"

