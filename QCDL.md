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

# Qubit initialized with a complex state
def q0: 0.6+0.8j, 0.0;
? [0]:36; [1]:64

# Bell state-like initialization
def q1: 0.707, 0.707j;
? [0]:50; [1]:50
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

Simple Hadamard Gate

```php
def q0;
H(q0);
measure;
? [0]: 50; [1]: 50;
```

Bell state

```php
def q1;
def q2;
H(q1);
CX(q1: q2);
measure;
? [0, 0]: 50; [1, 1]: 50;
```

Custom initial state

```php
def q3: 0.707, 0.707j;
X(q3);
Y(q3);
measure;
```

Quantum teleportation circuit

```php
def q4: 1, 0;
def q5;
def q6;
H(q5);
CX(q5: q6);
CX(q4: q5);
H(q4);
measure;
? [0, 0, 0]: 25; [0, 1, 1]: 25; [1, 0, 1]: 25; [1, 1, 0]: 25;
```
Multi-Controlled Gate

```php
def q7;
def q8;
def q9;
def q10;
H(q7);
H(q8);
H(q9);
CX(q10: q7, q8, q9);
measure;
```

Phase kickback

```php
def q11;
H(q11);
S(q11);
T(q11);
measure;
```

More Controllers

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

Deutsch-Jozsa Algorithm

```php
def q12;
def q13;
H(q12);
H(q13);
CX(q12: q13);
H(q12);
measure;
```