# Quantum Circuit Description Language (QCDL)

QCDL is a streamlined language designed to define quantum circuits by creating qubits and applying gate operations. Each statement must conclude with a semicolon (`;`).

## Qubit State Definition

Declare a qubit using the `def` keyword. Optionally, specify its state using complex amplitudes (alpha and beta). If not provided, the qubit defaults to the state (0, 1).

### Syntax

```php
def <qubit_name> [: <alpha_value>, <beta_value>];
```


### Examples

```php
# q0 is initialized to (0, 1) - Default state |0>
def q0;
? [0]:100

# q1 is initialized with custom amplitudes (0.6, 0.8)
def q1: 0.6, 0.8;
? [0]:36; [1]:64
```

## Unitary Gates

Apply unitary gate operations to qubits using a function-like syntax. Each operation ends with a semicolon.

### Supported Unitary Gates:

```php
X(<qubit>); # Pauli-X gate
Y(<qubit>); # Pauli-Y gate
Z(<qubit>); # Pauli-Z gate
H(<qubit>); # Hadamard gate
S(<qubit>); # Phase shift gate
```

## Controlled Gates

Controlled gates perform operations on a target qubit based on one or more control qubits. The target is specified first, followed by a colon and a comma-separated list of controller qubits.

### Syntax

```php
CX(<qubitTarget>: <qubit1>, ..., <qubitN>); # Controlled Pauli-X
CY(<qubitTarget>: <qubit1>, ..., <qubitN>); # Controlled Pauli-Y
CZ(<qubitTarget>: <qubit1>, ..., <qubitN>); # Controlled Pauli-Z
CH(<qubitTarget>: <qubit1>, ..., <qubitN>); # Controlled Hadamard
CS(<qubitTarget>: <qubit1>, ..., <qubitN>); # Controlled Shift
```

### Example

```php
# Applies a controlled Pauli-X on q0 with q1 and q2 as controllers
CX(q0: q1, q2); # q0 is flipped if q1 and q2 are both |1>
```

## Measurement

To measure the final value of the system, use the ```measure``` function.

### Syntax

```php
measure;
```

## Commenting

To add a comment line, start the line with ```#```.

### Example

```php
# this is a comment
```

## Testing

To add a testing expected result, append a question mark ```?``` followed by the expected measurement outcomes and their probabilities

### Syntax

```php
measure;
? [<outcome1>]: <probability1>; [<outcome2>]: <probability2>; ...
```

## Examples

Simple Hadamard and Measurement

```php
def q0;
H(q0);
measure;
? [0]: 50; [1]: 50; # q0 is in superposition, equal probability of |0> and |1>
```

Controlled-X and Measurement

```php
def q1;
def q2: 1, 0;
H(q1);
CX(q2: q1);
measure;
? [0, 0]: 50; [1, 1]: 50; # q1 and q2 are entangled, equal probability of |00> and |11>
```

Multiple Qubits and Gates

```php
def q3;
def q4: 0.707, 0.707;
H(q3);
X(q4);
CZ(q3: q4);
Y(q4);
measure;
```

Multiple Controlled Gates

```php
def q5;
def q6;
def q7;
H(q5);
H(q6);
CX(q7: q5, q6);
measure;

```
Phase Shift and Pauli-Z

```php
def q8;
S(q8);
Z(q8);
measure;
```

Custom Initial States and Pauli-Y

```php
def q9: 0.8, 0.6;
Y(q9);
measure;
```

More Complex Control

```php
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

```php
def q14;
X(q14);
Y(q14);
Z(q14);
measure;
```

CY gate usage

```php
def q15;
def q16;
H(q15);
CY(q16: q15);
measure;
```

All control gates on the same target

```php
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