# Quantum Circuit Simulator

This project provides a simple simulator for quantum circuits described using the Quantum Circuit Description Language (QCDL). The simulator can execute quantum circuits and perform multiple simulations to provide probabilistic results.

## Getting Started

### Prerequisites

Ensure you have Python installed on your system. This project is compatible with Python 3.x.

### Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/Tex024/QuantumCircuitSimulator.git
cd QuantumCircuitSimulator
```

## Usage

### Running the Simulator

The ```main.py``` script allows you to run a quantum circuit simulation. It will prompt you for a QCDL file and the number of simulations to perform.

```
python main.py
```

### Example of execution:

```
Enter QCDL file name: file_name.qcdl
Enter number of simulations: 1000
Compilation successful. Simulating circuit...
[QCDL] Number of simulations: 1000
[QCDL] Qubits: 2
[QCDL] Results:
    |00> : 48.600%
    |11> : 51.400%
```

## Running Tests

The ```tester.py``` script automatically runs all tests located in the tests folder. It evaluates each test and provides a summary of the results.

```
python tester.py
```

### Example output:

```
Test 'test0.qcdl' passed.
Test 'test1.qcdl' failed.
Expected percentages:
{(0, 0): 25.0, (1, 0): 72.85, (1, 1): 2.15}
Simulation percentages:
{(0, 0): 50.92, (1, 0): 24.68, (1, 1): 24.3}
Test 'test2.qcdl' passed.

[QCDL] Test Summary:
        Total tests: 3
        Passed: 2
        Failed: 1
```

## Project Structure

```
    main.py: Main script to run quantum circuit simulations.
    tester.py: Script to run tests on QCDL files in the tests folder.
    tests/: Directory containing QCDL test files.
    src/: Directory containing all other scripts of this project.
    QCDL.md: QCDL language desciption.
```
