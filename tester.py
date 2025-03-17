import os
import numpy as np

from src.qsimulator import *
from src.qparser import *

class Tester:
    def __init__(self, tests_directory="tests", num_simulations=5000):
        """
        Initialize the tester.
        
        Parameters:
            tests_directory (str): Path to the folder containing test files.
            num_simulations (int): Number of simulations to run for each test.
        """
        self.tests_directory = tests_directory
        self.num_simulations = num_simulations
        self.tolerance = 0.05

    def run_test(self, test_filename):
        """
        Run a single test.
        
        Parameters:
            test_filename (str): The filename of the .qcdl test file.
        
        Returns:
            bool: True if the test output matches the expected result, False otherwise.
        """
        test_path = os.path.join(self.tests_directory, test_filename)
        try:
            with open(test_path, "r") as file:
                content = file.read()
        except Exception as error:
            print(f"Error reading test file '{test_filename}': {error}")
            return False

        # Compile the QCDL content.
        try:
            compiler = QCDLCompiler()
            compiler.compile(content)
        except Exception as error:
            print(f"Compilation error in '{test_filename}': {error}")
            return False

        # Ensure the expected result is provided inside the file.
        if compiler.expected_result is None:
            print(f"No expected result found in '{test_filename}'. Expected a line starting with '?'.")
            return False

        # Run the simulation and capture the printed output.
        try:
            simulator = Simulator(compiler.operations, self.num_simulations)
            simulator.run_all()
            sim_percentages = simulator.percentages  # dict with keys as outcome tuples and values as percentages.
        except Exception as error:
            print(f"Simulation error in '{test_filename}': {error}")
            return False

        # Compare the simulation percentages with the expected result.
        if self.compare_results(sim_percentages, compiler.expected_result):
            print(f"Test '{test_filename}' passed.")
            return True
        else:
            print(f"Test '{test_filename}' failed.")
            print("Expected percentages:")
            print(compiler.expected_result)
            print("Simulation percentages:")
            print(sim_percentages)
            return False
        
    def compare_results(self, sim_percentages, expected_percentages):
        """
        Compare simulation results with expected results within a specified tolerance.
        """
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

        print("\n[QCDL] Test Summary:")
        print(f"\tTotal tests: {total_tests}")
        print(f"\tPassed: {passed_tests}")
        print(f"\tFailed: {total_tests - passed_tests}")

if __name__ == "__main__":
    tester = Tester()
    tester.run_all_tests()