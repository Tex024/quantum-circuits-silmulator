import math
import numpy as np
import random

class EntanglementGroup:
    "Represent a group of entangled qubits"

    def __init__(self):
        self.qubits = []
    
    def add(self, qubit):
        self.qubits.append(qubit)
        qubit.group = self

class Qubit:
    "Represents a qubit"
    name : str
    alpha : complex
    beta : complex
    group : EntanglementGroup
    collapsed : int

    def __init__(self, name: str, alpha: complex = 1.0, beta: complex = 0.0):
        if not math.isclose(abs(alpha)**2 + abs(beta)**2, 1.0, rel_tol=1e-9):
            raise ValueError("Invalid qubit state: |alpha|^2 + |beta|^2 must equal 1")
        
        self.name = name
        self.alpha = alpha
        self.beta = beta
        self.group = None
        self.update_collapse()  # set initial collapsed value

    def get_state_vector(self) -> np.ndarray:
        return np.array([self.alpha, self.beta], dtype=complex)
    
    def update_collapse(self):
        """Updates the qubit’s collapsed value based on its amplitudes."""
        if random.random() < abs(self.alpha)**2:
            self.collapsed = 0
        else:
            self.collapsed = 1

    def collapse(self):
        """Alias for update_collapse."""
        self.update_collapse()

    def __repr__(self):
        return f"Qubit({self.name}, α={self.alpha:.3f}, β={self.beta:.3f}, collapsed={self.collapsed})"

class UnitaryGate:
    """Represents a unitary quantum gate."""
    name: str
    matrix: np.ndarray

    def __init__(self, name: str, matrix: np.ndarray):
        self.name = name
        self.matrix = matrix
    
    def apply(self, qubit: Qubit):
        """
        Applies the gate to the given qubit state.
        """
        state_vector = qubit.get_state_vector()
        new_state_vector = np.dot(self.matrix, state_vector)
        qubit.alpha = new_state_vector[0]
        qubit.beta = new_state_vector[1]
        qubit.collapse()

    def __repr__(self):
        return f"UnitaryGate({self.name}, matrix=\n{self.matrix})"
    
I = UnitaryGate("I", np.array([[1, 0], [0, 1]], dtype=complex))
X = UnitaryGate("X", np.array([[0, 1], [1, 0]], dtype=complex))
Y = UnitaryGate("Y", np.array([[0, -1j], [1j, 0]], dtype=complex))
Z = UnitaryGate("Z", np.array([[1, 0], [0, -1]], dtype=complex))
H = UnitaryGate("H", np.array([[1/math.sqrt(2), 1/math.sqrt(2)], [1/math.sqrt(2), -1/math.sqrt(2)]], dtype=complex))
S = UnitaryGate("S", np.array([[1, 0], [0, 1j]], dtype=complex))
T = UnitaryGate("T", np.array([[1, 0], [0, np.exp(1j * math.pi / 4)]], dtype=complex))

class ControlledGate:
    """Represents a controlled quantum gate."""
    name: str
    unitary_gate: UnitaryGate

    def __init__(self, name: str, unitary_gate: UnitaryGate):
        self.name = name
        self.unitary_gate = unitary_gate

    def apply(self, target: Qubit, controls: list[Qubit]):
        """
        Applies the gate to the given target qubit state using the controller qubit.
        """
        if all(q.collapsed == 1 for q in controls):
            self.unitary_gate.apply(target)
            target.collapse()

    def __repr__(self):
        return f"ControlledGate({self.name}, unitary_gate={self.unitary_gate.name})"

CX = ControlledGate("CX", X)
CY = ControlledGate("CY", Y)
CZ = ControlledGate("CZ", Z)
CH = ControlledGate("CH", H)
CS = ControlledGate("CS", S)
CT = ControlledGate("CT", T)
        

class QuantumCircuit:
    """Represents a quantum circuit that holds qubits keyed by their names."""
    def __init__(self, qubits: dict = None):
        if qubits is None:
            self.qubits = {}
        else:
            self.qubits = qubits

    def add_qubit(self, qubit: Qubit):
        self.qubits[qubit.name] = qubit

    def apply_gate(self, gate, qubit_name: str):
        if qubit_name not in self.qubits:
            raise ValueError(f"Qubit '{qubit_name}' not found in the circuit.")
        gate.apply(self.qubits[qubit_name])

    def apply_controlled_gate(self, gate, target: str, controllers: list[str]):
        if target not in self.qubits:
            raise ValueError(f"Target qubit '{target}' not found in the circuit.")
        for ctrl in controllers:
            if ctrl not in self.qubits:
                raise ValueError(f"Controller qubit '{ctrl}' not found in the circuit.")
        control_qubits = [self.qubits[c] for c in controllers]
        gate.apply(self.qubits[target], control_qubits)

    def measure_all(self):
        """Returns a dictionary mapping qubit names to their collapsed values."""
        # (Assumes each gate call has already updated the collapse state.)
        return {name: qubit.collapsed for name, qubit in self.qubits.items()}

    def __repr__(self):
        return f"QuantumCircuit(qubits={self.qubits})"



# Usage
if __name__ == "__main__":
    circuit = QuantumCircuit(2)

    print(f"Initial state: {circuit}")

    # Apply Hadamard gate to first qubit
    circuit.apply_gate(H, 0)
    print(f"After H gate: {circuit}")

    # Apply CNOT (CX) gate with q0 as control and q1 as target
    circuit.apply_controlled_gate(CX, 1, [0])
    print(f"After CX gate: {circuit}")

    # Measure all qubits
    result = circuit.measure_all()
    print(f"Measurement result: {result}")

