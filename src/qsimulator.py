"""
This module implements a deterministic quantum circuit simulator that computes the final
state vector and outcome probabilities of a quantum circuit described using QCDL.
It supports both unitary and controlled gate operations applied directly on the state vector.

Author: Tex024
Date: 18/03/2024
"""

import math
import numpy as np
from src.qparser import Operation

#################
# QUANTUM GATES #
#################
"""
This section provides predefined quantum gate matrices and mappings for unitary and controlled quantum gates.

- I_GATE: Identity gate matrix.
- X_GATE: Pauli-X gate matrix.
- Y_GATE: Pauli-Y gate matrix.
- Z_GATE: Pauli-Z gate matrix.
- H_GATE: Hadamard gate matrix.
- S_GATE: Phase gate matrix.
- T_GATE: T gate matrix.

UNITARY_MAP: Mapping from unitary gate names to their matrices.
CONTROLLED_MAP: Mapping from controlled gate names to their matrices.
"""
    
I_GATE: np.ndarray = np.array([[1, 0], [0, 1]], dtype=complex)
X_GATE: np.ndarray = np.array([[0, 1], [1, 0]], dtype=complex)
Y_GATE: np.ndarray = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z_GATE: np.ndarray = np.array([[1, 0], [0, -1]], dtype=complex)
H_GATE: np.ndarray = np.array([[1 / math.sqrt(2), 1 / math.sqrt(2)],
                                [1 / math.sqrt(2), -1 / math.sqrt(2)]], dtype=complex)
S_GATE: np.ndarray = np.array([[1, 0], [0, 1j]], dtype=complex)
T_GATE: np.ndarray = np.array([[1, 0], [0, np.exp(1j * math.pi / 4)]], dtype=complex)

UNITARY_MAP: dict = {
    "I": I_GATE,
    "X": X_GATE,
    "Y": Y_GATE,
    "Z": Z_GATE,
    "H": H_GATE,
    "S": S_GATE,
    "T": T_GATE,
}

CONTROLLED_MAP: dict = {
    "CX": X_GATE,
    "CY": Y_GATE,
    "CZ": Z_GATE,
    "CH": H_GATE,
    "CS": S_GATE,
    "CT": T_GATE,
}


######################
# QUANTUM OPERATIONS #
######################

def apply_unitary_gate(state: np.ndarray, operator: np.ndarray, target_index: int, num_qubits: int) -> None:
    """Applies a one-qubit unitary gate to the given state vector."""
    total_states = 2 ** num_qubits
    target_mask = 1 << (num_qubits - 1 - target_index)
    indices = np.arange(total_states)
    mask = (indices & target_mask) == 0
    indices_zero = indices[mask]
    indices_one = indices_zero + target_mask

    amplitude_zero = state[indices_zero].copy()
    amplitude_one = state[indices_one].copy()

    state[indices_zero] = operator[0, 0] * amplitude_zero + operator[0, 1] * amplitude_one
    state[indices_one] = operator[1, 0] * amplitude_zero + operator[1, 1] * amplitude_one

def apply_controlled_gate(state: np.ndarray, operator: np.ndarray, control_indices: list, target_index: int, num_qubits: int) -> None:
    """Applies a controlled gate to the given state vector. The gate is applied only when all control qubits are in state |1> and the target qubit is in state |0>."""
    total_states = 2 ** num_qubits
    target_mask = 1 << (num_qubits - 1 - target_index)
    control_mask = 0
    for control_index in control_indices:
        control_mask |= (1 << (num_qubits - 1 - control_index))
    
    indices = np.arange(total_states)
    # Update amplitudes where the target is 0 and all control bits are 1.
    valid_mask = ((indices & target_mask) == 0) & ((indices & control_mask) == control_mask)
    indices_zero = indices[valid_mask]
    indices_one = indices_zero + target_mask

    amplitude_zero = state[indices_zero].copy()
    amplitude_one = state[indices_one].copy()

    state[indices_zero] = operator[0, 0] * amplitude_zero + operator[0, 1] * amplitude_one
    state[indices_one] = operator[1, 0] * amplitude_zero + operator[1, 1] * amplitude_one

#############
# SIMULATOR #
#############

class Simulator:
    """Simulator for computing the final state vector of a quantum circuit."""
    operations: list[Operation]
    qubit_definitions: list[tuple]
    num_qubits: int
    state: np.ndarray

    def __init__(self, operations: list[Operation]):
        """Initializes the Simulator with a list of operations."""
        self.operations = operations
        self.qubit_definitions = []
        for op in operations:
            if op.type == "define":
                self.qubit_definitions.append((op.target, op.state))
        if not self.qubit_definitions:
            raise ValueError("No qubits defined in the circuit.")
        self.num_qubits = len(self.qubit_definitions)
        self.state = self.build_initial_state()

    def build_initial_state(self) -> np.ndarray:
        """Constructs the initial global state vector as the tensor product of individual qubit states."""
        state = np.array([1], dtype=complex)
        for _, (alpha, beta) in self.qubit_definitions:
            qubit_state = np.array([alpha, beta], dtype=complex)
            state = np.kron(state, qubit_state)
        return state

    def get_qubit_index(self, qubit_name: str) -> int:
        """Retrieves the index of a qubit by its name."""
        for index, (name, _) in enumerate(self.qubit_definitions):
            if name == qubit_name:
                return index
        raise ValueError(f"Qubit {qubit_name} not found.")

    def run(self) -> np.ndarray:
        """Evolves the state vector by sequentially applying all quantum operations."""
        for op in self.operations:
            if op.type == "define":
                continue
            elif op.type == "unitary":
                if op.gate not in UNITARY_MAP:
                    raise ValueError(f"Unknown unitary gate: {op.gate}")
                operator = UNITARY_MAP[op.gate]
                target_index = self.get_qubit_index(op.target)
                apply_unitary_gate(self.state, operator, target_index, self.num_qubits)
            elif op.type == "controlled":
                if op.gate not in CONTROLLED_MAP:
                    raise ValueError(f"Unknown controlled gate: {op.gate}")
                operator = CONTROLLED_MAP[op.gate]
                target_index = self.get_qubit_index(op.target)
                control_indices = [self.get_qubit_index(ctrl) for ctrl in op.controllers]
                apply_controlled_gate(self.state, operator, control_indices, target_index, self.num_qubits)
            elif op.type == "measurement":
                # Measurement halts further operations.
                break
            else:
                raise ValueError(f"Unknown operation type: {op.type}")
        return self.state

    def print_result(self) -> None:
        """Prints the outcome probabilities for each computational basis state in a formatted table, removing trailing zeros."""
        print("\n\033[94mOutcome Probabilities:\033[0m")

        probabilities = np.abs(self.state) ** 2
        total_states = 2 ** self.num_qubits

        # Calculate maximum outcome string length and maximum probability string length.
        max_outcome_len = self.num_qubits + 2  # |001> -> length 5
        max_prob_len = max(len(f"{p * 100:.3f}%") for p in probabilities)

        # Calculate total table width.
        total_width = max_outcome_len + max_prob_len + 10

        print("-" * total_width)

        # Print headers.
        outcome_header = "\033[93mOutcome\033[0m"
        prob_header = "\033[93mProbability\033[0m"

        print(f"{outcome_header:<{max_outcome_len}} | {prob_header:>{max_prob_len}}")

        print("-" * total_width)

        # Print outcome probabilities.
        for index in range(total_states):
            outcome = format(index, f'0{self.num_qubits}b')
            probability_percentage = probabilities[index] * 100
            prob_str = f"{probability_percentage:.3f}".rstrip('0')
            if prob_str.endswith('.'):
                prob_str += '0'
            print(f"|{outcome}>\t| {prob_str:>{max_prob_len}}%")

        print("-" * total_width)


    def print_final_state(self) -> None:
        """Prints the final state vector in a formatted way, removing trailing zeros from complex numbers."""
        print("\n\033[94mFinal State Vector:\033[0m")
        print("-" * 20)
        for i, amplitude in enumerate(self.state):
            if abs(amplitude) > 1e-10:  # Avoid printing negligible amplitudes
                outcome = format(i, f'0{self.num_qubits}b')
                real_str = f"{amplitude.real:.3f}".rstrip('0')
                imag_str = f"{amplitude.imag:.3f}".rstrip('0')

                if real_str.endswith('.'):
                    real_str += '0'
                if imag_str.endswith('.'):
                    imag_str += '0'

                if imag_str == '0':
                    print(f"|{outcome}>: {real_str or '0'}")
                else:
                    sign = "+" if amplitude.imag >= 0 else "-"
                    imag_abs_str = imag_str.lstrip('-')
                    if real_str == '0':
                        print(f"|{outcome}>: {sign}{imag_abs_str or '0'}j")
                    else:
                        print(f"|{outcome}>: {real_str or '0'} {sign} {imag_abs_str or '0'}j")
        print("-" * 20)


