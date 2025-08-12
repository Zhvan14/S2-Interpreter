import re
import sys

def evaluate_expression(expr_string, variables, last_input):
    expr_string = expr_string.strip()

    # Replace system input ((input))
    expr_string = expr_string.replace('((input))', str(last_input))

    # Replace variables in the expression string with their current values
    def var_replace(match):
        var_name = match.group(1)
        if var_name in variables:
            return str(variables[var_name])
        else:
            raise Exception(f"Undefined variable '{var_name}'")
    processed_expr = re.sub(r'\(([a-zA-Z_][a-zA-Z0-9_]*)\)', var_replace, expr_string)

    # String concatenation operator '++'
    if "++" in processed_expr:
        parts = [p.strip() for p in processed_expr.split("++")]
        return ''.join(parts)

    # Attempt math evaluation
    if not re.fullmatch(r'[0-9+\-*/().\s]+', processed_expr):
        raise Exception("Invalid characters or syntax in arithmetic expression.")
    try:
        result = eval(processed_expr, {"__builtins__": None}, {})
        if isinstance(result, (int, float)):
            return result
        else:
            raise Exception("Expression did not evaluate to a valid number.")
    except Exception as e:
        raise Exception(f"Could not evaluate expression: {str(e)}")

def display_help():
    print("""
S Language Commands:
  write <text>                Prints literal text.
  write (variable_name)       Prints the value of a variable.
  write ((input))             Prints last input value.
  write (<expression>)        Prints result of arithmetic or string expr.
                              Operators: +, -, *, /, ++ (concatenation)
  writeinput <prompt>         Prompts for user input.
  variable_name <value>       Assigns a literal value.
  variable_name ((input))     Assigns last input to variable.
  variable_name (<expr>)      Assigns expr result to variable.
  img "image_url"             Prints image URL (CLI only).
  $                          Comments after $ are ignored.
""")

def parse_line(line):
    # Remove comments
    line = line.split('$')[0].strip()
    if not line:
        return None

    # writeinput
    m = re.match(r'^writeinput\s+(.*)$', line)
    if m:
        return ('writeinput', m.group(1))

    # img
    m = re.match(r'^img\s+"([^"]+)"$', line)
    if m:
        return ('img', m.group(1))

    # write ((input))
    if re.match(r'^write\s+\(\(input\)\)$', line):
        return ('write_system_input',)

    # write (<expr/var>)
    m = re.match(r'^write\s+\((.+)\)$', line)
    if m:
        content = m.group(1).strip()
        if re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', content):
            return ('write_var', content)
        else:
            return ('write_expr', content)

    # write literal
    m = re.match(r'^write\s+(.*)$', line)
    if m:
        return ('write_literal', m.group(1))

    # var assign
    m = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s+(.*)$', line)
    if m:
        var, val = m.group(1), m.group(2).strip()
        expr_match = re.match(r'^\((.+)\)$', val)
        if val == '((input))':
            return ('var_assign_input', var)
        elif expr_match:
            return ('var_assign_expr', var, expr_match.group(1).strip())
        else:
            return ('var_assign_literal', var, val)
    return ('error', line)

def run_s_code(lines):
    variables = {}
    last_input = ""
    for idx, line in enumerate(lines, 1):
        parsed = parse_line(line)
        if not parsed:
            continue
        cmd = parsed[0]

        try:
            if cmd == 'writeinput':
                prompt = parsed[1]
                last_input = input(prompt + " ")
                
            elif cmd == 'img':
                url = parsed[1]
                print(f"[Image: {url}]")
            elif cmd == 'write_system_input':
                print(last_input)
            elif cmd == 'write_var':
                var = parsed[1]
                if var in variables:
                    print(variables[var])
                else:
                    print(f"Error: Variable '{var}' not found (Line {idx})")
            elif cmd == 'write_expr':
                expr = parsed[1]
                try:
                    result = evaluate_expression(expr, variables, last_input)
                    print(result)
                except Exception as e:
                    print(f"Error: {e} (Line {idx})")
            elif cmd == 'write_literal':
                val = parsed[1]
                def var_sub(match):
                    v = match.group(1)
                    return str(variables.get(v, f"(Error: Var '{v}' not found)"))
                print(re.sub(r'\(([a-zA-Z_][a-zA-Z0-9_]*)\)', var_sub, val))
            elif cmd == 'var_assign_input':
                var = parsed[1]
                variables[var] = last_input
            elif cmd == 'var_assign_expr':
                var, expr = parsed[1], parsed[2]
                try:
                    variables[var] = evaluate_expression(expr, variables, last_input)
                except Exception as e:
                    print(f"Error assigning to '{var}': {e} (Line {idx})")
            elif cmd == 'var_assign_literal':
                var, val = parsed[1], parsed[2]
                variables[var] = val
            elif cmd == 'error':
                print(f"Error on line {idx}: Invalid syntax or unrecognized command: \"{parsed[1]}\"")
        except Exception as e:
            print(f"Error on line {idx}: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="S2 Language Interpreter CLI")
    parser.add_argument('file', nargs='?', help="S2 program file (.s2) to run")
    parser.add_argument('--help-s2', action='store_true', help="Show S2 language help and exit")
    args = parser.parse_args()

    if args.help_s2:
        display_help()
        sys.exit(0)

    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                lines = f.read().splitlines()
        except Exception as e:
            print(f"Error opening file: {e}")
            sys.exit(1)
        run_s_code(lines)
    else:
        print("S2 Interpreter CLI (type 'exit' or Ctrl+C to quit, '--help-s2' for language help)\n")
        display_help()
        lines = []
        while True:
            try:
                line = input("> ")
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break
            if line.strip().lower() == "exit":
                print("Bye!")
                break
            lines.append(line)
            if line.strip() == "":
                run_s_code(lines)
                lines = []
