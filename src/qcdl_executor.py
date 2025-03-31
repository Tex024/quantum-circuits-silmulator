"""
This script executes quantum circuits described in QCDL (Quantum Circuit Description Language).
It takes a QCDL file as input, compiles it using the `QCDLCompiler`, 
simulates the resulting quantum circuit using the `Simulator`, 
and outputs the final state vector and measurement probabilities.

Author: Tex024
Date: 18/03/2024
"""

import sys
from src.qparser import QCDLCompiler
from src.qsimulator import Simulator

########
# MAIN #
########

class QCLDExecutor:

    def run(filename: str):
        """Run and execute the file"""
        try:
            with open(filename.strip(), "r") as file:
                content = file.read()
        except Exception as error:
            print(f"Error opening file '{filename.strip()}': {error}")
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

if __name__ == "__main__":
    filename = input("Enter the QCDL file name: ").strip()
    try:
        with open(filename, "r") as file:
            content = file.read()
    except Exception as error:
        print(f"Error opening file '{filename}': {error}")
        sys.exit(1)

    QCLDExecutor.run(filename)
