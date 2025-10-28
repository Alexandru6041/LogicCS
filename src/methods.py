import re

from src.tree import Node
from src.expression import Expression
from utils.settings import (
    ATOM_PATTERN,
    BINARY_OPS,
    UNARY_OPS
)


class Expression_Methods(Expression):
    def is_wppf(self) -> tuple[bool, int]:
        tokens = self._Expression__space_atoms()
        sol, pos = Expression._Expression__check_full(tokens)
        is_valid = sol and pos == len(tokens)
        
        if is_valid:
            stripped = self.expression.strip()
        
            if stripped.startswith('(') and stripped.endswith(')'):
                inner = stripped[1:-1]
        
                if inner.startswith('(') and inner.endswith(')'):
                    inner_inner = inner[1:-1]
        
                    if Expression_Methods(inner_inner).is_wppf()[0]:
                        return False, -1    
        return is_valid, pos - 1
    
    def get_variables(self) -> set:
        tokens = self._Expression__space_atoms()
        return {token for token in tokens if re.fullmatch(ATOM_PATTERN, token)}
    
    def __parse_formula_tree(tokens, index):
        if index >= len(tokens):
            return None, index

        token = tokens[index]

        if re.fullmatch(ATOM_PATTERN, token):
            node = Node(token)
            return node, index + 1

        if token == "(":
            index += 1
            
            if index >= len(tokens):
                return None, index

            sub_token = tokens[index]

            if sub_token in UNARY_OPS:
                sub_node, j = Expression_Methods.__parse_formula_tree(tokens, index + 1)
                
                if sub_node is None:
                    return None, j
                
                if j >= len(tokens) or tokens[j] != ")":
                    return None, j
                
                node = Node(sub_token, [sub_node])
                print(f"Created unary node for '{sub_token}' with child '{sub_node.value}'")
                node.print_tree()
                print("\n")
                return node, j + 1
            
            else:
                left, j1 = Expression_Methods.__parse_formula_tree(tokens, index)
                
                if left is None:
                    return None, j1
                
                if j1 >= len(tokens):
                    return None, j1

                op = tokens[j1]
                
                if op in BINARY_OPS:
                    right, j2 = Expression_Methods.__parse_formula_tree(tokens, j1 + 1)
                
                    if right is None:
                        return None, j2
                
                    if j2 >= len(tokens) or tokens[j2] != ")":
                        return None, j2
                
                    node = Node(op, [left, right])
                    print(f"Created binary node for: '{op}' with children '{left.value}' and '{right.value}'")
                    node.print_tree()
                    print("\n") 
                    return node, j2 + 1
                
                elif op == ")":
                    print(f"Found closing parenthesis, returning left subformula '{left.value}'")
                    left.print_tree()
                    print()
                    return left, j1 + 1
                else:
                    return None, j1

        return None, index

    def __parse_full_tree(tokens, index=0):
        root, j = Expression_Methods.__parse_formula_tree(tokens, index)
        
        if root is None:
            return None, j

        current = root
        
        while j < len(tokens):
            if tokens[j] not in BINARY_OPS:
                break
            operation = tokens[j]
            right, j2 = Expression_Methods.__parse_formula_tree(tokens, j + 1)
        
            if right is None:
                return None, j2
        
            new_node = Node(operation, [current, right])
            print(f"Created new root node for '{operation}' with left '{current.value}' and right '{right.value}'")
            new_node.print_tree()
            print("\n")
            current = new_node
            j = j2

        return current, j
    
    def build_tree(self):
        tokens = self._Expression__space_atoms()
        root, pos = Expression_Methods._Expression_Methods__parse_full_tree(tokens)
        if root and pos == len(tokens):
            return root
        return None
    
    def analyze_relaxed_syntax(self):
        
        original_expr = self.expression.strip()
        tokens = self._Expression__space_atoms()
        print(f"Tokens: {tokens}")
        print("\n")
        
        
        precedence = {'not': 4, 'and': 3, 'or': 2, 'implies': 1, 'equivalent': 0}
        
        def parse_expression(min_prec=0):
            nonlocal index
            left = parse_primary()
            
            if left is None:
                return None
            
            while index < len(tokens) and tokens[index] in BINARY_OPS and precedence.get(tokens[index], -1) >= min_prec:
                op = tokens[index]
                index += 1
                right = parse_expression(precedence[op])
                if right is None:
                    return None
                left = Node(op, [left, right])
                # print(f"Created node for '{op}' with left '{left.children[0].value}' and right '{left.children[1].value}'.")
            
            return left
        
        def parse_primary():
            nonlocal index
            
            if index >= len(tokens):
                print("[*]Error: Unexpected end of tokens in primary.")
                return None
            
            token = tokens[index]
            
            if re.fullmatch(ATOM_PATTERN, token):
                index += 1
                return Node(token)
            elif token == "(":
                index += 1
                expr = parse_expression()
            
                if expr is None or index >= len(tokens) or tokens[index] != ")":
                    print("[*]Error: Mismatched parentheses.")
                    return None
                index += 1
                # print("Closed ')'; returning subexpression.")
                return expr
            
            elif token in UNARY_OPS:
                index += 1
                operand = parse_primary()
            
                if operand is None:
                    print("[*]Error: Unary missing operand.")
                    return None
                node = Node(token, [operand])
                return node
            
            else:
                print(f"[**]Invalid token '{token}' at position {index}.")
                return None
        
        def to_strict(node):
        
            if not node.children:
                return node.value
            elif len(node.children) == 1:
                return f"({node.value} {to_strict(node.children[0])})"
            else:
                return f"({to_strict(node.children[0])} {node.value} {to_strict(node.children[1])})"
        index = 0
        tree = parse_expression()
        current = tree
        
        while current is not None and index < len(tokens):
            if tokens[index] not in BINARY_OPS:
                break
            op = tokens[index]
            index += 1
            right = parse_expression()
            if right is None:
                current = None
                break
            current = Node(op, [current, right])
        
        tree = current  
        
        if index != len(tokens):
            return False, None
        
        else:
            strict_version = to_strict(tree)
            return True, strict_version
        

    def get_original_expression(self):
        return self.original_expression
    