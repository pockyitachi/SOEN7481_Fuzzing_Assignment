import ast
import operator


def safe_eval(expr):
    try:
        # Define allowed operators, including modulo
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod  # Add modulo support
        }

        # Parse expression
        node = ast.parse(expr, mode='eval')

        # Evaluate the expression safely
        def eval_node(node):
            if isinstance(node, ast.Expression):
                return eval_node(node.body)
            elif isinstance(node, ast.BinOp):
                left = eval_node(node.left)
                right = eval_node(node.right)
                return operators[type(node.op)](left, right)
            elif isinstance(node, ast.Constant):  # Use ast.Constant instead of ast.Num
                return node.value
            else:
                raise ValueError(f"Unsupported operation: {type(node)}")

        return eval_node(node.body)

    except Exception as e:
        return f"Invalid Expression, Error: {e}"


if __name__ == "__main__":
    expr = input("Enter an expression: ")
    print(safe_eval(expr))