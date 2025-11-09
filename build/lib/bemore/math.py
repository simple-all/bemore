import math
from typing import Any, Generic, List, SupportsIndex, TypeVar

from bemore.core.connectors import (
    BasicOutput,
    Connector,
    Input,
    Output,
    RequiredInput,
    RequiredMultiInput,
)
from bemore.core.node import Node


class MathNode(Node):
    pass


_T = TypeVar("_T")


class Indexer(MathNode, Generic[_T]):
    def __init__(self) -> None:
        super().__init__()
        self.indexable: RequiredInput[List[_T]] = RequiredInput(self, "indexable", SupportsIndex)
        self.index: RequiredInput[int] = RequiredInput(self, "index", int)
        self.output: BasicOutput[_T] = BasicOutput(self, "output", Any)

    def run(self) -> None:
        input_list = self.indexable.get_value()
        index = self.index.get_value()
        self.output.set_value(input_list[index])

    def validate(self) -> None:
        self.indexable.validate()
        self.index.validate()
        self.output.validate()

    def get_inputs(self) -> List[Connector]:
        return [self.indexable, self.index]

    def get_outputs(self) -> List[Connector]:
        return [self.output]


class Int(MathNode):
    def __init__(self, value: int) -> None:
        super().__init__()
        self.output: BasicOutput[int] = BasicOutput(self, "output", int)
        self._value = value

    def run(self) -> None:
        self.output.set_value(self._value)

    def get_inputs(self) -> List[Input]:
        return []

    def get_outputs(self) -> List[Output]:
        return [self.output]

    def validate(self) -> None:
        self.output.validate()


class Float(MathNode):
    def __init__(self, value: float) -> None:
        super().__init__()
        self.output: BasicOutput[float] = BasicOutput(self, "output", float)
        self._value = value

    def run(self) -> None:
        self.output.set_value(self._value)

    def get_inputs(self) -> List[Input]:
        return []

    def get_outputs(self) -> List[Output]:
        return [self.output]

    def validate(self) -> None:
        self.output.validate()


class String(MathNode):
    def __init__(self, value: str) -> None:
        super().__init__()
        self.output: BasicOutput[str] = BasicOutput(self, "output", str)
        self._value = value

    def run(self) -> None:
        self.output.set_value(self._value)

    def get_inputs(self) -> List[Input]:
        return []

    def get_outputs(self) -> List[Output]:
        return [self.output]

    def validate(self) -> None:
        self.output.validate()


class Sum(MathNode):
    def __init__(self) -> None:
        super().__init__()
        self.input: RequiredMultiInput[float] = RequiredMultiInput(self, "input", float)
        self.output: BasicOutput[float] = BasicOutput(self, "output", float)

    def run(self) -> None:
        in_value = self.input.get_value()
        self.output.set_value(sum(in_value))

    def get_inputs(self) -> List[Input]:
        return [self.input]

    def get_outputs(self) -> List[Output]:
        return [self.output]

    def validate(self) -> None:
        self.input.validate()
        self.output.validate()


class Product(MathNode):
    def __init__(self) -> None:
        super().__init__()
        self.input: RequiredMultiInput[float] = RequiredMultiInput(self, "input", float)
        self.output: BasicOutput[float] = BasicOutput(self, "output", float)

    def run(self) -> None:
        value = math.prod(self.input.get_value())

        self.output.set_value(value)

    def get_inputs(self) -> List[Input]:
        return [self.input]

    def get_outputs(self) -> List[Output]:
        return [self.output]

    def validate(self) -> None:
        self.input.validate()
        self.output.validate()


class Printer(MathNode):
    def __init__(self) -> None:
        super().__init__()
        self.input: RequiredInput[Any] = RequiredInput(self, "input", Any)

    def run(self) -> None:
        print(f"{self.name}: {self.input.get_value()}")

    def get_inputs(self) -> List[Input]:
        return [self.input]

    def get_outputs(self) -> List[Output]:
        return []

    def validate(self) -> None:
        self.input.validate()
