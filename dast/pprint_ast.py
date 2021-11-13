import ast

ast.Assign.__repr__ = lambda x: repr(x.targets) + " = " + repr(x.value)
ast.Name.__repr__ = lambda x: x.id
ast.Constant.__repr__ = lambda x: repr(x.value)
ast.Module.__repr__ = lambda x: repr(x.body)