import math
import numpy as np
from src.qparser import Operation

def apply_one_qubit(state: np.ndarray, operator: np.ndarray, target_index: int, num_qubits: int):
    """
    Applies a one-qubit operator directly on the state vector.
    The state is updated in-place.
    """
    N = 2 ** num_qubits
    target_mask = 1 << (num_qubits - 1 - target_index)
    indices = np.arange(N)
    mask = (indices & target_mask) == 0
    indices0 = indices[mask]
    indices1 = indices0 + target_mask

    amp0 = state[indices0].copy()
    amp1 = state[indices1].copy()
    
    state[indices0] = operator[0, 0] * amp0 + operator[0, 1] * amp1
    state[indices1] = operator[1, 0] * amp0 + operator[1, 1] * amp1

def apply_controlled_gate(state: np.ndarray, operator: np.ndarray, control_indices: list, target_index: int, num_qubits: int):
    """
    Applies a controlled one-qubit operator on the state vector.
    Only the amplitudes for which all control qubits are 1 are updated.
    """
    N = 2 ** num_qubits
    target_mask = 1 << (num_qubits - 1 - target_index)
    control_mask = 0
    for ctrl in control_indices:
        control_mask |= (1 << (num_qubits - 1 - ctrl))
        
    indices = np.arange(N)
    mask = (((indices & target_mask) == 0) & ((indices & control_mask) == control_mask))
    indices0 = indices[mask]
    indices1 = indices0 + target_mask

    amp0 = state[indices0].copy()
    amp1 = state[indices1].copy()
    
    state[indices0] = operator[0, 0] * amp0 + operator[0, 1] * amp1
    state[indices1] = operator[1, 0] * amp0 + operator[1, 1] * amp1

# Gate definitions
I_gate = np.array([[1, 0], [0, 1]], dtype=complex)
X_gate = np.array([[0, 1], [1, 0]], dtype=complex)
Y_gate = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z_gate = np.array([[1, 0], [0, -1]], dtype=complex)
H_gate = np.array([[1/math.sqrt(2), 1/math.sqrt(2)],
                   [1/math.sqrt(2), -1/math.sqrt(2)]], dtype=complex)
S_gate = np.array([[1, 0], [0, 1j]], dtype=complex)
T_gate = np.array([[1, 0], [0, np.exp(1j * math.pi / 4)]], dtype=complex)

UNITARY_MAP = {"I": I_gate, "X": X_gate, "Y": Y_gate, "Z": Z_gate,
               "H": H_gate, "S": S_gate, "T": T_gate}
CONTROLLED_MAP = {"CX": X_gate, "CY": Y_gate, "CZ": Z_gate,
                  "CH": H_gate, "CS": S_gate, "CT": T_gate}

class QuantumCircuit:
    """Represents a quantum circuit using a global state vector."""
    def __init__(self, qubit_defs: list):
        """Initializes the quantum circuit with given qubit definitions."""
        self.qubit_names = [name for name, _ in qubit_defs]
        self.num_qubits = len(qubit_defs)
        # Build the global state as the tensor product of individual qubit states.
        self.state = np.array([1], dtype=complex)
        for _, (alpha, beta) in qubit_defs:
            q_state = np.array([alpha, beta], dtype=complex)
            self.state = np.kron(self.state, q_state)

    def apply_unitary(self, gate_name: str, target: str):
        """Applies a one-qubit gate to a target qubit."""
        target_index = self.qubit_names.index(target)
        operator = UNITARY_MAP[gate_name]
        apply_one_qubit(self.state, operator, target_index, self.num_qubits)

    def apply_controlled(self, gate_name: str, target: str, controllers: list):
        """Applies a controlled gate to a target qubit."""
        target_index = self.qubit_names.index(target)
        control_indices = [self.qubit_names.index(ctrl) for ctrl in controllers]
        operator = CONTROLLED_MAP[gate_name]
        apply_controlled_gate(self.state, operator, control_indices, target_index, self.num_qubits)

    def measure(self):
        """Measures the state and returns the binary outcome as a tuple."""
        probabilities = np.abs(self.state) ** 2
        outcome_index = np.random.choice(len(self.state), p=probabilities / probabilities.sum())
        outcome = tuple(int(bit) for bit in format(outcome_index, f'0{self.num_qubits}b'))
        return outcome

    def get_state(self):
        """Returns the current global state vector."""
        return self.state

class Simulation:
    """Simulates one run of a quantum circuit."""
    def __init__(self, operations: list[Operation]):
        """Initializes the simulation with operations."""
        self.operations = operations
        qubit_defs = [(op.target, op.state) for op in operations if op.type == "define"]
        if not qubit_defs:
            raise ValueError("No qubits defined in the circuit.")
        self.circuit = QuantumCircuit(qubit_defs)

    def run(self):
        """Executes the circuit and returns the measurement outcome and final state."""
        for op in self.operations:
            if op.type == "define":
                continue
            elif op.type == "unitary":
                self.circuit.apply_unitary(op.gate, op.target)
            elif op.type == "controlled":
                self.circuit.apply_controlled(op.gate, op.target, op.controllers)
            elif op.type == "measurement":
                break
            else:
                raise ValueError(f"Unknown operation type: {op.type}")
        outcome = self.circuit.measure()
        final_state = self.circuit.get_state()
        return outcome, final_state

class Simulator:
    """Runs multiple simulations and aggregates results."""
    def __init__(self, operations: list[Operation], num_simulations: int):
        """Initializes the simulator with operations and number of simulations."""
        self.operations = operations
        self.num_simulations = num_simulations
        self.results = []
        self.aggregate_counts = {}
        self.percentages = {}
        # Retrieve the number of qubits from the first simulation.
        first_sim = Simulation(self.operations)
        self.num_qubits = first_sim.circuit.num_qubits

    def run_all(self):
        """Runs all simulations and aggregates outcomes."""
        for _ in range(self.num_simulations):
            sim = Simulation(self.operations)
            outcome, _ = sim.run()
            self.results.append(outcome)
            self.aggregate_counts[outcome] = self.aggregate_counts.get(outcome, 0) + 1
        self.percentages = {outcome: (count / self.num_simulations) * 100
                            for outcome, count in self.aggregate_counts.items()}

    def print_results(self):
        """Prints the aggregated simulation results."""
        print(f"[QCDL] Number of simulations: {self.num_simulations}")
        print(f"[QCDL] Qubits: {self.num_qubits}")
        print("[QCDL] Results:")
        sorted_results = sorted(self.percentages.items(), key=lambda item: item[0])
        for result, percentage in sorted_results:
            result_str = "|" + "".join(map(str, result)) + ">"
            print(f"    {result_str} : {percentage:.3f}%")
