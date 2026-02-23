from qcreason import preparation
from qcreason import simulation

import numpy as np

ANCILLA_PREFIX = "A"
ANCILLA_PREPARATIONS = [{"unitary": "X", "target": [ANCILLA_PREFIX]}, {"unitary": "H", "target": [ANCILLA_PREFIX]}]


def uncompute_auxiliary(operationList, headColor):
    """
    Removes the qubits shaping the head operations - those do not have to be uncomputed!
    :param operationList:
    :param headColor: color of the head qubit, to be ignored when in target
    :return:
    """
    return [operation for operation in operationList if headColor not in operation["target"]]


def get_prep_f_grover(prepOps, formula, distributedQubits, ancillaQubit):
    """
    Prepare the effective grover (when acting on anti-symmetric ancilla qubit state), by
    - decomposed computation circuit
    - uncomputation of the auxiliar statistic qubits (using filter_headOperations to drop ancilla target unitaries)
    - reflection on the prepared state (prepOps^T circ reflection on groundstate circ prepOps)
    :param prepOps: operations
    :param formula:
    :param distributedQubits:
    :param ancillaQubit:
    :return:
    """
    return preparation.generate_formula_operations(formula, headColor=ancillaQubit) + uncompute_auxiliary(
        preparation.generate_formula_operations(formula, adjoint=True, headColor=ancillaQubit),
        headColor=ancillaQubit) + prepOps[::-1] + preparation.get_groundstate_reflexion_operations(
        distributedQubits) + prepOps


def extract_moment(groverPhaseBits):
    """
    Corrects the missing sign in the grover (flipping the first bit), and extracts the moment
    :param groverPhaseBits: Measured phase in list of booleans
    :return:
    """
    flipped = [float(1 - (groverPhaseBits[0]))] + [float(b) for b in groverPhaseBits[1:]]
    return np.square(np.sin(np.pi * np.sum([b * 2 ** (-(l + 1)) for l, b in enumerate(flipped)])))


class MomentEstimator:

    def __init__(self, qSamplePrep, circuitProvider=None):
        """

        :param qSamplePrep: Preparation operations for the q-sample (without ancilla preparation)
        :param circuitProvider:
        """
        self.qSamplePrep = qSamplePrep
        self.circuitProvider = circuitProvider

    def estimate_moment(self, formula, precision, distributedQubits):
        """
        Prepares the phase estimation circuit for the grover operator to propPrep and formula
        Initializes the distributed qubits in the q-sample to ensure that only the eigenvalues +-\alpha are measured
        :param formula: Formula to the moment to be estimated, in nested list syntax
        :param precision: Number of bits measured to the phase
        :param distributedQubits: List of distributed qubits (atoms in the formula)
        :return:
        """
        ops = preparation.get_phase_estimator(
            operator=get_prep_f_grover(prepOps=self.qSamplePrep, formula=formula, distributedQubits=distributedQubits,
                                       ancillaQubit=ANCILLA_PREFIX),
            precision=precision,
            initOps=ANCILLA_PREPARATIONS + self.qSamplePrep,
            distributedQubits=distributedQubits)

        sim = simulation.get_circuit(self.circuitProvider)(ops, measured_qubits=[f"P_{j}" for j in range(precision)])
        samples = sim.run(1)
        return extract_moment(samples.iloc[0].tolist())
