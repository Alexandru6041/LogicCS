class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children or []
    
    def get_tree_lines(self):
        if not self.children:
            return [self.value]
        
        #'not'
        elif len(self.children) == 1:
            child_lines = self.children[0].get_tree_lines()
            return [self.value, " |"] + [" " + line for line in child_lines]
        
        #binary operators
        elif len(self.children) == 2:
            left_lines = self.children[0].get_tree_lines()
            right_lines = self.children[1].get_tree_lines()
        
            max_height = max(len(left_lines), len(right_lines))
            left_lines += [""] * (max_height - len(left_lines))
            right_lines += [""] * (max_height - len(right_lines))
        
            left_width = max(len(line) for line in left_lines) if left_lines else 0
            right_width = max(len(line) for line in right_lines) if right_lines else 0
        
            branch = "/" + " " * (left_width // 2) + " " + "\\" + " " * (right_width // 2)
            lines = [self.value, branch]
        
            for l, r in zip(left_lines, right_lines):
                lines.append(l.ljust(left_width) + " " + r)
        
        
            return lines
    
    def print_tree(self):
        lines = self.get_tree_lines()
        for line in lines:
            print(line)
