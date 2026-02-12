from qcreason.representation.m2bp_connectives import get_bpCP_connective
from qcreason.representation.m2bp_formulas import get_formula_string, add_formula_to_circuit, \
    generate_formula_operations

from qcreason.representation.logic_encoding import get_atoms

from qcreason.representation.operations_transform import get_groundstate_reflexion_operations, \
    get_adjoint_circuit, amplify_ones_state, get_hadamard_gates

from qcreason.representation.computation_activation_circuit import get_hln_ca_operations

from qcreason.representation.activation_circuits import tn_to_circuit, activation_core_to_circuit

standardCircuitProvider = "PennyLaneSimulator"
standardAncillaColor = "samplingAncilla"

