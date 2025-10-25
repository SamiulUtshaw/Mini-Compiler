# codegen.py

class CodeGenerator:
    def __init__(self):
        self.assembly_code = []
        self.registers = ['R1', 'R2', 'R3', 'R4']
        self.reg_map = {}
        self.next_reg = 0

    def get_register(self, var):
        if var in self.reg_map:
            return self.reg_map[var]

        reg = self.registers[self.next_reg % len(self.registers)]
        self.next_reg += 1
        self.reg_map[var] = reg
        return reg

    def generate(self, intermediate_code):
        self.assembly_code = []
        self.assembly_code.append("; Assembly Code Generated")
        self.assembly_code.append("section .data")
        self.assembly_code.append("section .text")
        self.assembly_code.append("global _start")
        self.assembly_code.append("_start:")

        for instruction in intermediate_code:
            op = instruction['op']
            arg1 = instruction['arg1']
            arg2 = instruction['arg2']
            result = instruction['result']

            if op == '=':
                reg_src = self.get_register(arg1) if isinstance(arg1, str) and arg1.startswith('t') else None
                reg_dest = self.get_register(result)

                if reg_src:
                    self.assembly_code.append(f"    MOV {reg_dest}, {reg_src}")
                else:
                    self.assembly_code.append(f"    MOV {reg_dest}, {arg1}")

            elif op in ['+', '-', '*', '/', '%']:
                reg1 = self.get_register(arg1) if isinstance(arg1, str) else None
                reg2 = self.get_register(arg2) if isinstance(arg2, str) else None
                reg_result = self.get_register(result)

                op_map = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', '%': 'MOD'}

                if reg1 and reg2:
                    self.assembly_code.append(f"    {op_map[op]} {reg_result}, {reg1}, {reg2}")
                elif reg1:
                    self.assembly_code.append(f"    {op_map[op]} {reg_result}, {reg1}, {arg2}")
                elif reg2:
                    self.assembly_code.append(f"    {op_map[op]} {reg_result}, {arg1}, {reg2}")
                else:
                    self.assembly_code.append(f"    {op_map[op]} {reg_result}, {arg1}, {arg2}")

            elif op in ['<', '<=', '>', '>=', '==', '!=']:
                reg1 = self.get_register(arg1) if isinstance(arg1, str) else None
                reg2 = self.get_register(arg2) if isinstance(arg2, str) else None
                reg_result = self.get_register(result)

                val1 = reg1 if reg1 else arg1
                val2 = reg2 if reg2 else arg2

                self.assembly_code.append(f"    CMP {val1}, {val2}")
                self.assembly_code.append(f"    SET{op} {reg_result}")

            elif op == 'label':
                self.assembly_code.append(f"{arg1}:")

            elif op == 'goto':
                self.assembly_code.append(f"    JMP {arg1}")

            elif op == 'if_false':
                reg = self.get_register(arg1) if isinstance(arg1, str) else None
                val = reg if reg else arg1
                self.assembly_code.append(f"    CMP {val}, 0")
                self.assembly_code.append(f"    JE {arg2}")

            elif op == 'print':
                reg = self.get_register(arg1) if isinstance(arg1, str) else None
                val = reg if reg else arg1
                self.assembly_code.append(f"    PRINT {val}")

        self.assembly_code.append("    MOV EAX, 1")
        self.assembly_code.append("    INT 0x80")

        return self.assembly_code