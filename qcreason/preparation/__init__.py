from qcreason.preparation.m2bp_connectives import get_bpCP_connective
from qcreason.preparation.m2bp_formulas import get_formula_string, generate_formula_operations

from qcreason.preparation.logic_encoding import get_atoms

from qcreason.preparation.operations_transform import get_groundstate_reflexion_operations, \
    get_adjoint_circuit, amplify_ones_state, get_hadamard_gates

from qcreason.preparation.computation_activation_circuit import get_hln_ca_operations

from qcreason.preparation.activation_circuits import tn_to_circuit, activation_core_to_circuit

standardCircuitProvider = "PennyLaneSimulator"
standardAncillaColor = "samplingAncilla"

