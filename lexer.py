# lexer.py
import re
import ply.lex as lex

class Lexer:
    # Reserved keywords
    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'for': 'FOR',
        'int': 'INT',
        'float': 'FLOAT',
        'return': 'RETURN',
        'print': 'PRINT',
    }

    # Token list
    tokens = [
        'ID', 'NUMBER', 'FLOAT_NUM',
        'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MODULO',
        'ASSIGN', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
        'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'SEMICOLON', 'COMMA',
    ] + list(reserved.values())

    # Token rules
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_MODULO = r'%'
    t_ASSIGN = r'='
    t_EQ = r'=='
    t_NE = r'!='
    t_LT = r'<'
    t_LE = r'<='
    t_GT = r'>'
    t_GE = r'>='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_SEMICOLON = r';'
    t_COMMA = r','

    # Ignored characters (spaces and tabs)
    t_ignore = ' \t'

    # Comment handling - MUST come before DIVIDE
    def t_COMMENT_SINGLE(self, t):
        r'//.*'
        pass  # Ignore single-line comments

    def t_COMMENT_MULTI(self, t):
        r'/\*(.|\n)*?\*/'
        t.lexer.lineno += t.value.count('\n')
        pass  # Ignore multi-line comments

    # DIVIDE token must come AFTER comment rules
    def t_DIVIDE(self, t):
        r'/'
        return t

    def t_FLOAT_NUM(self, t):
        r'\d+\.\d+'
        t.value = float(t.value)
        return t

    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        self.errors.append(f"Illegal character '{t.value[0]}' at line {t.lineno}")
        t.lexer.skip(1)

    def __init__(self):
        self.lexer = None
        self.tokens_list = []
        self.errors = []

    def build(self):
        self.lexer = lex.lex(module=self)

    def tokenize(self, data):
        self.tokens_list = []
        self.errors = []
        self.lexer.input(data)

        while True:
            tok = self.lexer.token()
            if not tok:
                break
            self.tokens_list.append({
                'type': tok.type,
                'value': tok.value,
                'line': tok.lineno,
                'position': tok.lexpos
            })

        return self.tokens_list, self.errors


class ScopeTrackingLexer(Lexer):
    """Extended lexer that tracks scope changes during tokenization"""

    def __init__(self, symbol_table):
        super().__init__()
        self.symbol_table = symbol_table
        self.original_token = None

    def build(self):
        super().build()
        # Wrap the token method to track scopes
        self.original_token = self.lexer.token
        self.lexer.token = self.token_with_scope_tracking

    def token_with_scope_tracking(self):
        tok = self.original_token()
        if tok:
            if tok.type == 'LBRACE':
                self.symbol_table.enter_scope()
            elif tok.type == 'RBRACE':
                self.symbol_table.exit_scope()
        return tok