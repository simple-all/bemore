from typing import Iterable, List
from typing import Any as _Any
from collections.abc import Collection

from bemore import (
    BasicOutput,
    Node,
    RequiredInput,
    InputConnectorProto,
    OutputConnectorProto,
)


class All(Node):
    def __init__(self) -> None:
        super().__init__()
        self.input: RequiredInput[Iterable[_Any]] = RequiredInput(self, "input", Iterable[Any])
        self.output: BasicOutput[bool] = BasicOutput(self, "output", bool)

    def run(self) -> None:
        input_value = self.input.get_value()
        all_val = all(input_value)
        self.output.set_value(all_val)

    def get_inputs(self) -> Collection[InputConnectorProto[Iterable[_Any]]]:
        return [self.input]

    def get_outputs(self) -> Collection[OutputConnectorProto[bool]]:
        return [self.output]

    def validate(self) -> None:
        self.output.validate()


a: List[int] = [1, 2, 3]
b: float = 3.5
c = b in a


class Any(Node):
    def __init__(self) -> None:
        super().__init__()
        self.input: RequiredInput[Iterable[_Any]] = RequiredInput(self, "input", Iterable)
        self.output: BasicOutput[bool] = BasicOutput(self, "output", bool)

    def run(self) -> None:
        input_value = self.input.get_value()
        any_val = any(input_value)
        self.output.set_value(any_val)

    def get_inputs(self) -> List[InputConnectorProto[Iterable[_Any]]]:
        return [self.input]

    def get_outputs(self) -> List[OutputConnectorProto[bool]]:
        return [self.output]

    def validate(self) -> None:
        self.output.validate()
