import re

from utils.settings import *

class Expression:
    def __init__(self, expression: str):
        self.expression = expression
        print(f"Original Expression: {self.expression}\n")
        self.__match_symbols()
    
    def __match_symbols(self):
        for symbol, word in SYMBOL_MAP.items():
            self.expression = self.expression.replace(symbol, f" {word} ")
    
    def __space_atoms(self):
        return self.expression.replace("(", " ( ").replace(")", " ) ").split()
    

    def __check_formula(tokens, index: int):
        if index >= len(tokens):
            return False, index

        token = tokens[index]

        if re.fullmatch(ATOM_PATTERN, token):
            return True, index + 1

        if token == "(":
            index += 1
            if index >= len(tokens):
                return False, index

            sub_token = tokens[index]

            if sub_token in UNARY_OPS:
                ok, j = Expression.__check_formula(tokens, index + 1)
                if not ok:
                    return False, j
                if j >= len(tokens) or tokens[j] != ")":
                    return False, j
                return True, j + 1
            else:
                ok1, j1 = Expression.__check_formula(tokens, index)
                if not ok1:
                    return False, j1
                if j1 >= len(tokens):
                    return False, j1

                op = tokens[j1]
                if op in BINARY_OPS:
                    ok2, j2 = Expression.__check_formula(tokens, j1 + 1)
                    if not ok2:
                        return False, j2
                    if j2 >= len(tokens) or tokens[j2] != ")":
                        return False, j2
                    return True, j2 + 1
                elif op == ")":
                    return True, j1 + 1
                else:
                    return False, j1

        return False, index

    def __check_full(tokens, index=0):
        ok, j = Expression.__check_formula(tokens, index)
        if not ok:
            return False, j
        
        while j < len(tokens):
            if tokens[j] not in BINARY_OPS:
                break
            operation = tokens[j]
            ok2, j2 = Expression.__check_formula(tokens, j + 1)
            if not ok2:
                return False, j2
            j = j2
        
        return True, j
