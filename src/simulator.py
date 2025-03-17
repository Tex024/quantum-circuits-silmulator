import math
import numpy as np
from src.qparser import *

def tensor(*matrices):
    """Compute the tensor (Kronecker) product of matrices."""
    result = matrices[0]
    for m in matrices[1:]:
        result = np.kron(result, m)
    return result

def one_qubit_operator(operator, target_index, total_qubits):
    """
    Constructs a full operator for a one-qubit gate acting on target_index.
    The total Hilbert space dimension is 2^(total_qubits).
    """
    op = None
    for i in range(total_qubits):
        # Use the gate on the target; otherwise identity.
        current = operator if i == target_index else np.eye(2, dtype=complex)
        op = current if op is None else np.kron(op, current)
    return op

def controlled_operator(control_indices, target_index, operator, total_qubits):
    """
    Constructs the full operator for a controlled gate.
    The operator is applied to the target qubit only when all control qubits are in |1⟩.
    This function builds the matrix by iterating over all basis states.
    """
    N = 2 ** total_qubits
    U = np.zeros((N, N), dtype=complex)
    for i in range(N):
        # Get binary representation (list of bits) for the basis state.
        bits = [(i >> (total_qubits - 1 - j)) & 1 for j in range(total_qubits)]
        # Check if all controls are 1.
        if all(bits[idx] == 1 for idx in control_indices):
            # The target bit is transformed by the operator.
            target_bit = bits[target_index]
            for m in [0, 1]:
                new_bits = bits.copy()
                new_bits[target_index] = m
                j = 0
                for bit in new_bits:
                    j = (j << 1) | bit
                U[j, i] += operator[m, target_bit]
        else:
            U[i, i] = 1
    return U

I_gate = np.array([[1, 0], [0, 1]], dtype=complex)
X_gate = np.array([[0, 1], [1, 0]], dtype=complex)
Y_gate = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z_gate = np.array([[1, 0], [0, -1]], dtype=complex)
H_gate = np.array([[1/math.sqrt(2), 1/math.sqrt(2)],
                   [1/math.sqrt(2), -1/math.sqrt(2)]], dtype=complex)
S_gate = np.array([[1, 0], [0, 1j]], dtype=complex)
T_gate = np.array([[1, 0], [0, np.exp(1j * math.pi / 4)]], dtype=complex)

# Mapping for unitary and controlled gates
UNITARY_MAP = {"I": I_gate, "X": X_gate, "Y": Y_gate, "Z": Z_gate,
               "H": H_gate, "S": S_gate, "T": T_gate}
CONTROLLED_MAP = {"CX": X_gate, "CY": Y_gate, "CZ": Z_gate,
                  "CH": H_gate, "CS": S_gate, "CT": T_gate}

class QuantumCircuit:
    """
    Represents a quantum circuit using a global state vector.
    The qubits are defined in order and the state is a vector in ℂ^(2^n).
    """
    def __init__(self, qubit_defs: list):
        """
        qubit_defs: list of tuples (name, (alpha, beta))
        """
        self.qubit_names = [name for name, _ in qubit_defs]
        self.num_qubits = len(qubit_defs)
        # Build initial state as tensor product of individual qubit states.
        state = np.array([1], dtype=complex)
        for name, (alpha, beta) in qubit_defs:
            q_state = np.array([alpha, beta], dtype=complex)
            state = np.kron(state, q_state)
        self.state = state  # Shape: (2^n,)
    
    def apply_unitary(self, gate_name: str, target: str):
        if target not in self.qubit_names:
            raise ValueError(f"Unknown target qubit {target}")
        target_index = self.qubit_names.index(target)
        if gate_name not in UNITARY_MAP:
            raise ValueError(f"Unknown gate {gate_name}")
        U = one_qubit_operator(UNITARY_MAP[gate_name], target_index, self.num_qubits)
        self.state = U @ self.state
    
    def apply_controlled(self, gate_name: str, target: str, controllers: list):
        if target not in self.qubit_names:
            raise ValueError(f"Unknown target qubit {target}")
        for ctrl in controllers:
            if ctrl not in self.qubit_names:
                raise ValueError(f"Unknown controller qubit {ctrl}")
        target_index = self.qubit_names.index(target)
        control_indices = [self.qubit_names.index(ctrl) for ctrl in controllers]
        if gate_name not in CONTROLLED_MAP:
            raise ValueError(f"Unknown controlled gate {gate_name}")
        U = controlled_operator(control_indices, target_index, CONTROLLED_MAP[gate_name], self.num_qubits)
        self.state = U @ self.state
    
    def measure(self):
        """
        Measures the global state.
        Returns a tuple representing the measurement outcome for each qubit.
        """
        N = 2 ** self.num_qubits
        probabilities = np.abs(self.state)**2
        outcome_index = np.random.choice(N, p=probabilities / probabilities.sum())
        outcome = tuple(int(x) for x in format(outcome_index, f'0{self.num_qubits}b'))
        return outcome

    def get_state(self):
        """Returns the current global state vector."""
        return self.state
    
class Simulation:
    """
    Simulates one run of a quantum circuit based on global state vector evolution.
    Expects a list of operations (from the QCDL parser) where:
      - 'define' operations provide qubit names and initial states.
      - 'unitary' and 'controlled' operations apply gates.
      - 'measurement' stops further evolution.
    """
    def __init__(self, operations: list[Operation]):
        self.operations = operations
        # Collect qubit definitions in the order they were defined.
        qubit_defs = []
        for op in self.operations:
            if op.type == "define":
                qubit_defs.append((op.target, op.state))
        if not qubit_defs:
            raise ValueError("No qubits defined in the circuit.")
        self.circuit = QuantumCircuit(qubit_defs)
    
    def run(self):
        for op in self.operations:
            if op.type == "define":
                continue  # Already used to initialize the circuit.
            elif op.type == "unitary":
                self.circuit.apply_unitary(op.gate, op.target)
            elif op.type == "controlled":
                self.circuit.apply_controlled(op.gate, op.target, op.controllers)
            elif op.type == "measurement":
                break  # Stop processing further operations.
            else:
                raise ValueError(f"Unknown operation type: {op.type}")
        outcome = self.circuit.measure()
        final_state = self.circuit.get_state()
        return outcome, final_state

class Simulator:
    """
    Runs multiple independent global simulations and aggregates results.
    Tracks for each simulation:
      - The final measurement outcome (as a tuple).
      - The final global state vector.
    Also aggregates measurement frequencies.
    """
    def __init__(self, operations: list[Operation], num_simulations: int):
        self.operations = operations
        self.num_simulations = num_simulations
        self.results = []  # List of tuples: (outcome, final_state)
        self.aggregate_counts = {}  # Outcome tuple -> count
        self.percentages = {} # Outcome tuple -> percentage
        self.num_qubits = 0
    
    def run_all(self):
        for _ in range(self.num_simulations):
            sim = Simulation(self.operations)
            outcome, final_state = sim.run()
            self.results.append((outcome, final_state))
            self.aggregate_counts[outcome] = self.aggregate_counts.get(outcome, 0) + 1

        self.percentages = {outcome: (count / self.num_simulations) * 100 for outcome, count in self.aggregate_counts.items()}

        for op in self.operations:
            if op.type == "define":
                self.num_qubits +=1
            if op.type == "measurement":
                break

    def print_results(self):
        print(f"[QCDL] Number of simulations: {self.num_simulations}")
        print(f"[QCDL] Qubits: {self.num_qubits}")
        print("[QCDL] Results:")

        # Sort results for better output
        sorted_results = sorted(self.percentages.items(), key=lambda item: item[0])

        for result, percentage in sorted_results:
            result_str = "|" + "".join(map(str, result)) + ">"
            print(f"       {result_str} : {percentage:.3f}%")