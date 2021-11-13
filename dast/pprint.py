"""
Module with pretty-printing functionality for ASTs
"""
import ast

class PrettyAST(ast.AST): # pylint: disable=too-few-public-methods
    """
    A version of AST with a nicer repr
    """
    def __repr__(self):
        if isinstance(self, ast.Assign):
            return repr(self.targets) + " = " + repr(self.value)
        if isinstance(self, ast.Name):
            return self.id
        if isinstance(self, ast.Constant):
            return repr(self.value)
        if isinstance(self, ast.Module):
            return repr(self.body)

        return super().__repr__()
