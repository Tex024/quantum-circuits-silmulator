"""
This script provides a command-line interface for testing and running QCDL (Quantum Circuit Description Language) files.

It supports two main functionalities:
1. Running all defined tests.
2. Executing a specified QCDL file.

Usage:
  python3 main.py test
  python3 main.py run <qcdl_file>

Author: Tex024
Date: 31/03/2024
"""

import sys

from src.tester import Tester
from src.qcdl_executor import QCLDExecutor

def print_usage():
    """
    Prints the correct usage instructions for the script and exits.
    This function is called when the script is invoked with incorrect arguments.
    """
    print("Usage:")
    print("  python3 main.py test")
    print("  python3 main.py run <qcdl_file>")
    sys.exit(1)

def main():
    """
    Main function that parses command-line arguments and executes the corresponding action.
    It handles 'test' and 'run' commands, invoking the appropriate modules.
    """
    if len(sys.argv) < 2:
        print_usage()

    command = sys.argv[1].lower()  # Convert command to lowercase for case-insensitive matching

    if command == "test":
        """
        Executes all tests defined in the 'tester.py' module.
        """
        tester = Tester()
        tester.run_all_tests()

    elif command == "run":
        """
        Executes a specified QCDL file using the 'qcdl_executor.py' module.
        Requires a filename as the second command-line argument.
        """
        if len(sys.argv) < 3:
            print("Error: No QCDL file specified.")
            print_usage()
        filename = sys.argv[2]
        QCLDExecutor.run(filename)

    else:
        """
        Handles unknown commands by printing an error message and usage instructions.
        """
        print(f"Error: Unknown command '{command}'.")
        print_usage()

if __name__ == "__main__":
    main()