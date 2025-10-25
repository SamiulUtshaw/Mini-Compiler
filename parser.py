# parser.py
import ply.yacc as yacc

from lexer import Lexer, ScopeTrackingLexer
from symbol_table import SymbolTable

class Parser:
    tokens = Lexer.tokens

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.intermediate_code = []
        self.temp_count = 0
        self.label_count = 0
        self.errors = []
        self.parse_tree = []

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, op, arg1=None, arg2=None, result=None):
        code = {'op': op, 'arg1': arg1, 'arg2': arg2, 'result': result}
        self.intermediate_code.append(code)
        return result

    def backpatch(self, code_list, label):
        """Backpatch a list of instructions with a label"""
        for code in code_list:
            if code['arg2'] == 'BACKPATCH':
                code['arg2'] = label

    # Grammar rules
    def p_program(self, p):
        '''program : statement_list'''
        p[0] = ('program', p[1])
        self.parse_tree.append(p[0])

    def p_statement_list(self, p):
        '''statement_list : statement_list statement
                         | statement'''
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_statement(self, p):
        '''statement : declaration
                    | assignment
                    | print_statement
                    | if_statement
                    | while_statement
                    | block'''
        p[0] = p[1]

    def p_declaration(self, p):
        '''declaration : type ID SEMICOLON
                      | type ID ASSIGN expression SEMICOLON'''
        var_type = p[1]
        var_name = p[2]

        # Check if variable already declared in current scope
        if self.symbol_table.lookup_current_scope(var_name):
            self.errors.append(f"Variable '{var_name}' already declared in current scope")
        else:
            if len(p) == 4:
                self.symbol_table.insert(var_name, var_type)
                p[0] = ('declaration', var_type, var_name)
            else:
                value = p[4]
                self.symbol_table.insert(var_name, var_type, value)
                self.emit('=', value, None, var_name)
                p[0] = ('declaration_init', var_type, var_name, value)

    def p_type(self, p):
        '''type : INT
               | FLOAT'''
        p[0] = p[1]

    def p_assignment(self, p):
        '''assignment : ID ASSIGN expression SEMICOLON'''
        var_name = p[1]
        expr = p[3]

        if not self.symbol_table.lookup(var_name):
            self.errors.append(f"Variable '{var_name}' not declared")

        self.emit('=', expr, None, var_name)
        p[0] = ('assignment', var_name, expr)

    def p_print_statement(self, p):
        '''print_statement : PRINT LPAREN expression RPAREN SEMICOLON'''
        self.emit('print', p[3], None, None)
        p[0] = ('print', p[3])

    def p_if_statement(self, p):
        '''if_statement : IF LPAREN condition RPAREN m_label block n_label
                       | IF LPAREN condition RPAREN m_label block n_label ELSE m_label block'''
        # Basic handling of labels; labels are created by m_label and n_label helpers.
        if len(p) == 8:  # Simple if
            false_label = p[5]
            self.emit('label', false_label, None, None)
        else:  # if-else (len == 11)
            false_label = p[5]
            end_label = p[9]
            self.emit('label', false_label, None, None)
            self.emit('label', end_label, None, None)

        p[0] = ('if', p[3])

    def p_while_statement(self, p):
        '''while_statement : WHILE m_label LPAREN condition RPAREN m_label block n_label'''
        start_label = p[2]
        exit_label = p[6]

        # Jump back to start
        self.emit('goto', start_label, None, None)
        # Exit label
        self.emit('label', exit_label, None, None)

        p[0] = ('while', p[4])

    def p_m_label(self, p):
        '''m_label : '''
        # Create a new label and emit it
        label = self.new_label()
        self.emit('label', label, None, None)
        p[0] = label

    def p_n_label(self, p):
        '''n_label : '''
        # Create a label for later use (for goto)
        label = self.new_label()
        # Don't emit yet, will be used for jumps
        self.emit('goto', label, None, None)
        p[0] = label

    def p_block(self, p):
        '''block : LBRACE statement_list RBRACE'''
        p[0] = ('block', p[2])

    def p_condition(self, p):
        '''condition : expression relop expression'''
        temp = self.new_temp()
        self.emit(p[2], p[1], p[3], temp)

        # Emit conditional jump right after condition
        false_label = self.new_label()
        self.emit('if_false', temp, false_label, None)

        p[0] = (temp, false_label)

    def p_relop(self, p):
        '''relop : LT
                | LE
                | GT
                | GE
                | EQ
                | NE'''
        p[0] = p[1]

    def p_expression_binop(self, p):
        '''expression : expression PLUS term
                     | expression MINUS term'''
        temp = self.new_temp()
        self.emit(p[2], p[1], p[3], temp)
        p[0] = temp

    def p_expression_term(self, p):
        '''expression : term'''
        p[0] = p[1]

    def p_term_binop(self, p):
        '''term : term TIMES factor
               | term DIVIDE factor
               | term MODULO factor'''
        temp = self.new_temp()
        self.emit(p[2], p[1], p[3], temp)
        p[0] = temp

    def p_term_factor(self, p):
        '''term : factor'''
        p[0] = p[1]

    def p_factor_number(self, p):
        '''factor : NUMBER
                 | FLOAT_NUM'''
        p[0] = p[1]

    def p_factor_id(self, p):
        '''factor : ID'''
        if not self.symbol_table.lookup(p[1]):
            self.errors.append(f"Variable '{p[1]}' not declared")
        p[0] = p[1]

    def p_factor_paren(self, p):
        '''factor : LPAREN expression RPAREN'''
        p[0] = p[2]

    def p_error(self, p):
        if p:
            self.errors.append(f"Syntax error at '{p.value}' (line {p.lineno})")
        else:
            self.errors.append("Syntax error at EOF")

    def build(self):
        self.parser = yacc.yacc(module=self)

    def parse(self, data):
        self.intermediate_code = []
        self.temp_count = 0
        self.label_count = 0
        self.errors = []
        self.parse_tree = []

        # Create a custom lexer that tracks scopes
        lexer = ScopeTrackingLexer(self.symbol_table)
        lexer.build()

        result = self.parser.parse(data, lexer=lexer.lexer)
        return result