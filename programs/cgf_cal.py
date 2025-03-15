import random
import coverage
import numpy as np
import matplotlib.pyplot as plt
from calculator import SafeEvaluator, process_input  # Import calculator components

# Initialize Coverage.py
cov = coverage.Coverage()
cov.start()

# Operators & Functions
OPERATORS = ["+", "-", "*", "/", "**", "%"]
FUNCTIONS = ["sin", "cos", "tan", "log", "exp", "sqrt", "abs"]

# Seed expressions (initial inputs)
seed_inputs = [
    "2 + 3", "5 * 6", "log(10)", "sin(3.14)", "exp(2)",
    "x ** 2", "sqrt(x)", "x + 5 * sin(x)", "cos(x) / log(x + 1)"
]

# Fuzzing Parameters
num_iterations = 500  # Total test cases
coverage_progress = []
unique_coverage = set()  # Track unique executed lines

# Initialize evaluator
evaluator = SafeEvaluator()


def mutate_expression(expr):
    """Mutate an existing expression in a way that might increase coverage."""
    if random.random() < 0.4:
        # Insert a function at a random position
        func = random.choice(FUNCTIONS)
        value = "x" if "x" in expr and random.random() < 0.7 else str(round(random.uniform(-20, 20), 2))
        mutation = f"{func}({value})"
    else:
        # Insert a complex subexpression
        mutation = f"({expr} {random.choice(OPERATORS)} {round(random.uniform(-20, 20), 2)})"

    return mutation


# Start Fuzzing
for i in range(num_iterations):
    # Choose from seeds or mutate an existing input
    if random.random() < 0.3:
        expr = random.choice(seed_inputs)  # Use existing expression
    else:
        expr = mutate_expression(random.choice(seed_inputs))

    # Execute and check coverage
    try:
        if "x" in expr:
            x_vals = np.linspace(-10, 10, 100)
            y_vals = [evaluator.evaluate(expr.replace("x", str(x))) for x in x_vals]
        else:
            evaluator.evaluate(expr)

        process_input(expr)  # Also test input handling
    except Exception:
        pass  # Ignore errors

    # Measure coverage
    cov.stop()
    cov.save()
    covered_lines = set(cov.analysis("calculator.py")[1])  # Get executed line numbers

    if covered_lines - unique_coverage:  # New coverage found?
        unique_coverage.update(covered_lines)  # Add to discovered lines
        seed_inputs.append(expr)  # Keep test case that helped!

    # Log coverage every 10 iterations
    if i % 10 == 0:
        coverage_progress.append(len(unique_coverage))

    cov.start()

# Stop coverage tracking
cov.stop()
cov.save()

# Get total possible lines
total_lines = len(cov.analysis("calculator.py")[0])

# Plot Coverage Progress
plt.figure(figsize=(8, 5))
plt.plot(range(0, num_iterations, 10), coverage_progress, marker="o", linestyle="-", color="b",
         label="Coverage-Guided Progress")
plt.axhline(total_lines, color="r", linestyle="--", label="Max Coverage")
plt.xlabel("Fuzzing Iterations")
plt.ylabel("Covered Lines")
plt.title("Coverage-Guided Fuzzing Progress")
plt.legend()
plt.grid(True)
plt.savefig("coverage_plot_cal_cgf.png")  # Saves the plot instead of displaying it
print("Coverage plot saved as 'coverage_plot_cal_cgf.png'.")
print(f"Total covered lines: {len(unique_coverage)} / {total_lines}")