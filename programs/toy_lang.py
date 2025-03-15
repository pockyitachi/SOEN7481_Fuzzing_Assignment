import random
import string
import matplotlib.pyplot as plt
import numpy as np

# ========================
# 1. GLOBAL COVERAGE
# ========================
coverage_map = {}  # branch_name -> 1 (binary coverage)


def record_coverage(branch):
    """
    Mark a given branch as covered (1).
    Once covered, it stays covered for this run.
    """
    global coverage_map
    coverage_map[branch] = 1


# ========================
# 2. LEXER
# ========================
class Token:
    def __init__(self, ttype, value):
        self.ttype = ttype
        self.value = value

    def __repr__(self):
        return f"Token({self.ttype}, {self.value})"


def tokenize(code):
    """
    Convert a string of code into a list of tokens.
    """
    record_coverage("lexer_start")
    tokens = []
    i = 0
    while i < len(code):
        c = code[i]

        if c.isspace():
            i += 1
            continue

        if c.isalpha():
            # Collect identifier or keyword
            start = i
            while i < len(code) and (code[i].isalnum() or code[i] == '_'):
                i += 1
            ident = code[start:i]
            if ident == "print":
                tokens.append(Token("PRINT", ident))
                record_coverage("lexer_print_kw")
            else:
                tokens.append(Token("IDENT", ident))
                record_coverage("lexer_ident")
            continue

        if c.isdigit():
            # Collect number
            start = i
            while i < len(code) and code[i].isdigit():
                i += 1
            num_str = code[start:i]
            tokens.append(Token("NUMBER", int(num_str)))
            record_coverage("lexer_number")
            continue

        if c in "+-*/=();":
            # Single-character tokens
            if c == '+':
                tokens.append(Token("PLUS", c))
                record_coverage("lexer_plus")
            elif c == '-':
                tokens.append(Token("MINUS", c))
                record_coverage("lexer_minus")
            elif c == '*':
                tokens.append(Token("STAR", c))
                record_coverage("lexer_star")
            elif c == '/':
                tokens.append(Token("SLASH", c))
                record_coverage("lexer_slash")
            elif c == '=':
                tokens.append(Token("EQUALS", c))
                record_coverage("lexer_equals")
            elif c == '(':
                tokens.append(Token("LPAREN", c))
                record_coverage("lexer_lparen")
            elif c == ')':
                tokens.append(Token("RPAREN", c))
                record_coverage("lexer_rparen")
            elif c == ';':
                tokens.append(Token("SEMI", c))
                record_coverage("lexer_semi")
            i += 1
            continue

        # If we reach here, it's an unknown symbol
        record_coverage("lexer_unknown_symbol")
        raise ValueError(f"Unknown symbol '{c}' at position {i}")

    record_coverage("lexer_end")
    return tokens


# ========================
# 3. PARSER (Recursive-Descent)
# ========================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token("EOF", None)

    def advance(self):
        self.pos += 1

    def parse_program(self):
        """
        program -> statement+
        """
        record_coverage("parse_program_start")
        statements = []
        while self.current_token().ttype != "EOF":
            stmt = self.parse_statement()
            statements.append(stmt)
        record_coverage("parse_program_end")
        return ("PROGRAM", statements)

    def parse_statement(self):
        """
        statement -> assign_stmt | print_stmt
        """
        tok = self.current_token()
        if tok.ttype == "IDENT":
            record_coverage("parse_stmt_assign")
            return self.parse_assign_stmt()
        elif tok.ttype == "PRINT":
            record_coverage("parse_stmt_print")
            return self.parse_print_stmt()
        else:
            record_coverage("parse_stmt_error")
            raise ValueError(f"Unexpected token {tok}")

    def parse_assign_stmt(self):
        """
        assign_stmt -> IDENT '=' expr ';'
        """
        ident_token = self.current_token()
        self.advance()  # consume IDENT
        eq_token = self.current_token()
        if eq_token.ttype != "EQUALS":
            record_coverage("parse_assign_no_equals")
            raise ValueError("Expected '=' in assignment.")
        self.advance()  # consume '='
        expr_node = self.parse_expr()
        semi_token = self.current_token()
        if semi_token.ttype != "SEMI":
            record_coverage("parse_assign_no_semi")
            raise ValueError("Expected ';' after assignment.")
        self.advance()  # consume ';'
        return ("ASSIGN", ident_token.value, expr_node)

    def parse_print_stmt(self):
        """
        print_stmt -> 'print' '(' expr ')' ';'
        """
        self.advance()  # consume 'print'
        lp = self.current_token()
        if lp.ttype != "LPAREN":
            record_coverage("parse_print_no_lparen")
            raise ValueError("Expected '(' after 'print'.")
        self.advance()  # consume '('
        expr_node = self.parse_expr()
        rp = self.current_token()
        if rp.ttype != "RPAREN":
            record_coverage("parse_print_no_rparen")
            raise ValueError("Expected ')' after expression in print.")
        self.advance()  # consume ')'
        semi = self.current_token()
        if semi.ttype != "SEMI":
            record_coverage("parse_print_no_semi")
            raise ValueError("Expected ';' after print statement.")
        self.advance()  # consume ';'
        return ("PRINT", expr_node)

    def parse_expr(self):
        """
        expr -> term (('+' | '-') term)*
        """
        left = self.parse_term()
        while self.current_token().ttype in ("PLUS", "MINUS"):
            op = self.current_token()
            self.advance()
            right = self.parse_term()
            left = ("BINOP", op.ttype, left, right)
        return left

    def parse_term(self):
        """
        term -> factor (('*' | '/') factor)*
        """
        left = self.parse_factor()
        while self.current_token().ttype in ("STAR", "SLASH"):
            op = self.current_token()
            self.advance()
            right = self.parse_factor()
            left = ("BINOP", op.ttype, left, right)
        return left

    def parse_factor(self):
        """
        factor -> NUMBER | IDENT | '(' expr ')'
        """
        tok = self.current_token()
        if tok.ttype == "NUMBER":
            self.advance()
            return ("NUMBER", tok.value)
        elif tok.ttype == "IDENT":
            self.advance()
            return ("IDENT", tok.value)
        elif tok.ttype == "LPAREN":
            self.advance()
            inner_expr = self.parse_expr()
            rp = self.current_token()
            if rp.ttype != "RPAREN":
                record_coverage("parse_factor_no_rparen")
                raise ValueError("Expected ')' after expression.")
            self.advance()
            return inner_expr
        else:
            record_coverage("parse_factor_error")
            raise ValueError(f"Unexpected token in factor: {tok}")


# ========================
# 4. INTERPRETER
# ========================
class Interpreter:
    def __init__(self):
        self.variables = {}  # name -> int

    def eval_program(self, node):
        # node is ("PROGRAM", [stmt1, stmt2, ...])
        for stmt in node[1]:
            self.eval_statement(stmt)

    def eval_statement(self, stmt):
        stype = stmt[0]
        if stype == "ASSIGN":
            record_coverage("interp_assign")
            # stmt = ("ASSIGN", varname, expr)
            varname = stmt[1]
            expr_node = stmt[2]
            value = self.eval_expr(expr_node)
            self.variables[varname] = value
        elif stype == "PRINT":
            record_coverage("interp_print")
            # stmt = ("PRINT", expr_node)
            expr_node = stmt[1]
            value = self.eval_expr(expr_node)
            print(value)
        else:
            record_coverage("interp_unknown_stmt")
            raise ValueError(f"Unknown statement type: {stype}")

    def eval_expr(self, expr):
        etype = expr[0]
        if etype == "NUMBER":
            return expr[1]
        elif etype == "IDENT":
            varname = expr[1]
            if varname not in self.variables:
                record_coverage("interp_undefined_var")
                raise ValueError(f"Undefined variable '{varname}'")
            return self.variables[varname]
        elif etype == "BINOP":
            record_coverage("interp_binop")
            # expr = ("BINOP", op, left, right)
            op = expr[1]
            left_val = self.eval_expr(expr[2])
            right_val = self.eval_expr(expr[3])
            if op == "PLUS":
                return left_val + right_val
            elif op == "MINUS":
                return left_val - right_val
            elif op == "STAR":
                return left_val * right_val
            elif op == "SLASH":
                if right_val == 0:
                    record_coverage("interp_div_zero")
                    raise ValueError("Division by zero")
                return left_val // right_val
            else:
                record_coverage("interp_unknown_op")
                raise ValueError(f"Unknown operator {op}")
        else:
            record_coverage("interp_unknown_expr")
            raise ValueError(f"Unknown expression type {etype}")


# ========================
# 5. FUZZING
# ========================
def random_code_string(max_len=50):
    """
    Generates a random string of up to max_len characters.
    May contain random letters, digits, punctuation, etc.
    """
    length = random.randint(0, max_len)
    # We'll allow newline and a subset of punctuation
    chars = string.ascii_letters + string.digits + "+-*/=(); \n"
    return ''.join(random.choice(chars) for _ in range(length))


def parse_and_run(code):
    """
    A helper that lexes, parses, and interprets code in one shot.
    """
    tokens = tokenize(code)
    parser = Parser(tokens)
    program_ast = parser.parse_program()
    interp = Interpreter()
    interp.eval_program(program_ast)


def pure_random_fuzzing(iterations=500):
    """
    Performs pure random fuzzing on the toy language interpreter.
    Returns a list of coverage counts (len of coverage_map) after each iteration.
    """
    global coverage_map
    coverage_map = {}
    coverage_history = []
    for i in range(iterations):
        code = random_code_string(max_len=50)
        try:
            parse_and_run(code)
        except Exception:
            record_coverage("fuzz_exception")
        coverage_history.append(len(coverage_map))
    return coverage_history


def mutate_string(s):
    """
    Mutates a string by insertion, deletion, or replacement.
    """
    if not s:
        return random_code_string(10)
    mutation_type = random.choice(["insert", "delete", "replace"])
    pos = random.randint(0, len(s) - 1)
    chars = string.ascii_letters + string.digits + "+-*/=(); \n"
    if mutation_type == "insert":
        return s[:pos] + random.choice(chars) + s[pos:]
    elif mutation_type == "delete":
        return s[:pos] + s[pos + 1:]
    else:  # replace
        return s[:pos] + random.choice(chars) + s[pos + 1:]


def coverage_guided_fuzzing(iterations=500):
    """
    Performs coverage-guided fuzzing on the toy language interpreter.
    Returns a list of coverage counts (len of coverage_map) over iterations.
    """
    global coverage_map
    coverage_map = {}
    coverage_history = []

    # Seed with some small valid or semi-valid programs
    seeds = [
        "x=1;print(x);",
        "x=2;y=3;print(x+y);",
        "print(1+2*3);",
        "abc=123;print(abc);"
    ]
    covered_branches = set()

    for i in range(iterations):
        seed = random.choice(seeds)
        mutated = mutate_string(seed)

        # Temporarily track coverage for this iteration
        temp_map = {}
        saved_map = coverage_map
        coverage_map = temp_map

        try:
            parse_and_run(mutated)
        except Exception:
            record_coverage("fuzz_exception")

        # Find newly covered branches
        new_branches = set(temp_map.keys()) - covered_branches
        if new_branches:
            seeds.append(mutated)
            covered_branches.update(new_branches)

        # Merge the temporary coverage into the main coverage map (binary)
        for br in temp_map:
            saved_map[br] = 1

        coverage_map = saved_map
        coverage_history.append(len(coverage_map))

    return coverage_history


# ========================
# 6. PLOT COVERAGE
# ========================
def plot_coverage_evolution(coverage_random, coverage_guided):
    """
    Plots coverage (number of covered branches) over iterations.
    """
    plt.figure(figsize=(8, 5))
    plt.plot(coverage_random, label="Pure Random", color="blue")
    plt.plot(coverage_guided, label="Coverage Guided", color="orange")
    plt.xlabel("Iteration")
    plt.ylabel("Number of Covered Branches")
    plt.title("Toy Language Interpreter: Fuzzing Coverage Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ========================
# 7. MAIN
# ========================
def main():
    # Quick demonstration of the interpreter on a small code sample
    demo_code = "x=2; y=3; print(x*y);"
    print("=== Demo Code ===")
    print(demo_code)
    try:
        parse_and_run(demo_code)
    except Exception as e:
        print("Error:", e)

    # Run fuzzing
    print("\n=== Running Pure Random Fuzzing ===")
    coverage_history_random = pure_random_fuzzing(iterations=300)
    print("Final coverage with Pure Random:", coverage_history_random[-1])

    print("\n=== Running Coverage-Guided Fuzzing ===")
    coverage_history_guided = coverage_guided_fuzzing(iterations=300)
    print("Final coverage with Coverage-Guided:", coverage_history_guided[-1])

    # Plot
    print("\n=== Plotting Coverage Evolution ===")
    plot_coverage_evolution(coverage_history_random, coverage_history_guided)


if __name__ == "__main__":
    main()
