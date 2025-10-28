from src.methods import Expression_Methods
from time import sleep

class Menu():
    def __init__(self):
        self.client_expression = None
        self.is_valid_under_relaxed_syntax = False
        self.is_well_formed_propositional_formulae = False
        self.d = None
        self.strict_version = None
    
    def __delattr__(self, name):
        if name == 'd':
            super().__delattr__(name) 
    
    
    def run(self):
        while True:
            expression = input("Enter your expression (or 'quit' to exit): ").strip()
            if expression.lower() == 'quit':
                print("Exiting...")
                return 

            self.client_expression = Expression_Methods(expression)
            self.is_valid_under_relaxed_syntax, self.strict_version = self.client_expression.analyze_relaxed_syntax()
            self.is_well_formed_propositional_formulae, self.d = self.client_expression.is_wppf()
            del self.d
            
            self._show_menu()
    
    def _display(self):
        print("\nChoose your action:")
        print("\t1. Check if the expression is a 'well formed propositional formulae'")
        print("\t2. Analyze Relaxed Syntax")
        print("\t3. Build the abstract syntax step-by-step if the expression is valid")
        print("\t4. Get the variables")
        print("\t5. Enter a new expression")
        print("\t6. Quit")
        
    def _show_menu(self):
        
        while True:
            sleep(0.5)
            self._display()
            choice = input("Your Choice: ").strip()
            if not choice.isdigit():
                print("Invalid Choice")
                continue
            
            choice = int(choice)
            
            match choice:
                case 1:
                    print("This expression is a well formed propositional formulae" if self.is_well_formed_propositional_formulae == True else "Expression is not a well formed propositional formulae")
            
                case 2:
                    print("This expression is valid under relaxed syntax" if self.is_valid_under_relaxed_syntax == True else "Expression is not valid under relaxed syntax")
                
                case 3:
                    if not self.is_well_formed_propositional_formulae:
                        if self.is_valid_under_relaxed_syntax:
                            
                            tree = Expression_Methods(self.strict_version).build_tree()
                            if tree:
                                print("Final tree structure: ")
                                tree.print_tree() 
                        else:
                            print("The given formulae is neither a well formed propositional formulae, nor valid under relaxed syntax.")
                            break
                    else:
                        tree = self.client_expression.build_tree()
                        if tree:
                            print("Final tree structure: ")
                            tree.print_tree()
                
                case 4:
                    if self.is_valid_under_relaxed_syntax or self.is_well_formed_propositional_formulae:
                        vars = self.client_expression.get_variables()
                        print(f"Variables: {sorted(vars)}")
                    else:
                        print("Invalid Expression")
                case 5:   
                    break
                
                case 6:
                    exit()

                case _:
                    pass
    