"""
Module with pretty-printing functionality for ASTs
"""
import ast

class PrettyAST(ast.AST): # pylint: disable=too-few-public-methods
    """
    A version of AST with a nicer repr
    """
    def __repr__(self):
        if self.node_type is ast.Assign:
            return repr(self.targets) + " = " + repr(self.value)
        if self.node_type is ast.Name:
            return self.id
        if self.node_type is ast.Constant:
            return repr(self.value)
        if self.node_type is ast.Module:
            return repr(self.body)

        return super().__repr__()
