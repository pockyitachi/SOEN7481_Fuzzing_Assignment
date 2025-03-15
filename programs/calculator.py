import ast
import operator
import numpy as np
import matplotlib.pyplot as plt
import math
import time
import logging
import os
import threading
from collections import deque

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
FUZZING_MODE = os.getenv("FUZZING_MODE", "0") == "1"

class SafeEvaluator(ast.NodeVisitor):
    """Evaluates mathematical expressions safely using AST parsing and supports functions, variables, and modes."""

    operators = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Mod: operator.mod, ast.Pow: operator.pow,
        ast.BitAnd: operator.and_, ast.BitOr: operator.or_,
        ast.BitXor: operator.xor, ast.LShift: operator.lshift,
        ast.RShift: operator.rshift
    }

    functions = {
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'log': math.log, 'exp': math.exp, 'sqrt': math.sqrt,
        'abs': abs, 'round': round, 'ceil': math.ceil, 'floor': math.floor,
        'factorial': math.factorial
    }

    def __init__(self, debug=False):
        self.variables = {}  # Store user-defined variables
        self.functions = {}  # Store user-defined functions
        self.history = deque(maxlen=50)  # Store last 50 operations
        self.debug = debug  # Debug mode
        self.execution_mode = "basic"  # Can be 'basic', 'scientific', 'programming'

    def visit_BinOp(self, node):
        """Handles binary operations."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        if self.debug:
            logging.debug(f"Evaluating: {left} {type(node.op)} {right}")
        try:
            return self.operators[type(node.op)](left, right)
        except ZeroDivisionError:
            return "Error: Division by zero"
        except Exception as e:
            return f"Error: {e}"

    def visit_UnaryOp(self, node):
        """Handles unary operations."""
        return -self.visit(node.operand) if isinstance(node.op, ast.USub) else self.visit(node.operand)

    def visit_Name(self, node):
        """Handles variable usage."""
        return self.variables.get(node.id, f"Error: Undefined variable '{node.id}'")

    def visit_Num(self, node):
        """Handles numbers."""
        return node.n

    def visit_Expr(self, node):
        """Handles expressions."""
        return self.visit(node.value)

    def visit_Call(self, node):
        """Handles function calls."""
        func_name = node.func.id if isinstance(node.func, ast.Name) else None
        if func_name in self.functions:
            try:
                arg_value = self.visit(node.args[0])
                return self.functions[func_name](arg_value)
            except Exception as e:
                return f"Error: Invalid input for {func_name}()"
        return f"Error: Unsupported function '{func_name}'"

    def visit_Assign(self, node):
        """Handles variable assignments."""
        var_name = node.targets[0].id
        value = self.visit(node.value)
        self.variables[var_name] = value
        return f"Variable '{var_name}' set to {value}"

    def evaluate(self, expr):
        """Evaluates an expression safely."""
        try:
            parsed_expr = ast.parse(expr, mode="exec" if "=" in expr else "eval")
            result = self.visit(parsed_expr.body[0]) if isinstance(parsed_expr, ast.Module) else self.visit(
                parsed_expr.body)
            self.history.append(expr)
            return result
        except Exception as e:
            return f"Error: {e}"

    def list_variables(self):
        """Returns the stored variables."""
        return self.variables


def evaluate_expression(expr):
    """Evaluates a mathematical expression safely."""
    evaluator = SafeEvaluator()
    return evaluator.evaluate(expr)


def plot_function(expr, x_min=-10, x_max=10, num_points=500):
    """Plots a mathematical function with x in a given range."""
    try:
        evaluator = SafeEvaluator()
        x_values = np.linspace(x_min, x_max, num_points)
        y_values = [evaluator.evaluate(expr.replace("x", str(x))) for x in x_values]

        plt.figure(figsize=(8, 5))
        plt.plot(x_values, y_values, label=f"f(x) = {expr}", color="b")
        plt.axhline(0, color="black", linewidth=0.5)
        plt.axvline(0, color="black", linewidth=0.5)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()
        plt.title(f"Graph of f(x) = {expr}")
        plt.xlabel("x")
        plt.ylabel("f(x)")
        plt.show()

    except Exception as e:
        logging.error(f"Graphing Error: {e}")


def process_input(expr):
    """Automatically decides whether to evaluate, assign a variable, or plot."""
    expr = expr.strip()
    evaluator = SafeEvaluator()

    if "=" in expr:
        logging.info(f"Processing assignment: {expr}")
        result = evaluator.evaluate(expr)
        print(result)
    elif "x" in expr and not FUZZING_MODE:  # Prevents plotting when fuzzing
        logging.info(f"Detected function: {expr} → Plotting graph.")
        plot_function(expr, -10, 10)
    elif expr.lower() == "vars":
        print("Stored Variables:", evaluator.list_variables())
    else:
        result = evaluator.evaluate(expr)
        print(f"Evaluated: {expr} = {result}")


if __name__ == "__main__":
    while True:
        expr = input("\nEnter an expression, function, or assignment (or type 'exit' to quit): ")
        if expr.lower() == "exit":
            print("Exiting calculator...")
            break
        process_input(expr)
