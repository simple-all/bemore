import ast
from typing import Generic, TypeVar, Optional
from typing import List as _List

from bemore import BasicNode, BasicOutput, CodeGenerator, Connector

_T = TypeVar("_T")


class Int(BasicNode, CodeGenerator):
    def __init__(self, value: int) -> None:
        super().__init__()
        self.output: BasicOutput[int] = BasicOutput(self, "output", int)
        self._value = value

    def run(self) -> None:
        self.output.set_value(self._value)

    def get_inputs(self) -> _List[Connector]:
        return []

    def get_outputs(self) -> _List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.output.validate()

    def generate_ast(self) -> ast.Module:
        line = f"{self.output.code_gen_name} = {self._value}\n"
        return ast.parse(line)


class Float(BasicNode):
    def __init__(self, value: float) -> None:
        super().__init__()
        self.output: BasicOutput[float] = BasicOutput(self, "output", float)
        self._value = value

    def run(self) -> None:
        self.output.set_value(self._value)

    def get_inputs(self) -> _List[Connector]:
        return []

    def get_outputs(self) -> _List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.output.validate()

    def generate_ast(self) -> ast.Module:
        line = f"{self.output.code_gen_name} = {self._value}\n"
        return ast.parse(line)


class String(BasicNode):
    def __init__(self, value: str) -> None:
        super().__init__()
        self.output: BasicOutput[str] = BasicOutput(self, "output", str)
        self._value = value

    def run(self) -> None:
        self.output.set_value(self._value)

    def get_inputs(self) -> _List[Connector]:
        return []

    def get_outputs(self) -> _List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.output.validate()

    def generate_ast(self) -> ast.Module:
        line = f"{self.output.code_gen_name} = {self._value}\n"
        return ast.parse(line)


class List(BasicNode, Generic[_T]):
    def __init__(self) -> None:
        super().__init__()
        self.output: BasicOutput[_List[_T]] = BasicOutput(self, "output", _List[_T])
        self.value: Optional[_List[_T]] = None

    def run(self) -> None:
        if self.value is not None:
            self.output.set_value(self.value)
        else:
            self.output.set_value([])

    def get_inputs(self) -> _List[Connector]:
        return []

    def get_outputs(self) -> _List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.output.validate()

    def generate_ast(self) -> ast.Module:
        if self.value is not None:
            line = f"{self.output.code_gen_name} = {self.value}\n"
        else:
            line = f"{self.output.code_gen_name} = []\n"

        return ast.parse(line)
