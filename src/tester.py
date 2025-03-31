"""
This module provides a testing framework for quantum circuits described in QCDL.
The `Tester` class automates the execution of tests located in a specified directory. 
It reads QCDL files, compiles them into quantum operations using the `QCDLCompiler`, and simulates the circuits using the `Simulator`. 
The simulation results, represented as probabilities of measurement outcomes, are then compared against expected results defined within the test files.

Author: Tex024
Date: 18/03/2024
"""

import os
import numpy as np
from src.qsimulator import Simulator
from src.qparser import QCDLCompiler

##########
# TESTER #
##########

class Tester:
    def __init__(self, tests_directory="tests"):
        """Initialize the tester."""
        self.tests_directory = tests_directory
        self.tolerance = 0.05

    def run_test(self, test_filename):
        """Run a single test."""
        test_path = os.path.join(self.tests_directory, test_filename)
        try:
            with open(test_path, "r") as file:
                content = file.read()
        except Exception as error:
            print(f"[TEST] Error reading test file '{test_filename}': {error}")
            return False

        # Compile the QCDL content.
        try:
            compiler = QCDLCompiler()
            compiler.compile(content)
        except Exception as error:
            print(f"[QCDL] Compilation error in '{test_filename}': {error}")
            return False

        # Ensure the expected result is provided inside the file.
        if compiler.expected_result is None:
            print(f"[TEST] No expected result found in '{test_filename}'. Expected a line starting with '?'.")
            return False

        # Run the simulation and compute outcome probabilities.
        try:
            simulator = Simulator(compiler.operations)
            final_state = simulator.run()
            probabilities = np.abs(final_state) ** 2 * 100
            sim_percentages = {}
            total_states = 2 ** simulator.num_qubits
            for index in range(total_states):
                outcome_tuple = tuple(int(bit) for bit in format(index, f'0{simulator.num_qubits}b'))
                sim_percentages[outcome_tuple] = probabilities[index]
            # Filter out outcomes with negligible (0.0) probability.
            sim_percentages = {outcome: perc for outcome, perc in sim_percentages.items() if perc > 1e-6}
        except Exception as error:
            print(f"[TEST] Simulation error in '{test_filename}': {error}")
            return False

        # Compare the computed probabilities with the expected results.
        if self.compare_results(sim_percentages, compiler.expected_result):
            print(f"\033[92m[TEST] Test '{test_filename}' passed.\033[0m")
            return True
        else:
            print(f"\033[91m[TEST] Test '{test_filename}' failed.\033[0m")
            print("-" * 43)

            all_outcomes = set(compiler.expected_result.keys()) | set(sim_percentages.keys())

            for outcome in sorted(all_outcomes):
                expected = compiler.expected_result.get(outcome, 0.0)
                actual = sim_percentages.get(outcome, 0.0)
                
                diff = abs(expected - actual)
                
                if diff > self.tolerance:
                    print(f"{outcome} | Expected: {expected:.3f} | Actual: {actual:.3f} \033[91m(Diff: {diff:.3f})\033[0m")
                else:
                    print(f"{outcome} | Expected: {expected:.3f} | Actual: {actual:.3f}")

            print("-" * 43)
            return False

        
    def compare_results(self, sim_percentages, expected_percentages):
        """Compare simulation results with expected results within a specified tolerance."""
        if set(sim_percentages.keys()) != set(expected_percentages.keys()):
            return False

        for outcome, expected_percentage in expected_percentages.items():
            sim_percentage = sim_percentages[outcome]
            if not np.isclose(sim_percentage, expected_percentage, rtol=self.tolerance):
                return False
        return True

    def run_all_tests(self):
        """
        Discover and run all .qcdl tests in the tests directory.
        Prints a summary of passed and failed tests.
        """
        tests = [f for f in os.listdir(self.tests_directory) if f.endswith(".qcdl")]
        total_tests = len(tests)
        passed_tests = 0

        for test in tests:
            if self.run_test(test):
                passed_tests += 1

        print("\nTest Summary:")
        print("-" * 20)
        print(f"{'Total Tests:':<12} {total_tests:>4}")
        print(f"\033[92m{'Passed:':<12} {passed_tests:>4}\033[0m")
        failed_tests = total_tests - passed_tests
        if failed_tests > 0:
            print(f"\033[91m{'Failed:':<12} {failed_tests:>4}\033[0m")
        else:
            print(f"{'Failed:':<12} {failed_tests:>4}")
        print("-" * 20)


########
# MAIN #
########

if __name__ == "__main__":
    tester = Tester()
    tester.run_all_tests()
