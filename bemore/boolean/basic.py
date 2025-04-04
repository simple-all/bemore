from typing import Iterable, List

from bemore import BasicOutput, Connector, Node, RequiredInput


class All(Node):
    def __init__(self) -> None:
        super().__init__()
        self.input: RequiredInput[Iterable[Any]] = RequiredInput(self, "input", Iterable[Any])
        self.output: BasicOutput[bool] = BasicOutput(self, "output", bool)

    def run(self) -> None:
        input_value = self.input.get_value()
        all_val = all(input_value)
        self.output.set_value(all_val)

    def get_inputs(self) -> List[Connector]:
        return [self.input]

    def get_outputs(self) -> List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.output.validate()


class Any(Node):
    def __init__(self) -> None:
        super().__init__()
        self.input: RequiredInput[Iterable[Any]] = RequiredInput(self, "input", Iterable)
        self.output: BasicOutput[bool] = BasicOutput(self, "output", bool)

    def run(self) -> None:
        input_value = self.input.get_value()
        any_val = any(input_value)
        self.output.set_value(any_val)

    def get_inputs(self) -> List[Connector]:
        return [self.input]

    def get_outputs(self) -> List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.output.validate()
