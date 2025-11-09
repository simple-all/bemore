import ast
from typing import Any, List

from bemore import BasicNode, Connector, RequiredInput


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

    def get_inputs(self) -> List[Connector]:
        return [self.input]

    def get_outputs(self) -> List[Connector]:
        return []

    def validate(self) -> None:
        self.input.validate()

    def generate_ast(self) -> ast.Module:
        return ast.parse("")
