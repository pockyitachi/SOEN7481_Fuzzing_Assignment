import ast
import operator
import numpy as np
import matplotlib.pyplot as plt
import math


class SafeEvaluator(ast.NodeVisitor):
    """Evaluates mathematical expressions safely using AST parsing and supports functions."""

    operators = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Mod: operator.mod, ast.Pow: operator.pow
    }

    functions = {
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'log': math.log, 'exp': math.exp, 'sqrt': math.sqrt,
        'abs': abs
    }

    def visit_BinOp(self, node):
        """Handles binary operations like 3 + 5, 2 ** 3, etc."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        if type(node.op) in self.operators:
            return self.operators[type(node.op)](left, right)
        raise ValueError(f"Unsupported operation: {type(node.op)}")

    def visit_UnaryOp(self, node):
        """Handles unary operations like -5."""
        if isinstance(node.op, ast.UAdd):
            return self.visit(node.operand)
        elif isinstance(node.op, ast.USub):
            return -self.visit(node.operand)

    def visit_Num(self, node):
        """Handles numbers."""
        return node.n

    def visit_Expr(self, node):
        """Handles expressions."""
        return self.visit(node.value)

    def visit_Call(self, node):
        """Handles function calls like sin(x), log(10)."""
        if isinstance(node.func, ast.Name) and node.func.id in self.functions:
            arg = self.visit(node.args[0])
            return self.functions[node.func.id](arg)
        raise ValueError(f"Unsupported function: {node.func.id}")

    def evaluate(self, expr):
        """Evaluates an expression safely."""
        try:
            parsed_expr = ast.parse(expr, mode="eval")
            return self.visit(parsed_expr.body)
        except Exception as e:
            return f"Error: {e}"


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
        print(f"Graphing Error: {e}")


def process_input(expr):
    """Automatically decides whether to evaluate or plot."""
    expr = expr.strip()

    # If input contains 'x', assume it's a function and plot it
    if "x" in expr:
        print(f"Detected function: {expr} → Plotting graph.")
        plot_function(expr, -10, 10)  # Default range
    else:
        # Otherwise, evaluate as a normal mathematical expression
        result = evaluate_expression(expr)
        print(f"Evaluated: {expr} = {result}")


if __name__ == "__main__":
    while True:
        expr = input("\nEnter an expression or function (or type 'exit' to quit): ")
        if expr.lower() == "exit":
            print("Exiting calculator...")
            break
        process_input(expr)
