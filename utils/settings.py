ATOM_PATTERN = r'[A-Z⊤⊥]'
OPERATIONS_PATTERN = r"(^|∧|∨|v|⇒|→|⇔|↔|¬)"

BINARY_OPS = {"and", 'or', 'implies', 'equiv'}
UNARY_OPS = {"not"}
OPS = BINARY_OPS | UNARY_OPS

SYMBOL_MAP = {
    "^": "and",
    "∧": "and",
    "∨": "or",
    "v": "or",
    "⇒": "implies",
    "→": "implies",
    "⇔": "equiv",
    "↔": "equiv",
    "¬": "not",
}
