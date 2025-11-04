import re
import itertools
import sys
import os
from contextlib import redirect_stdout

from src.tree import Node
from src.expression import Expression
from utils.settings import (
    ATOM_PATTERN,
    BINARY_OPS,
    UNARY_OPS,
    SYMBOL_MAP
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
        return {token for token in tokens if re.fullmatch(ATOM_PATTERN, token) and token not in ['⊤', '⊥']}

    
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
        
        word_to_symbol = {variable: key for key, variable in SYMBOL_MAP.items()}

        
        precedence = {'not': 4, 'and': 3, 'or': 2, 'implies': 1, 'equiv': 0}
        
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
            
            return left
        
        def parse_primary():
            nonlocal index
            
            if index >= len(tokens):
                return None
            
            token = tokens[index]
            
            if re.fullmatch(ATOM_PATTERN, token):
                index += 1
                return Node(token)
            elif token == "(":
                index += 1
                expr = parse_expression()
            
                if expr is None or index >= len(tokens) or tokens[index] != ")":
                    return None
                index += 1
                return expr
            
            elif token in UNARY_OPS:
                index += 1
                operand = parse_primary()
            
                if operand is None:
                    return None
                node = Node(token, [operand])
                return node
            
            else:
                return None
        
        def to_strict(node):
        
            if not node.children:
                return word_to_symbol.get(node.value, node.value)
            elif len(node.children) == 1:
                return f"({word_to_symbol.get(node.value, node.value)} {to_strict(node.children[0])})"
            else:
                return f"({to_strict(node.children[0])} {word_to_symbol.get(node.value, node.value)} {to_strict(node.children[1])})"
            
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
    
    def get_subformulas(self, node, subformulas=None, seen=None):
        if subformulas is None:
            subformulas = []
        if seen is None:
            seen = set()
        
        if node.children:
            for child in node.children:
                self.get_subformulas(child, subformulas, seen)
            
            strict_str = self.to_strict_node(node)
            if strict_str not in seen:
                seen.add(strict_str)
                subformulas.append(node)
        
        return subformulas

    
    def to_strict_node(self, node):
        word_to_symbol = {variable: key for key, variable in SYMBOL_MAP.items()}
        
        if not node.children:
            return word_to_symbol.get(node.value, node.value)
        elif len(node.children) == 1:
            return f"({word_to_symbol.get(node.value, node.value)} {self.to_strict_node(node.children[0])})"
        
        else:
            return f"({self.to_strict_node(node.children[0])} {word_to_symbol.get(node.value, node.value)} {self.to_strict_node(node.children[1])})"

    def build_truth_table(self):
        with redirect_stdout(open(os.devnull, 'w')):
            tree = self.build_tree()
        
        if tree is None:
            print("Error: Invalid formula.")
            return
        
        variables = sorted(list(self.get_variables()))
        n = len(variables)
        
        if n == 0:
            print("Truth Table for constant formula:")
            value = self.evaluate_constant(tree)
            print(f"{self.expression} | {value}")
            return
        
        subformulas = self.get_subformulas(tree)
        
        _, strict_expr = self.analyze_relaxed_syntax()
        if strict_expr is None:
            strict_expr = self.expression
        
        header = variables + [self.to_strict_node(sub) for sub in subformulas]
        
        interpretations = list(itertools.product([True, False], repeat=n))
        rows = []
        for interp in interpretations:
            assignment = dict(zip(variables, interp))
            row = [str(int(assignment[var])) for var in variables]
            for sub in subformulas:
                if sub.value == '⊤':
                    sub_value = True
                elif sub.value == '⊥':
                    sub_value = False
                else:
                    sub_value = self.evaluate_tree(sub, assignment)
                row.append(str(int(sub_value)))
            rows.append(row)
        col_widths = [max(len(header[i]), max(len(row[i]) for row in rows)) for i in range(len(header))]
    
        header_line = " | ".join(header[i].ljust(col_widths[i]) for i in range(len(header)))
        print(header_line)
        
        separator = "+".join("-" * (col_widths[i] + 2) for i in range(len(header)))
        print(separator)
        
        for row in rows:
            row_line = " | ".join(row[i].ljust(col_widths[i]) for i in range(len(row)))
            print(row_line)

    
    def evaluate_tree(self, node, assignment):
        if not node.children:
            if node.value == '⊤':
                return True
            elif node.value in '⊥':
                return False
            else:
                return assignment.get(node.value, False)
        
        op = node.value
        if op == 'not':
            return not self.evaluate_tree(node.children[0], assignment)
        elif op == 'and':
            return self.evaluate_tree(node.children[0], assignment) and self.evaluate_tree(node.children[1], assignment)
        elif op == 'or':
            return self.evaluate_tree(node.children[0], assignment) or self.evaluate_tree(node.children[1], assignment)
        elif op == 'implies':
            left = self.evaluate_tree(node.children[0], assignment)
            right = self.evaluate_tree(node.children[1], assignment)
            return not left or right
        elif op == 'equiv':
            left = self.evaluate_tree(node.children[0], assignment)
            right = self.evaluate_tree(node.children[1], assignment)
            return left == right
    

    def evaluate_constant(self, tree):
        return self.evaluate_tree(tree, {})
    
    def get_original_expression(self):
        return self.original_expression