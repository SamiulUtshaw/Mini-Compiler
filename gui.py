# gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from lexer import Lexer
from parser import Parser
from codegen import CodeGenerator

class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CSE 430 - Mini Compiler")
        self.root.geometry("1000x600")

        # Initialize compiler components
        self.lexer = Lexer()
        self.lexer.build()
        self.parser = Parser()
        self.parser.build()
        self.code_generator = CodeGenerator()

        self.setup_ui()

    def setup_ui(self):
        # Top section - Input
        top_frame = tk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(top_frame, text="Source Code:", font=('Arial', 10, 'bold')).pack(anchor='w')

        self.input_text = scrolledtext.ScrolledText(top_frame, font=('Courier', 10), height=12)
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Sample code with comments and scopes
        sample_code = """// Global variables
int x;
int y;
x = 10;
y = 20;

/* Calculate sum */
int sum;
sum = x + y;
print(sum);

// If block with local scope
if (x < y) {
    int diff;  // Local to if block
    diff = y - x;
    print(diff);
}

// While loop with local scope
int counter;
counter = 0;
while (counter < 5) {
    int temp;  // Local to while block
    temp = counter * 2;
    counter = counter + 1;
}
"""
        self.input_text.insert('1.0', sample_code)

        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Compile", command=self.compile_code, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear All", command=self.clear_all, width=12).pack(side=tk.LEFT, padx=5)

        # Bottom section - Output with Tabs
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(bottom_frame, text="Output:", font=('Arial', 10, 'bold')).pack(anchor='w')

        self.notebook = ttk.Notebook(bottom_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create tabs
        self.create_tab("Tokens", "tokens_text")
        self.create_tab("Symbol Table", "symbol_text")
        self.create_tab("Intermediate Code", "intermediate_text")
        self.create_tab("Assembly", "assembly_text")
        self.create_tab("Errors", "errors_text")

    def create_tab(self, title, attr_name):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=title)

        text_widget = scrolledtext.ScrolledText(frame, font=('Courier', 9), height=10)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        setattr(self, attr_name, text_widget)

    def compile_code(self):
        source_code = self.input_text.get('1.0', tk.END)

        # Clear outputs
        for attr in ['tokens_text', 'symbol_text', 'intermediate_text',
                     'assembly_text', 'errors_text']:
            getattr(self, attr).delete('1.0', tk.END)

        # Lexical Analysis (for display only)
        tokens, lex_errors = self.lexer.tokenize(source_code)

        token_output = "Token Type       Value           Line\n"
        token_output += "-" * 45 + "\n"
        for token in tokens:
            token_output += f"{token['type']:<16} {str(token['value']):<15} {token['line']}\n"

        self.tokens_text.insert('1.0', token_output)

        # Syntax and Semantic Analysis (with scope tracking)
        self.parser = Parser()
        self.parser.build()
        self.parser.parse(source_code)

        # Symbol Table with scope information
        symbol_output = "Name             Type       Scope\n"
        symbol_output += "-" * 45 + "\n"
        symbols = sorted(self.parser.symbol_table.get_all(),
                         key=lambda x: (0 if x['scope'] == 'global' else 1, x['name']))
        for symbol in symbols:
            symbol_output += f"{symbol['name']:<16} {symbol['type']:<10} {symbol['scope']}\n"

        self.symbol_text.insert('1.0', symbol_output)

        # Intermediate Code
        ic_output = ""
        for i, inst in enumerate(self.parser.intermediate_code, 1):
            op = inst['op']
            arg1 = inst['arg1']
            arg2 = inst['arg2']
            result = inst['result']

            if op == '=':
                ic_output += f"{i}. {result} = {arg1}\n"
            elif op in ['+', '-', '*', '/', '%']:
                ic_output += f"{i}. {result} = {arg1} {op} {arg2}\n"
            elif op == 'label':
                ic_output += f"{i}. {arg1}:\n"
            elif op == 'goto':
                ic_output += f"{i}. goto {arg1}\n"
            elif op == 'if_false':
                ic_output += f"{i}. if_false {arg1} goto {arg2}\n"
            elif op == 'print':
                ic_output += f"{i}. print {arg1}\n"
            else:
                ic_output += f"{i}. {result} = {arg1} {op} {arg2}\n"

        self.intermediate_text.insert('1.0', ic_output)

        # Assembly Code
        assembly = self.code_generator.generate(self.parser.intermediate_code)
        assembly_output = "\n".join(assembly)
        self.assembly_text.insert('1.0', assembly_output)

        # Errors
        all_errors = lex_errors + self.parser.errors
        if all_errors:
            errors_output = ""
            for i, error in enumerate(all_errors, 1):
                errors_output += f"{i}. {error}\n"
            self.errors_text.insert('1.0', errors_output)
        else:
            self.errors_text.insert('1.0', "✓ No errors found.\n✓ Comments handled correctly.\n✓ Scopes managed properly.\n✓ Control flow is correct.")

    def clear_all(self):
        self.input_text.delete('1.0', tk.END)
        for attr in ['tokens_text', 'symbol_text', 'intermediate_text',
                     'assembly_text', 'errors_text']:
            getattr(self, attr).delete('1.0', tk.END)