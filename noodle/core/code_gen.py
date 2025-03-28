import ast
from typing import Protocol


class CodeGenerator(Protocol):
    def generate_ast(self) -> ast.Module: ...


def generate_code(obj: CodeGenerator) -> str:
    ast_gen = obj.generate_ast()
    return ast.unparse(ast_gen)
