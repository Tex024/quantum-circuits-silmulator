from src.qsimulator import *
from src.qparser import *

filename = input("Enter QCDL file name: ").strip()

try:
    with open(filename, "r") as file:
        content = file.read()
except Exception as error:
    print(f"Error opening file '{filename}': {error}")
    sys.exit(1)

num_simulations = int(input("Enter number of simulations: ").strip())

compiler = QCDLCompiler()
compiler.compile(content)

print("Compilation successful. Simulating circuit...")
simulator = Simulator(compiler.operations, num_simulations)
simulator.run_all()
simulator.print_results()
