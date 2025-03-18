"""
This script provides a command-line interface for compiling and simulating quantum circuits described in QCDL.
It prompts the user to enter the name of a QCDL file, reads the file content, compiles it using the `QCDLCompiler`, 
and then simulates the resulting quantum circuit using the `Simulator`. 
The script then outputs the final state vector and the probabilities of measurement outcomes.

Author: Tex024
Date: 18/03/2024
"""

import sys
from src.qparser import QCDLCompiler
from src.qsimulator import Simulator

########
# MAIN #
########

if __name__ == "__main__":
    filename = input("Enter the QCDL file name: ").strip()
    try:
        with open(filename, "r") as file:
            content = file.read()
    except Exception as error:
        print(f"Error opening file '{filename}': {error}")
        sys.exit(1)

    # Compile the QCDL code
    compiler = QCDLCompiler()
    compiler.compile(content)
    
    print("\033[92m[QCDL] Compilation successful.\033[0m")
    print("Simulating circuit...")

    # Run the simulator
    simulator = Simulator(compiler.operations)
    final_state = simulator.run()

    # Print the results
    simulator.print_final_state()
    simulator.print_result()
