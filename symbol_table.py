# symbol_table.py

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.scope_stack = ['global']
        self.scope_counter = 0

    def enter_scope(self, scope_name=None):
        """Enter a new scope (e.g., entering an if block or while loop)"""
        if scope_name is None:
            self.scope_counter += 1
            scope_name = f"scope_{self.scope_counter}"
        self.scope_stack.append(scope_name)
        return scope_name

    def exit_scope(self):
        """Exit the current scope"""
        if len(self.scope_stack) > 1:
            return self.scope_stack.pop()
        return None

    def current_scope(self):
        """Get the current scope"""
        return self.scope_stack[-1]

    def insert(self, name, symbol_type, value=None, scope=None):
        """Insert a symbol into the table"""
        if scope is None:
            scope = self.current_scope()

        # Check if variable already exists in current scope
        key = f"{scope}:{name}"
        if key in self.symbols:
            return False  # Already declared in this scope

        self.symbols[key] = {
            'name': name,
            'type': symbol_type,
            'value': value,
            'scope': scope
        }
        return True

    def lookup(self, name):
        """Lookup a symbol, searching from innermost to outermost scope"""
        for scope in reversed(self.scope_stack):
            key = f"{scope}:{name}"
            if key in self.symbols:
                return self.symbols[key]
        return None

    def lookup_current_scope(self, name):
        """Lookup a symbol only in the current scope"""
        scope = self.current_scope()
        key = f"{scope}:{name}"
        return self.symbols.get(key)

    def get_all(self):
        """Get all symbols"""
        return list(self.symbols.values())