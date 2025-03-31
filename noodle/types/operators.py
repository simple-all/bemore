from noodle import BasicNode, RequiredInput, Connector
from typing import Generic, TypeVar, List
from noodle.core.connectors import InputRelay, OutputRelay, connect_relays
import ast


_T = TypeVar("_T")


class Append(BasicNode, Generic[_T]):
    def __init__(self) -> None:
        super().__init__()
        self.list: InputRelay[List[_T]] = InputRelay(self, "list", List[_T])
        self.value: RequiredInput[_T] = RequiredInput(self, "value", _T)
        self.output: OutputRelay[List[_T]] = OutputRelay(self, "output", List[_T])
        connect_relays(self.list, self.output)

    def run(self) -> None:
        input_list = self.list.get_value()
        new_value = self.value.get_value()
        input_list.append(new_value)

        # Output is a relay, don't need to set its value.

    def get_inputs(self) -> List[Connector]:
        return [self.list, self.value]

    def get_outputs(self) -> List[Connector]:
        return [self.output]

    def validate(self) -> None:
        self.list.validate()
        self.value.validate()
        self.output.validate()

    def generate_ast(self) -> ast.Module:
        line = f"{self.list.code_gen_name}.append({self.value.code_gen_name})\n"
        return ast.parse(line)
