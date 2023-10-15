import re

# Define Token Types
IDENTIFIER = 'IDENTIFIER'
NUMBER = 'NUMBER'
OPERATOR = 'OPERATOR'
OPEN_PARENT = 'OPEN_PARENT'
CLOSE_PARENT = 'CLOSE_PARENT'

# Tokenize Function
def tokenize(input_string):
    token_specification = [
        (IDENTIFIER, r'[a-zA-Z][a-zA-Z0-9]*'),   # Identifier (variable)
        (NUMBER, r'\d+'),                        # Integer constant
        (OPERATOR, r'[\+\-\*\/\=]'),             # Operators (+, -, *, /, =)
        (OPEN_PARENT, r'\('),                    # Opening parenthesis
        (CLOSE_PARENT, r'\)'),                   # Closing parenthesis
    ]

    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    tokens = []

    for line_number, line in enumerate(input_string.split('\n'), start=1):
        for match in re.finditer(tok_regex, line):
            for token_name, token_value in match.groupdict().items():
                if token_value:
                    tokens.append(Token(token_name, token_value, line_number))
                    break

    return tokens

# Token Class
class Token:
    def __init__(self, name, value, line_number):
        self.name = name
        self.value = value
        self.line_number = line_number

    def __str__(self):
        return f"<{self.name}, {self.value}>"

# Recursive Descent Parser
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.current_index = 0
        self.parse_tree = []

    def get_next_token(self):
        if self.current_index < len(self.tokens):
            self.current_token = self.tokens[self.current_index]
            self.current_index += 1
        else:
            self.current_token = Token('EOF', None, -1)  # Special EOF token

    def match(self, expected_token_type):
        if self.current_token and self.current_token.name == expected_token_type:
            self.get_next_token()
        else:
            raise ValueError("Error in parsing. Expected '{}' but found '{}'.".format(
                expected_token_type, self.current_token.value if self.current_token else 'EOF'))

    def parse(self, start_symbol):
        self.get_next_token()
        self.parse_tree.append(start_symbol)
        if start_symbol == 'E':
            self.parse_e()
        else:
            raise ValueError("Invalid start symbol for parsing.")

        if self.current_token.name == 'EOF':  # Check for EOF
            return True
        else:
            raise ValueError("Error in parsing. Unexpected token '{}'.".format(
                self.current_token.value))

    def parse_e(self):
        self.parse_tree.append('T')
        self.parse_t()
        self.parse_e_prime()

    def parse_e_prime(self):
        if self.current_token and self.current_token.name == 'OPERATOR' and self.current_token.value in ['+', '-']:
            self.parse_tree.append(self.current_token.value)
            self.match('OPERATOR')
            self.parse_tree.append('T')
            self.parse_t()
            self.parse_e_prime()

    def parse_t(self):
        self.parse_tree.append('F')
        self.parse_f()
        self.parse_t_prime()

    def parse_t_prime(self):
        if self.current_token and self.current_token.name == 'OPERATOR' and self.current_token.value in ['*', '/']:
            self.parse_tree.append(self.current_token.value)
            self.match('OPERATOR')
            self.parse_tree.append('F')
            self.parse_f()
            self.parse_t_prime()

    def parse_f(self):
        if self.current_token and self.current_token.name == 'OPEN_PAREN':
            self.parse_tree.append('(')
            self.match('OPEN_PAREN')
            self.parse_tree.append('E')
            self.parse_e()
            self.parse_tree.append(')')
            self.match('CLOSE_PAREN')
        elif self.current_token and self.current_token.name == 'IDENTIFIER':
            self.parse_tree.append(self.current_token.value)
            self.match('IDENTIFIER')
        elif self.current_token and self.current_token.name == 'NUMBER':
            self.parse_tree.append(self.current_token.value)
            self.match('NUMBER')
        else:
            raise ValueError("Error in parsing. Unexpected token '{}'.".format(
                self.current_token.value))

    def get_parse_tree(self):
        return self.parse_tree

# Print Tokens Function
def print_tokens(tokens):
    print("\nToken Lexemes:")
    lexemes = [token.value for token in tokens]
    print(", ".join(lexemes))

# Print Token Matrix Function
def print_token_matrix(token_matrix):
    print("\nSymbol Table:")
    for row in token_matrix:
        print(f"Lexeme: {row[0]}, Token Type: {row[1]}, Line Number: {row[2]}")

# Print Parse Tree Function
def print_parse_tree(parse_tree, level=0):
    if isinstance(parse_tree, list):
        print("  " * level + parse_tree[0])
        for subtree in parse_tree[1:]:
            print_parse_tree(subtree, level + 1)
    else:
        print("  " * level + str(parse_tree))

# Main Function
def main():
    file_name = 'input.txt'  # input strings file
    with open(file_name, 'r') as file:
        input_string = file.read()

    print("Input String:")
    print(input_string)

    tokens = tokenize(input_string)

    # Print Tokens
    print_tokens(tokens)

    # Token Matrix
    token_matrix = []
    for token in tokens:
        token_matrix.append([token.value, token.name, token.line_number])
    print_token_matrix(token_matrix)

    # Map lexemes into tokens and display
    print("\nMapped Tokens:")
    mapped_tokens = []
    current_id = 1
    for token in tokens:
        if token.name == IDENTIFIER:
            mapped_tokens.append(f"<id,{current_id}>")
            current_id += 1
        elif token.name == NUMBER:
            mapped_tokens.append(f"<num,{token.value}>")
        else:
            mapped_tokens.append(f"<op,{token.value}>")

    # Group mapped tokens with line numbers
    mapped_tokens_grouped = []
    current_line = 0
    for token, line_number in zip(mapped_tokens, [token.line_number for token in tokens]):
        if line_number != current_line:
            current_line = line_number
            mapped_tokens_grouped.append('\n')
        mapped_tokens_grouped.append(token)

    print(" ".join(mapped_tokens_grouped))

    # Top-Down Parsing and Acceptance Check
    parser = Parser(tokens)
    try:
        parser.parse('E')
        parse_tree = parser.get_parse_tree()

        # Print the parse tree to the terminal
        print("\nParse Tree:")
        print_parse_tree(parse_tree)
        print("Input string can be accepted.")
    except ValueError as e:
        print("Error:", e)
        print("Input string cannot be accepted.")

if __name__ == "__main__":
    main()
