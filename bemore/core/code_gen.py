import ast
from typing import Protocol


class CodeGeneratorProto(Protocol):
    def generate_ast(self) -> ast.Module: ...


def generate_code(obj: CodeGeneratorProto) -> str:
    ast_gen = obj.generate_ast()
    return ast.unparse(ast_gen)
