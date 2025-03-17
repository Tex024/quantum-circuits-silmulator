#!/usr/bin/env python3
import re
import sys
from qlib import *

class QCDLSyntaxError(Exception):
    """Exception raised for syntax errors in QCDL statements."""
    pass

class Operation:
    """Represents a quantum operation."""
    def __init__(self, type, gate=None, target=None, controllers=None, state=None, line=None):
        """
        Initializes an Operation object.
        - type (str): The type of the operation (e.g., "define", "unitary", "controlled", "evaluation").
        - gate (str, optional): The gate applied (e.g., "X", "H").
        - target (str, optional): The target qubit name.
        - controllers (list, optional): List of controller qubit names.
        - state (tuple, optional): The qubit's state (alpha, beta) for definitions.
        - line (int, optional): The line number where the operation was defined.
        """
        self.type = type
        self.gate = gate
        self.target = target
        self.controllers = controllers
        self.state = state
        self.line = line

    def __str__(self):
        details = {}
        if self.gate:
            details['gate'] = self.gate
        if self.target:
            details['target'] = self.target
        if self.controllers:
            details['controllers'] = self.controllers
        if self.state:
            details['state'] = self.state
        if self.line:
            details['line'] = self.line

        return f"{self.type}: {details}"

class QCDLCompiler:
    """
    Compiles QCDL code into a list of operations.

    This class provides methods to parse and compile QCDL (Quantum Circuit Description Language) code.
    It manages qubits, parses statements, and generates a list of operations representing the quantum circuit.
    """
    def __init__(self):
        """
        Initializes a QCDLCompiler object.

        Attributes:
            qubits (dict): A dictionary to store defined qubits, keyed by their names.
            operations (list): A list to store parsed quantum operations.
            line_number (int): The current line number during compilation for error reporting.
        """
        self.qubits = {}
        self.operations = []
        self.line_number = 0

    def compile(self, content):
        """
        Compiles the given QCDL content.
        - content (str): The QCDL code to compile.
        - raises QCDLSyntaxError if a syntax error is found in the QCDL code.
        """
        statements = [stmt.strip() for stmt in content.split(";") if stmt.strip()]
        for stmt in statements:
            self.line_number += 1
            try:
                self.parse_statement(stmt)
            except QCDLSyntaxError as err:
                print(f"Compilation Error: {err}")
                sys.exit(1)

    def parse_statement(self, statement):
        """Parses a single QCDL statement."""
        if not statement:
            return

        if statement.startswith("def "):
            self.parse_definition(statement)
        elif statement == "measure":
            self.operations.append(Operation(type="measurement"))
        else:
            self.parse_gate_operation(statement)

    def parse_definition(self, statement):
        """Parses a qubit definition statement."""
        pattern = r"^def\s+([A-Za-z]\w*)(?:\s*:\s*([-+]?\d*\.?\d+)\s*,\s*([-+]?\d*\.?\d+))?$"
        match = re.fullmatch(pattern, statement)
        if not match:
            raise QCDLSyntaxError(f"Line {self.line_number}: Invalid qubit definition syntax: '{statement}'")

        qubit_name = match.group(1)
        if qubit_name in self.qubits:
            raise QCDLSyntaxError(f"Line {self.line_number}: Qubit '{qubit_name}' already defined.")

        if match.group(2) is None or match.group(6) is None:
            alpha, beta = (1.0, 0.0)
        else:
            try:
                alpha = complex(match.group(2))
                beta = complex(match.group(6))
            except ValueError:
                raise QCDLSyntaxError(f"Line {self.line_number}: Invalid complex number format.")

        self.qubits[qubit_name] = Qubit(qubit_name, alpha, beta)
        self.operations.append(Operation(type="define", target=qubit_name, state=(alpha, beta), line=self.line_number))
    def parse_gate_operation(self, statement):
        """Parses a unitary or controlled gate operation."""
        unitary_pattern = r"^(X|Y|Z|H|S)\s*\(\s*([A-Za-z]\w*)\s*\)$"
        controlled_pattern = r"^(CX|CY|CZ)\s*\(\s*([A-Za-z]\w*)\s*:\s*([A-Za-z]\w*(?:\s*,\s*[A-Za-z]\w*)*)\s*\)$"

        unitary_match = re.fullmatch(unitary_pattern, statement)
        controlled_match = re.fullmatch(controlled_pattern, statement)

        if unitary_match:
            self.parse_unitary_gate(unitary_match)
        elif controlled_match:
            self.parse_controlled_gate(controlled_match)
        else:
            raise QCDLSyntaxError(f"Line {self.line_number}: Syntax error in statement: '{statement}'")

    def parse_unitary_gate(self, match):
        """Parses a unitary gate operation."""
        gate = match.group(1)
        target = match.group(2)
        if target not in self.qubits:
            raise QCDLSyntaxError(f"Line {self.line_number}: Qubit '{target}' is not defined for gate {gate}.")
        self.operations.append(Operation(type="unitary", gate=gate, target=target, line=self.line_number))

    def parse_controlled_gate(self, match):
        """Parses a controlled gate operation."""
        gate = match.group(1)
        target = match.group(2)
        controllers_str = match.group(3)
        controllers = [q.strip() for q in controllers_str.split(",")]

        if target not in self.qubits:
            raise QCDLSyntaxError(f"Line {self.line_number}: Qubit '{target}' is not defined for gate {gate}.")
        for ctrl in controllers:
            if ctrl not in self.qubits:
                raise QCDLSyntaxError(f"Line {self.line_number}: Controller qubit '{ctrl}' is not defined for gate {gate}.")

        self.operations.append(Operation(type="controlled", gate=gate, target=target, controllers=controllers, line=self.line_number))


# Usage
def main():
    filename = input("Enter the QCDL file name: ").strip()
    try:
        with open(filename, "r") as file:
            content = file.read()
    except Exception as e:
        print(f"Error opening file '{filename}': {e}")
        sys.exit(1)

    compiler = QCDLCompiler()
    compiler.compile(content)

    print("Compilation successful.\n")
    print("Defined Qubits:")
    for qubit in compiler.qubits.values():
        print(f"  {qubit}")

    print("\nOperations:")
    for op in compiler.operations:
        print(op)

if __name__ == "__main__":
    main()
