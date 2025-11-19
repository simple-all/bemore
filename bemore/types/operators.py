import ast
from typing import Generic, List, TypeVar

from bemore import BasicNode, ConnectorProto, DynamicTypeVar, RequiredInput, BasicOutput
_T = TypeVar("_T")


class Append(BasicNode, Generic[_T]):
    def __init__(self) -> None:
        super().__init__()
        self.list: RequiredInput[List[_T]] = RequiredInput(self, "list", List[_T])
        self.value: RequiredInput[_T] = RequiredInput(self, "value", DynamicTypeVar)
        self.output: BasicOutput[List[_T]] = BasicOutput(self, "output", List[_T])

    def run(self) -> None:
        input_list = self.list.get_value()
        new_value = self.value.get_value()
        input_list.append(new_value)

        # Output is a relay, don't need to set its value.

    def get_inputs(self) -> List[ConnectorProto]:
        return [self.list, self.value]

    def get_outputs(self) -> List[ConnectorProto]:
        return [self.output]

    def validate(self) -> None:
        self.list.validate()
        self.value.validate()
        self.output.validate()

    def generate_ast(self) -> ast.Module:
        line = f"{self.list.code_gen_name}.append({self.value.code_gen_name})\n"
        return ast.parse(line)
