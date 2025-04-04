from typing import Any, List

from bemore import Connector, Node, RequiredInput


class ConsolePrinter(Node):
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
