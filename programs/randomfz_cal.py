import random
import subprocess
import coverage
import matplotlib.pyplot as plt
import os

# Set environment variable to disable plotting
os.environ["FUZZING_MODE"] = "1"

# Random expression components
OPERATORS = ["+", "-", "*", "/", "**", "%"]
FUNCTIONS = ["sin", "cos", "tan", "log", "exp", "sqrt", "abs", "round", "ceil", "floor", "factorial"]
VARIABLES = ["a", "b", "c"]
NUMBERS = [str(random.randint(-100, 100)) for _ in range(20)]


def random_expression():
    """Generates a random mathematical expression."""
    expr = random.choice(NUMBERS)
    for _ in range(random.randint(1, 5)):  # Randomly add operations
        if random.random() < 0.2:  # 20% chance to use a function
            expr = f"{random.choice(FUNCTIONS)}({expr})"
        elif random.random() < 0.3:  # 30% chance to use a variable
            expr = f"{random.choice(VARIABLES)} = {expr}"
        else:  # Otherwise, use an operator
            expr += f" {random.choice(OPERATORS)} {random.choice(NUMBERS)}"
    return expr


def fuzz_calculator(num_tests=1000):
    """Runs pure random fuzzing and tracks coverage per iteration."""
    cov = coverage.Coverage(source=["calculator"])  # Track only `calculator.py`
    cov.start()

    coverage_over_time = []  # Store coverage % at each iteration

    for i in range(1, num_tests + 1):
        expr = random_expression()
        subprocess.run(
            ["python", "calculator.py"],
            input=expr,
            text=True,
            capture_output=True,
            env=os.environ,  # Pass environment variable
        )

        # Collect coverage data at every 50 iterations
        if i % 50 == 0:
            cov.stop()
            cov.save()
            covered_lines = len(cov.analysis("calculator.py")[3])  # Covered lines
            total_lines = len(cov.analysis("calculator.py")[1])  # Total lines
            coverage_percent = (covered_lines / total_lines) * 100 if total_lines > 0 else 0
            coverage_over_time.append((i, coverage_percent))
            cov.start()

    cov.stop()
    cov.save()

    # Plot and save coverage trend
    plot_coverage_trend(coverage_over_time)


def plot_coverage_trend(coverage_data):
    """Plots and saves the coverage trend over iterations."""
    iterations, coverage_values = zip(*coverage_data)

    plt.figure(figsize=(8, 5))
    plt.plot(iterations, coverage_values, marker="o", linestyle="-")
    plt.title("Code Coverage Over Fuzzing Iterations")
    plt.xlabel("Iterations")
    plt.ylabel("Coverage (%)")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.savefig("coverage_trend.png")
    plt.show()
    print("Coverage trend saved as 'coverage_trend.png'.")


if __name__ == "__main__":
    print("Starting fuzzing test...")
    fuzz_calculator(1000)
    print("Fuzzing completed.")
