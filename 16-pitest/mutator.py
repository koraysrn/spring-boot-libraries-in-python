"""Mutation operators, the equivalent of PIT (Pitest) mutations.

Each operator intentionally breaks the code in one small way. A strong test
suite must detect every mutation.
"""

import ast


class _OnceTransformer(ast.NodeTransformer):
    def __init__(self):
        self.applied = False


class FlipComparison(_OnceTransformer):
    def visit_Compare(self, node):
        if not self.applied:
            for i, op in enumerate(node.ops):
                if isinstance(op, ast.Gt):
                    node.ops[i] = ast.Lt()
                    self.applied = True
                    break
                if isinstance(op, ast.Lt):
                    node.ops[i] = ast.Gt()
                    self.applied = True
                    break
        return node


class GteToGt(_OnceTransformer):
    def visit_Compare(self, node):
        if not self.applied:
            for i, op in enumerate(node.ops):
                if isinstance(op, ast.GtE):
                    node.ops[i] = ast.Gt()
                    self.applied = True
                    break
        return node


class AndToOr(_OnceTransformer):
    def visit_BoolOp(self, node):
        if not self.applied and isinstance(node.op, ast.And):
            node.op = ast.Or()
            self.applied = True
        return node


class ReturnZeroToOne(_OnceTransformer):
    def visit_Return(self, node):
        if (
            not self.applied
            and isinstance(node.value, ast.Constant)
            and node.value.value == 0
        ):
            node.value = ast.Constant(value=1)
            self.applied = True
        return node


class DeleteReturnValue(_OnceTransformer):
    def visit_Return(self, node):
        if not self.applied and isinstance(node.value, ast.BinOp):
            node.value = ast.Constant(value=None)
            self.applied = True
        return node


class RemoveIfCondition(_OnceTransformer):
    def visit_If(self, node):
        if not self.applied and any(isinstance(stmt, ast.Raise) for stmt in node.body):
            self.applied = True
            return node.body
        return node


class ActiveStringToEmpty(_OnceTransformer):
    def visit_Constant(self, node):
        if not self.applied and isinstance(node.value, str) and node.value == "active":
            node.value = ""
            self.applied = True
        return node


class RemoveRaise(_OnceTransformer):
    def visit_Raise(self, node):
        if not self.applied:
            self.applied = True
            return ast.Pass()
        return node


OPERATORS = [
    ("flip > to <", FlipComparison),
    ("change >= to >", GteToGt),
    ("change and to or", AndToOr),
    ("change 0 to 1", ReturnZeroToOne),
    ("delete return", DeleteReturnValue),
    ("remove if condition", RemoveIfCondition),
    ("change 'active' to empty string", ActiveStringToEmpty),
    ("delete raise", RemoveRaise),
]


def generate_mutants(source):
    mutants = []
    for description, transformer_class in OPERATORS:
        tree = ast.parse(source)
        transformer = transformer_class()
        transformer.visit(tree)
        if transformer.applied:
            ast.fix_missing_locations(tree)
            mutants.append((description, ast.unparse(tree)))
    return mutants
