import math
import numpy as np

class Qubit:
    "Represents a qubit"
    name : str
    alpha : complex
    beta : complex

    def __init__(self, name: str, alpha: complex = 1.0, beta: complex = 0.0):
        if not math.isclose(alpha**2 + beta**2, 1.0, rel_tol=1e-9):
            raise ValueError("Invalid qubit state: |alpha|^2 + |beta|^2 must equal 1")
        
        self.name = name
        self.alpha = alpha
        self.beta = beta

    def get_state_vector(self) -> np.ndarray:
        """Returns the qubit state as a numpy array."""
        return np.array([self.alpha, self.beta], dtype=complex)

    def __repr__(self):
        return f"Qubit({self.name}, α={self.alpha:.3f}, β={self.beta:.3f})"


class QuantumGate:
    """Represents a quantum gate."""
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

    def __repr__(self):
        return f"QuantumGate({self.name}, matrix=\n{self.matrix})"
    
I = QuantumGate("I", np.array([[1, 0], [0, 1]], dtype=complex))
X = QuantumGate("X", np.array([[0, 1], [1, 0]], dtype=complex))
Y = QuantumGate("Y", np.array([[0, -1j], [1j, 0]], dtype=complex))
Z = QuantumGate("Z", np.array([[1, 0], [0, -1]], dtype=complex))
H = QuantumGate("H", np.array([[1/math.sqrt(2), 1/math.sqrt(2)], [1/math.sqrt(2), -1/math.sqrt(2)]], dtype=complex))
S = QuantumGate("S", np.array([[1, 0], [0, 1j]], dtype=complex))
T = QuantumGate("T", np.array([[1, 0], [0, np.exp(1j * math.pi / 4)]], dtype=complex))


# Pole, this is an example of computation using the library
if __name__ == "__main__":

    # this is how to define a qubit
    q1 = Qubit("q1")

    print(f"Initial qubit state: {q1}")

    # apply the H gate
    H.apply(q1)
    print(f"Qubit state after applying H gate: {q1}")

