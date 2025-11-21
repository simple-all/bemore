import ast
from typing import Any

from bemore import BasicNode, RequiredInput, InputConnectorProto, OutputConnectorProto
from collections.abc import Collection


class ConsolePrinter(BasicNode):
    def __init__(self) -> None:
        super().__init__()
        self.input: RequiredInput[Any] = RequiredInput(self, "input", Any)

    def run(self) -> None:
        print(f"{self.name}: {self.input.get_value()}")

    def get_inputs(self) -> Collection[InputConnectorProto[Any]]:
        return [self.input]

    def get_outputs(self) -> Collection[OutputConnectorProto[Any]]:
        return []

    def validate(self) -> None:
        self.input.validate()

    def generate_ast(self) -> ast.Module:
        return ast.parse(f"print({self.input.code_gen_name})")
