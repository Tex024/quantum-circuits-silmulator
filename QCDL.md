# Quantum Circuit Description Language (QCDL)

QCDL is a simple language to define quantum circuits by creating qubits and applying gate operations. Each statement must end with a semicolon (;).

## Qubit State Definition

Declare a qubit with the def keyword. Optionally, specify its state using complex amplitudes (alpha and beta). If not provided, the qubit defaults to the state (0, 1).

Syntax:

```scss
def <qubit_name> [: <alpha_value>, <beta_value>];
```


Examples:

```scss
// q0 is initialized to (0, 1)
def q0;

// q1 is initialized with custom amplitudes (0.6, 0.8)
def q1: 0.6, 0.8;
```

## Unitary Gates

Apply unitary gate operations to qubits using a function-like syntax. Each operation ends with a semicolon.

Supported Unitary Gates:

```scss
X(<qubit>); // Pauli-X gate
Y(<qubit>); // Pauli-Y gate
Z(<qubit>); // Pauli-Z gate
H(<qubit>); // Hadamard gate
S(<qubit>); // Phase shift gate
```

## Controlled Gates

Controlled gates perform operations on a target qubit based on one or more control qubits. The target is specified first, followed by a colon and a comma-separated list of controller qubits.

Syntax:

```scss
CX(<qubitTarget>: <qubit1>, ..., <qubitN>); // Controlled Pauli-X
CY(<qubitTarget>: <qubit1>, ..., <qubitN>); // Controlled Pauli-Y
CZ(<qubitTarget>: <qubit1>, ..., <qubitN>); // Controlled Pauli-Z
```

Example:

```scss
// Applies a controlled Pauli-X on q0 with q1 and q2 as controllers
CX(q0: q1, q2);
```

## Measurement

To measure the final value of the system there is the function `measure`


## Examples

Simple Hadamard and Measurement

```scss
def q0;
H(q0);
measure;
```

Controlled-X and Measurement

```scss
def q1;
def q2: 1, 0;
H(q1);
CX(q2: q1);
measure;
```

Multiple Qubits and Gates

```scss
def q3;
def q4: 0.707, 0.707;
H(q3);
X(q4);
CZ(q3: q4);
Y(q4);
measure;
```

Multiple Controlled Gates

```scss
def q5;
def q6;
def q7;
H(q5);
H(q6);
CX(q7: q5, q6);
measure;

```
Phase Shift and Pauli-Z

```scss
def q8;
S(q8);
Z(q8);
measure;
```

Custom Initial States and Pauli-Y

```scss
def q9: 0.8, 0.6;
Y(q9);
measure;
```

More Complex Control

```scss
def q10;
def q11;
def q12;
def q13;
H(q10);
H(q11);
H(q12);
CX(q13: q10, q11, q12);
measure;
```

X,Y,Z gates together.

```scss
def q14;
X(q14);
Y(q14);
Z(q14);
measure;
```

CY gate usage

```scss
def q15;
def q16;
H(q15);
CY(q16: q15);
measure;
```

All control gates on the same target

```scss
def q17;
def q18;
def q19;
H(q17);
H(q18);
H(q19);
CX(q17: q18);
CY(q17: q19);
CZ(q17: q18,q19);
measure;
```