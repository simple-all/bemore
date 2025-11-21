import ast
from collections.abc import Collection
from typing import Any

from bemore import BasicNode, InputConnectorProto, OutputConnectorProto, RequiredInput


class Display(BasicNode):
    def __init__(self) -> None:
        super().__init__()
        self.input: RequiredInput[Any] = RequiredInput(self, "input", Any)
        self._to_display: Any = ""

    @property
    def to_display(self) -> Any:
        return self._to_display

    def run(self) -> None:
        self._to_display = self.input.get_value()

    def get_inputs(self) -> Collection[InputConnectorProto[Any]]:
        return [self.input]

    def get_outputs(self) -> Collection[OutputConnectorProto[Any]]:
        return []

    def validate(self) -> None:
        self.input.validate()

    def generate_ast(self) -> ast.Module:
        return ast.parse("")
