import math
from typing import Generic, List, SupportsAbs, TypeVar

from noodle import BasicOutput, Connector, DynamicTypeVar, Node, RequiredInput, RequiredMultiInput

_T = TypeVar("_T")


class Sum(Node):
    def __init__(self) -> None:
        super().__init__()
        self.input: RequiredMultiInput[float] = RequiredMultiInput(self, "input", float)
        self.output: BasicOutput[float] = BasicOutput(self, "output", float)

    def run(self) -> None:
        in_value = self.input.get_value()
        self.output.set_value(sum(in_value))

    def get_inputs(self) -> List[Connector]:
        return [self.input]

    def get_outputs(self) -> List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.input.validate()
        self.output.validate()


class Product(Node):
    def __init__(self) -> None:
        super().__init__()
        self.input: RequiredMultiInput[float] = RequiredMultiInput(self, "input", float)
        self.output: BasicOutput[float] = BasicOutput(self, "output", float)

    def run(self) -> None:
        value = math.prod(self.input.get_value())

        self.output.set_value(value)

    def get_inputs(self) -> List[Connector]:
        return [self.input]

    def get_outputs(self) -> List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.input.validate()
        self.output.validate()


class Subtract(Node):

    def __init__(self) -> None:
        super().__init__()
        self.left: RequiredInput[float] = RequiredInput(self, "input", float)
        self.right: RequiredInput[float] = RequiredInput(self, "input", float)
        self.output: BasicOutput[float] = BasicOutput(self, "output", float)

    def run(self) -> None:
        left = self.left.get_value()
        right = self.right.get_value()

        result = left - right

        self.output.set_value(result)

    def get_inputs(self) -> List[Connector]:
        return [self.left, self.right]

    def get_outputs(self) -> List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.left.validate()
        self.right.validate()
        self.output.validate()


class Divide(Node):

    def __init__(self) -> None:
        super().__init__()
        self.numerator: RequiredInput[float] = RequiredInput(self, "input", float)
        self.denominator: RequiredInput[float] = RequiredInput(self, "input", float)
        self.output: BasicOutput[float] = BasicOutput(self, "output", float)

    def run(self) -> None:
        numerator = self.numerator.get_value()
        denominator = self.denominator.get_value()

        result = numerator / denominator

        self.output.set_value(result)

    def get_inputs(self) -> List[Connector]:
        return [self.numerator, self.denominator]

    def get_outputs(self) -> List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.numerator.validate()
        self.denominator.validate()
        self.output.validate()


class Abs(Node, Generic[_T]):
    def __init__(self) -> None:
        super().__init__()
        _t = DynamicTypeVar()
        self.input: RequiredInput[SupportsAbs[_T]] = RequiredInput(self, "input", _t)
        self.output: BasicOutput[_T] = BasicOutput(self, "output", _t)

    def run(self) -> None:
        input_value = self.input.get_value()
        abs_val = abs(input_value)
        self.output.set_value(abs_val)

    def get_inputs(self) -> List[Connector]:
        return [self.input]

    def get_outputs(self) -> List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.output.validate()


class Modulo(Node):

    def __init__(self) -> None:
        super().__init__()
        self.dividend: RequiredInput[float] = RequiredInput(self, "input", float)
        self.divisor: RequiredInput[float] = RequiredInput(self, "input", float)
        self.output: BasicOutput[float] = BasicOutput(self, "output", float)

    def run(self) -> None:
        dividend = self.dividend.get_value()
        divisor = self.divisor.get_value()

        result = dividend % divisor

        self.output.set_value(result)

    def get_inputs(self) -> List[Connector]:
        return [self.dividend, self.divisor]

    def get_outputs(self) -> List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.dividend.validate()
        self.divisor.validate()
        self.output.validate()
