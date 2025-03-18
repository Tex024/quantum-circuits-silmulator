"""
This script implements a compiler for QCDL (Quantum Circuit Description Language).
It defines classes for representing quantum operations (`Operation`) and handling syntax errors (`QCDLSyntaxError`). 
The `QCDLCompiler` class parses QCDL code, manages qubit definitions, and generates a list of `Operation` objects representing the quantum circuit.

Author: Tex024
Date: 18/03/2024
"""

import re
import sys

#############
# EXCEPTION #
#############

class QCDLSyntaxError(Exception):
    """Exception raised for syntax errors in QCDL statements."""
    pass

##############
# OPERATIONS #
##############

class Operation:
    """Represents a quantum operation."""
    def __init__(self, type, gate=None, target=None, controllers=None, state=None, line=None):
        """Initializes an Operation object."""
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

############
# COMPILER #
############

class QCDLCompiler:
    """
    Compiles QCDL code into a list of operations.
    This class provides methods to parse and compile QCDL (Quantum Circuit Description Language) code.
    It manages qubits, parses statements, and generates a list of operations representing the quantum circuit.
    """
    def __init__(self):
        """Initializes a QCDLCompiler object."""
        self.qubits = []
        self.operations = []
        self.line_number = 0
        self.expected_result = None

    def compile(self, content):
        """
        Compiles the given QCDL content.
        Raises QCDLSyntaxError if a syntax error is found.
        """
        clean_lines = []
        for line in content.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                # Ignore comment lines.
                continue
            elif stripped.startswith("?"):
                # Extract expected result from the first occurrence and parse it into a dictionary.
                if self.expected_result is not None:
                    raise QCDLSyntaxError(f"Multiple expected result lines found at statement {self.line_number + 1}.")
                self.expected_result = self.parse_expected_result(stripped[1:].strip())
            else:
                clean_lines.append(line)
        # Join the non-comment, non-expected-result lines.
        processed_content = "\n".join(clean_lines)
        # Split the content into statements using ';' as delimiter.
        statements = [stmt.strip() for stmt in processed_content.split(";") if stmt.strip()]
        for stmt in statements:
            self.line_number += 1
            try:
                self.parse_statement(stmt)
            except QCDLSyntaxError as err:
                print(f"\033[91m[QCDL] Compilation Error: {err}\033[0m")
                sys.exit(1)
                
    def parse_expected_result(self, expected_str):
        """Parses the expected result string into a dictionary."""
        expected_dict = {}
        parts = [part.strip() for part in expected_str.split(";") if part.strip()]
        for part in parts:
            match = re.fullmatch(r"\[([01](?:\s*,\s*[01])*)\]\s*:\s*([\d\.]+)", part)
            if not match:
                raise QCDLSyntaxError(f"Invalid expected result format: '{part}'")
            state_str = match.group(1)
            percentage = float(match.group(2))
            state_tuple = tuple(int(bit.strip()) for bit in state_str.split(","))
            expected_dict[state_tuple] = percentage
        return expected_dict

    def parse_statement(self, statement):
        """Parses a single QCDL statement."""
        if not statement:
            return
        if statement.startswith("def "):
            self.parse_definition(statement)
        elif statement == "measure":
            self.operations.append(Operation(type="measurement", line=self.line_number))
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
        if match.group(2) is None or match.group(3) is None:
            alpha, beta = (1.0, 0.0)
        else:
            try:
                alpha = complex(match.group(2))
                beta = complex(match.group(3))
            except ValueError:
                raise QCDLSyntaxError(f"Line {self.line_number}: Invalid complex number format.")
        self.qubits.append(qubit_name)
        self.operations.append(Operation(type="define", target=qubit_name, state=(alpha, beta), line=self.line_number))

    def parse_gate_operation(self, statement):
        """Parses a unitary or controlled gate operation."""
        unitary_pattern = r"^(X|Y|Z|H|S)\s*\(\s*([A-Za-z]\w*)\s*\)$"
        controlled_pattern = r"^(CX|CY|CZ|CH|CS|CT)\s*\(\s*([A-Za-z]\w*)\s*:\s*([A-Za-z]\w*(?:\s*,\s*[A-Za-z]\w*)*)\s*\)$"

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