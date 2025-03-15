import random
import string
import matplotlib.pyplot as plt
import numpy as np
from collections import deque

# ----------------------------------------------------------------------
# 1. GLOBAL COVERAGE TRACKING (BINARY)
# ----------------------------------------------------------------------
coverage_map = {}  # Maps branch -> 1 (covered)


def record_coverage(branch):
    """
    Mark a branch as covered (1).
    Once covered, we don't increment any counters further.
    """
    global coverage_map
    coverage_map[branch] = 1


def current_coverage_count():
    """Return how many distinct branches have been covered so far."""
    return len(coverage_map)


# ----------------------------------------------------------------------
# 2. MAZE CLASS: PARSE, VALIDATE, SOLVE, VISUALIZE
# ----------------------------------------------------------------------
class Maze:
    def __init__(self, grid, start, finish):
        self.grid = grid  # 2D list of characters
        self.start = start  # (row, col)
        self.finish = finish  # (row, col)
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0

    @classmethod
    def from_string(cls, text):
        """Parses a multi-line string into a Maze object (binary coverage)."""
        if not text.strip():
            record_coverage("empty_input")
            raise ValueError("Maze input is empty.")

        lines = text.strip().split('\n')
        grid = []
        start = finish = None

        expected_length = len(lines[0])
        for r, line in enumerate(lines):
            # Check for rectangular shape
            if len(line) != expected_length:
                record_coverage("non_rectangular")
                raise ValueError("Maze is not rectangular.")
            row = list(line)
            for c, ch in enumerate(row):
                if ch == 'S':
                    if start is None:
                        start = (r, c)
                        record_coverage("found_start")
                    else:
                        record_coverage("multiple_start")
                        raise ValueError("Multiple start points found.")
                elif ch == 'F':
                    if finish is None:
                        finish = (r, c)
                        record_coverage("found_finish")
                    else:
                        record_coverage("multiple_finish")
                        raise ValueError("Multiple finish points found.")
                elif ch not in ('#', '.', ' ', 'S', 'F'):
                    # Mark invalid characters
                    record_coverage("invalid_char")
            grid.append(row)

        if start is None:
            record_coverage("no_start")
            raise ValueError("No start point found in maze.")
        if finish is None:
            record_coverage("no_finish")
            raise ValueError("No finish point found in maze.")

        record_coverage("maze_parsed")
        return cls(grid, start, finish)

    def find_shortest_path(self):
        """Uses BFS to find the shortest path from start to finish (binary coverage)."""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        queue = deque([(self.start, [self.start])])
        visited = set([self.start])
        record_coverage("bfs_start")

        while queue:
            (r, c), path = queue.popleft()
            if (r, c) == self.finish:
                record_coverage("path_found")
                return path
            for dr, dc in directions:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if (nr, nc) not in visited and self.grid[nr][nc] != '#':
                        visited.add((nr, nc))
                        queue.append(((nr, nc), path + [(nr, nc)]))
                        record_coverage("queue_append")
        record_coverage("no_path")
        return None

    def visualize_path(self, path):
        """Return a string representation of the maze with the path overlaid."""
        visual = [row.copy() for row in self.grid]
        if path:
            for r, c in path:
                if visual[r][c] not in ('S', 'F'):
                    visual[r][c] = '*'
            record_coverage("visual_path")
        else:
            record_coverage("visual_no_path")
        return "\n".join("".join(row) for row in visual)


# ----------------------------------------------------------------------
# 3. FUZZING HELPERS
# ----------------------------------------------------------------------
def generate_random_maze_string():
    """Generates a random multi-line maze string with random dimensions."""
    rows = random.randint(3, 10)
    cols = random.randint(3, 10)
    maze = []
    # Random positions for S and F
    start_row, start_col = random.randint(0, rows - 1), random.randint(0, cols - 1)
    finish_row, finish_col = random.randint(0, rows - 1), random.randint(0, cols - 1)
    for r in range(rows):
        line_chars = []
        for c in range(cols):
            if (r, c) == (start_row, start_col):
                line_chars.append('S')
            elif (r, c) == (finish_row, finish_col):
                line_chars.append('F')
            else:
                # Randomly choose wall or open space
                ch = random.choices(['#', '.', ' '], weights=[30, 60, 10])[0]
                line_chars.append(ch)
        maze.append("".join(line_chars))
    return "\n".join(maze)


def mutate_maze_string(maze_str):
    """Mutates the maze string by randomly inserting, deleting, or replacing a character."""
    if not maze_str:
        return generate_random_maze_string()
    mutation_type = random.choice(["insert", "delete", "replace"])
    pos = random.randint(0, len(maze_str) - 1)
    if mutation_type == "insert":
        new_char = random.choice(string.printable + "\n")
        return maze_str[:pos] + new_char + maze_str[pos:]
    elif mutation_type == "delete":
        return maze_str[:pos] + maze_str[pos + 1:]
    elif mutation_type == "replace":
        new_char = random.choice(string.printable + "\n")
        return maze_str[:pos] + new_char + maze_str[pos + 1:]
    return maze_str


# ----------------------------------------------------------------------
# 4. FUZZING FUNCTIONS THAT TRACK COVERAGE OVER ITERATIONS
# ----------------------------------------------------------------------
def pure_random_fuzzing(iterations=500):
    """
    Performs pure random fuzzing on the maze parsing and solving functions.
    Returns:
      - final coverage map (branch -> 1)
      - a list coverage_history where coverage_history[i] = number of covered branches after iteration i
    """
    global coverage_map
    coverage_map = {}  # Reset coverage

    coverage_history = []
    for _ in range(iterations):
        random_maze = generate_random_maze_string()
        try:
            m = Maze.from_string(random_maze)
            m.find_shortest_path()
        except Exception:
            record_coverage("exception")
        # Record how many branches are covered so far
        coverage_history.append(current_coverage_count())

    return coverage_map.copy(), coverage_history


def coverage_guided_fuzzing(iterations=500):
    """
    Performs coverage-guided fuzzing on the maze functions using seed inputs.
    Returns:
      - final coverage map (branch -> 1)
      - a list coverage_history where coverage_history[i] = number of covered branches after iteration i
    """
    global coverage_map
    coverage_map = {}  # Reset coverage

    # Start with a handful of seed mazes
    seeds = [generate_random_maze_string() for _ in range(5)]
    total_covered_branches = set()
    coverage_history = []

    for _ in range(iterations):
        seed = random.choice(seeds)
        mutated = mutate_maze_string(seed)

        # Temporarily store coverage for this run
        temp_map = {}
        saved_map = coverage_map
        coverage_map = temp_map

        try:
            m = Maze.from_string(mutated)
            m.find_shortest_path()
        except Exception:
            record_coverage("exception")

        # Merge coverage from this iteration
        newly_covered = set(temp_map.keys()) - total_covered_branches
        if newly_covered:
            # Add mutated input if it yields new coverage
            seeds.append(mutated)
            total_covered_branches.update(newly_covered)

        # Once covered, always covered
        for branch in temp_map:
            saved_map[branch] = 1

        coverage_map = saved_map
        total_covered_branches = set(coverage_map.keys())

        # Record coverage size
        coverage_history.append(len(total_covered_branches))

    return coverage_map.copy(), coverage_history


# ----------------------------------------------------------------------
# 5. PLOTTING COVERAGE OVER TIME
# ----------------------------------------------------------------------
def plot_coverage_over_iterations(coverage_random_list, coverage_guided_list):
    """
    Plots how coverage changes over iterations for both fuzzing methods.
    coverage_random_list[i] = coverage after i-th iteration (pure random)
    coverage_guided_list[i] = coverage after i-th iteration (guided)
    """
    plt.figure(figsize=(8, 5))
    plt.plot(coverage_random_list, label='Pure Random', color='blue')
    plt.plot(coverage_guided_list, label='Coverage Guided', color='orange')
    plt.xlabel('Iteration')
    plt.ylabel('Number of Covered Branches')
    plt.title('Coverage Growth Over Iterations')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ----------------------------------------------------------------------
# 6. MAIN
# ----------------------------------------------------------------------
def main():
    print("=== Maze Solver: Tracking Coverage Over Time ===")
    sample_maze = (
        "S.#.\n"
        ".#F.\n"
        "....\n"
    )
    print("Sample Maze:\n", sample_maze)

    try:
        m = Maze.from_string(sample_maze)
        path = m.find_shortest_path()
        if path:
            print("Found a path:")
            print(m.visualize_path(path))
        else:
            print("No path found in the maze.")
    except Exception as e:
        print("Error processing maze:", e)

    # Run Pure Random Fuzzing
    print("\n=== Running Pure Random Fuzzing ===")
    cov_random, random_history = pure_random_fuzzing(iterations=300)
    print("Final Covered Branches (Pure Random):", cov_random.keys())
    print("Coverage Growth (Pure Random):", random_history[-10:], "... (last 10 iterations)")

    # Run Coverage-Guided Fuzzing
    print("\n=== Running Coverage-Guided Fuzzing ===")
    cov_guided, guided_history = coverage_guided_fuzzing(iterations=300)
    print("Final Covered Branches (Coverage Guided):", cov_guided.keys())
    print("Coverage Growth (Coverage Guided):", guided_history[-10:], "... (last 10 iterations)")

    # Plot how coverage changes over iterations
    print("\n=== Plotting Coverage Over Iterations ===")
    plot_coverage_over_iterations(random_history, guided_history)


if __name__ == '__main__':
    main()
