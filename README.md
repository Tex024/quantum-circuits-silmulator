# Quantum Circuit Simulator

This project implements a deterministic quantum circuit simulator that computes the final state vector and outcome probabilities of quantum circuits described using the **Quantum Circuit Description Language (QCDL)**. The simulator supports both standard unitary gates and controlled gates, providing exact probabilities for each computational basis.

## Overview

The simulator parses a QCDL file to extract *qubit definitions* and *quantum operations* (unitary and controlled). It then deterministically evolves the global state vector by applying the specified operations in sequence and measures the resulting amplitude probabilities.

## Getting Started

### Prerequisites

Ensure that Python 3.x is installed on your system. This project also requires the NumPy library. You can install NumPy via pip if it is not already installed:

```bash
pip install numpy
```

### Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/Tex024/QuantumCircuitSimulator.git
cd QuantumCircuitSimulator
```

## Project structure

```bash
QuantumCircuitSimulator/
├── main.py                 # Main script to run quantum circuit simulations.
├── tester.py               # Script to run tests on QCDL files in the tests folder.
├── tests/                  # Directory containing QCDL test files.
├── src/                 
│   ├── qcdl_executor.py    # File used for executing the parsing and the simulation of a qcdl file.
│   ├── tester.py           # Module for testing all files in tests folder.
│   ├── qparser.py          # Module for parsing QCDL files.
│   └── qsimulator.py       # Deterministic quantum circuit simulator implementation.
├── QCDL.md/                # Description of the QCDL language.
├── README               
└── LICENCE               
```

## Usage

### Running the Simulator

To execute a QCDL file, use the `run` command followed by your `.qcdl` filename:

```shell
python main.py run <qcdl_file>
```

### Example of execution:

```shell
> main.py run file.qcdl 

[QCDL] Compilation successful.
Simulating circuit...

Final State Vector:
--------------------
|00>: 0.5 + 0.0j
|10>: 0.854 + 0.0j
|11>: -0.146 + 0.0j
--------------------

Outcome Probabilities:
---------------------
Outcome | Probability
---------------------
|00>    |    25.0%
|01>    |     0.0%
|10>    |  72.855%
|11>    |   2.145%
---------------------
```

## Running Tests

It is also possible to run all QCDL test files in the ```tests``` directory, comparing the computed outcome probabilities against the expected values defined within each test file. The script filters out outcomes with negligible probabilities, ensuring that only significant results are compared.

```shell
python main.py test
```

### Example output:

```shell
> python main.py test

[TEST] Test 'test1.qcdl' passed.
[TEST] Test 'test2.qcdl' failed.
-------------------------------------------
(0, 0) | Expected: 25.000 | Actual: 50.000 (Diff: 25.000)
(1, 1) | Expected: 75.000 | Actual: 50.000 (Diff: 25.000)
-------------------------------------------
[TEST] Test 'test3.qcdl' passed.
[TEST] Test 'test4.qcdl' passed.

Test Summary:
--------------------
Total Tests:    4
Passed:         3
Failed:         1
--------------------
```

## How the system works

1) *Parsing QCDL*: 
    The ```qparser.py``` module parses the QCDL file to extract qubit definitions and a list of operations (including unitary and controlled gate operations).

2) *State Vector Initialization*:
    The simulator constructs the initial global state vector by taking the tensor product of each qubit’s initial state as defined in the QCDL file.

3) *Evolution and Simulation*:
    Using the deterministic simulator implemented in ```qsimulator.py```, the state vector is evolved by applying each gate operation sequentially:
    - *Unitary Gates*: A unitary gate is applied directly by updating the amplitudes corresponding to the target qubit.
    - *Controlled Gates*: A controlled gate is applied only to those indices where the control qubits are in the state ∣1⟩∣1⟩ and the target qubit is ∣0⟩∣0⟩.

4) *Probability Computation*:
    Once all operations are applied, the simulator computes the probability of each outcome by taking the square of the modulus of the amplitude, then multiplying by 100 to express it as a percentage.

5) *Testing Framework*:
    The ```tester.py``` script compares the computed probabilities with the expected values provided in each test file, reporting a summary of the tests.