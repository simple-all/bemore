import ast
from typing import Any, List

from bemore import BasicNode, Connector, RequiredInput


class ConsolePrinter(BasicNode):
    def __init__(self) -> None:
        super().__init__()
        self.input: RequiredInput[Any] = RequiredInput(self, "input", Any)

    def run(self) -> None:
        print(f"{self.name}: {self.input.get_value()}")

    def get_inputs(self) -> List[Connector]:
        return [self.input]

    def get_outputs(self) -> List[Connector]:
        return []

    def validate(self) -> None:
        self.input.validate()

    def generate_ast(self) -> ast.Module:
        return ast.parse(f"print({self.input.code_gen_name})")
