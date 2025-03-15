import random
import string
import matplotlib.pyplot as plt
import numpy as np

# Global variable for coverage tracking.
# We use a mutable global variable to record each branch hit.
current_coverage_map = {}


def record_coverage(branch):
    """Record coverage for the given branch in the global coverage map."""
    global current_coverage_map
    # Mark each branch as covered at least once (binary coverage approach).
    # If you still want to count hits, replace the next line with += 1.
    current_coverage_map[branch] = 1


# ----------------------------------------------------------------------
# Complex function with many branches and helper functions.
# This function processes an input string with various checks.
# ----------------------------------------------------------------------
def process_input(data):
    record_coverage("start")
    result = ""
    # Branch 1: Check if the input is very short.
    if len(data) < 3:
        record_coverage("len_short")
        result += "Too short."
        if len(data) == 0:
            record_coverage("empty")
            result += " (empty)"
        else:
            record_coverage("not_empty")
        return result
    else:
        record_coverage("len_ok")
        # Branch 2: Check if the input starts with an alphabet.
        if data[0].isalpha():
            record_coverage("alpha_start")
            result += "Starts with alpha. "
        else:
            record_coverage("non_alpha_start")
            result += "Does not start with alpha. "
        # Branch 3: Check for any digits.
        if any(ch.isdigit() for ch in data):
            record_coverage("digit_found")
            result += "Has digit. "
        else:
            record_coverage("no_digit")
            result += "No digit. "
        # Branch 4: Check the case of the string.
        if data.isupper():
            record_coverage("all_upper")
            result += "All upper. "
        elif data.islower():
            record_coverage("all_lower")
            result += "All lower. "
        else:
            record_coverage("mixed_case")
            result += "Mixed case. "
        # Branch 5: Check for special characters.
        if any(ch in "!@#$%^&*()" for ch in data):
            record_coverage("special_char")
            result += "Special char found. "
        else:
            record_coverage("no_special_char")
            result += "No special char. "
        # Branch 6: Try converting the input to an integer.
        try:
            num = int(data)
            record_coverage("numeric")
            result += "Numeric input. "
        except ValueError:
            record_coverage("non_numeric")
            result += "Non-numeric input. "
        # Branch 7: Check if the length is even or odd.
        if len(data) % 2 == 0:
            record_coverage("even_length")
            result += "Even length. "
        else:
            record_coverage("odd_length")
            result += "Odd length. "
        # Branch 8: Check for the greeting "hello" (case-insensitive).
        if "hello" in data.lower():
            record_coverage("greeting")
            result += "Greeting detected. "
        else:
            record_coverage("no_greeting")
            result += "No greeting. "
        # Branch 9: Count digits and compare to a threshold.
        count_digits = sum(1 for ch in data if ch.isdigit())
        if count_digits > 2:
            record_coverage("many_digits")
            result += "Many digits. "
        else:
            record_coverage("few_digits")
            result += "Few digits. "
        # Branch 10: Check if the input is a palindrome.
        if data == data[::-1]:
            record_coverage("palindrome")
            result += "Palindrome. "
        else:
            record_coverage("not_palindrome")
            result += "Not a palindrome. "
    return result


# Additional helper functions to increase complexity
def helper_function_a(x):
    """Compute the sum of squares from 1 to x."""
    total = 0
    for i in range(1, x + 1):
        total += i * i
    return total


def helper_function_b(s):
    """Reverse the order of words in a sentence."""
    words = s.split()
    return " ".join(words[::-1])


def compute_fibonacci(n):
    """Compute the nth Fibonacci number recursively."""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return compute_fibonacci(n - 1) + compute_fibonacci(n - 2)


def process_data_list(data_list):
    """Process a list of strings using process_input and helper functions."""
    results = []
    for data in data_list:
        res = process_input(data)
        res += " | SumSquares: " + str(helper_function_a(len(data)))
        res += " | Reversed: " + helper_function_b(data)
        results.append(res)
    return results


def simulate_complex_operations():
    """Simulate various operations to add complexity to the program."""
    fib = compute_fibonacci(10)
    message = "Hello world from complex simulation"
    reversed_message = helper_function_b(message)
    squares = helper_function_a(10)
    combined = f"Fibonacci: {fib}, Message: {reversed_message}, Squares: {squares}"
    return combined


# ----------------------------------------------------------------------
# Fuzzing functions with coverage tracking over time.
# ----------------------------------------------------------------------
def pure_random_fuzzing(iterations=1000):
    """
    Perform pure random fuzzing on process_input.
    Returns a list that tracks how many branches are covered after each iteration.
    """
    global current_coverage_map
    current_coverage_map = {}  # Reset coverage
    coverage_history = []

    for _ in range(iterations):
        length = random.randint(0, 20)
        random_input = ''.join(random.choices(string.printable, k=length))
        try:
            process_input(random_input)
        except Exception:
            record_coverage("fuzz_exception")
        # Append the number of covered branches so far
        coverage_history.append(len(current_coverage_map))

    return coverage_history


def mutate_input(input_str):
    """Randomly mutate the input string by insertion, deletion, or replacement."""
    if not input_str:
        input_str = random.choice(string.printable)
    mutation_type = random.choice(["insert", "delete", "replace"])
    pos = random.randint(0, len(input_str) - 1) if input_str else 0
    if mutation_type == "insert":
        new_char = random.choice(string.printable)
        return input_str[:pos] + new_char + input_str[pos:]
    elif mutation_type == "delete" and len(input_str) > 0:
        return input_str[:pos] + input_str[pos + 1:]
    elif mutation_type == "replace" and len(input_str) > 0:
        new_char = random.choice(string.printable)
        return input_str[:pos] + new_char + input_str[pos + 1:]
    return input_str


def coverage_guided_fuzzing(iterations=1000):
    """
    Perform coverage-guided fuzzing on process_input.
    Returns a list that tracks how many branches are covered after each iteration.
    """
    global current_coverage_map
    current_coverage_map = {}  # Reset coverage
    coverage_history = []

    seeds = ["", "a", "A", "0", "hello", "123", "!@#"]
    total_coverage = set()

    for _ in range(iterations):
        seed = random.choice(seeds)
        mutated = mutate_input(seed)

        temp_map = {}
        # Temporarily use a new coverage map for this run.
        saved_map = current_coverage_map
        current_coverage_map = temp_map

        try:
            process_input(mutated)
        except Exception:
            record_coverage("fuzz_exception")

        # Determine which new branches we covered in this iteration
        new_branches = set(temp_map.keys()) - total_coverage
        if new_branches:
            seeds.append(mutated)
            total_coverage.update(new_branches)

        # Merge temporary coverage into the saved map.
        for branch in temp_map:
            saved_map[branch] = 1  # Mark as covered
        current_coverage_map = saved_map

        coverage_history.append(len(current_coverage_map))

    return coverage_history


# ----------------------------------------------------------------------
# Plot coverage vs. iteration (line chart).
# ----------------------------------------------------------------------
def plot_coverage_evolution(coverage_random, coverage_guided):
    """Plot how coverage (number of covered branches) changes over iterations."""
    plt.figure(figsize=(8, 5))
    plt.plot(coverage_random, label='Pure Random', color='blue')
    plt.plot(coverage_guided, label='Coverage Guided', color='orange')
    plt.xlabel('Iteration')
    plt.ylabel('Number of Covered Branches')
    plt.title('Fuzzing Coverage Over Iterations')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ----------------------------------------------------------------------
# Main function to run the fuzzers and plot the comparison over time.
# ----------------------------------------------------------------------
def main():
    print("Simulating complex operations...")
    simulation_result = simulate_complex_operations()
    print(simulation_result)

    print("\nRunning pure random fuzzing...")
    coverage_history_random = pure_random_fuzzing(iterations=2000)
    print("Final coverage (branches covered) with Pure Random:", coverage_history_random[-1])

    print("\nRunning coverage-guided fuzzing...")
    coverage_history_guided = coverage_guided_fuzzing(iterations=2000)
    print("Final coverage (branches covered) with Coverage-Guided:", coverage_history_guided[-1])

    print("\nPlotting coverage evolution...")
    plot_coverage_evolution(coverage_history_random, coverage_history_guided)


if __name__ == '__main__':
    main()
