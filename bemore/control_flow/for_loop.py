import ast
from typing import Any, Collection, Dict, Set, Tuple

from bemore import BasicNode, BasicSystem, RequiredInput, SystemProto
from bemore.core.connectors import BasicOutput, InputConnectorProto, OutputConnectorProto
from bemore.core.system_nodes import KeywordInput, Output


class For[T](BasicNode):
    def __init__(self) -> None:
        super().__init__()
        self._inputs: Dict[str, InputConnectorProto[Any]] = {}
        self._iterables: Dict[str, InputConnectorProto[Any]] = {}
        self._outputs: Dict[str, OutputConnectorProto[Any]] = {}

        # Initialize with a basic system
        self._subsystem: SystemProto = BasicSystem("for")

        self.inline_subsystem: bool = True

    @property
    def subsystem(self) -> SystemProto:
        return self._subsystem

    @subsystem.setter
    def subsystem(self, subsystem: SystemProto) -> None:
        # Set the new system
        self._subsystem = subsystem

    @property
    def input_names(self) -> Set[str]:
        all_input_names = set(self._inputs).union(self._iterables)
        return all_input_names

    def make_iterable(self, name: str) -> None:
        assert name in self._inputs
        self._iterables[name] = self._inputs[name]
        del self._inputs[name]

    def make_singular(self, name: str) -> None:
        assert name in self._iterables
        self._inputs[name] = self._iterables[name]
        del self._iterables[name]

    def add_input(
        self,
        name: str,
        signature: Any,
    ) -> Tuple[InputConnectorProto[Any], KeywordInput[Any]]:
        assert name not in self.input_names, f"Input with the name {name} already exists."

        subsystem_input_node = KeywordInput[Any](name)
        self._subsystem.add_node(subsystem_input_node)
        self._inputs[name] = RequiredInput(self, name, signature)

        return self._inputs[name], subsystem_input_node

    def remove_input(self, name: str) -> None:
        assert name in self._inputs, f"Input with the name {name} does not exist"
        del self._inputs[name]

        for node in self._subsystem.get_inputs():
            if node.name == name:
                self._subsystem.remove_node(node)
                break

    def add_output(
        self,
        name: str,
        signature: Any,
    ) -> OutputConnectorProto[Any]:
        assert name not in self._outputs, f"Output with the name {name} already exists."
        self._outputs[name] = BasicOutput(self, name, signature)

        self._subsystem.add_node(Output(name))

        return self._outputs[name]

    def remove_output(self, name: str) -> None:
        assert name in self._outputs, f"Output with the name {name} does not exist."
        del self._outputs[name]

        for node in self._subsystem.get_outputs():
            if node.name == name:
                self._subsystem.remove_node(node)
                break

    def get_inputs(self) -> Collection[InputConnectorProto[Any]]:
        return self._inputs.values()

    def get_outputs(self) -> Collection[OutputConnectorProto[Any]]:
        return self._outputs.values()

    def run(self) -> None:
        iterable_values = [connector.get_value() for connector in self._iterables.values()]
        iterable_names = self._iterables.keys()
        output_map = {}

        inputs = {connector.name: connector.get_value() for connector in self._inputs.values()}

        for values in zip(*iterable_values):
            iterable_inputs = {name: value for name, value in zip(iterable_names, values)}
            inputs.update(iterable_inputs)
            output_map = self._subsystem.run(**inputs)

        for name, value in output_map.items():
            self._outputs[name].set_value(value)

    def validate(self) -> None:
        for input_node in self._inputs.values():
            input_node.validate()

        for output_node in self._outputs.values():
            output_node.validate()

    def generate_ast(self) -> ast.Module:

        singular_names = list(self._inputs.keys())
        iterable_names = list(self._iterables.keys())
        input_name_node_map = {node.name: node for node in self._subsystem.get_inputs()}

        iterable_node_names: list[ast.expr] = [
            ast.Name(input_name_node_map[name].output.code_gen_name) for name in iterable_names
        ]

        singular_node_name_aliases: Dict[str, str] = {
            input_name_node_map[name].output.code_gen_name: self._inputs[name].code_gen_name
            for name in singular_names
        }

        subsystem_ast = self._subsystem.generate_ast()

        if self.inline_subsystem:
            # Replace subsystem singular inputs with for loop singular names
            for node in ast.walk(subsystem_ast):
                if isinstance(node, ast.Name):
                    alias = singular_node_name_aliases.get(node.id)
                    if alias is not None:
                        node.id = alias

        for_loop = ast.For(
            iter=ast.Call(
                ast.Name("zip"),
                args=[ast.Name(connector.code_gen_name) for connector in self._iterables.values()],
                keywords=[],
            ),
            target=ast.Tuple(elts=iterable_node_names),
            body=subsystem_ast.body,
            col_offset=0,
            end_col_offset=None,
            end_lineno=None,
            lineno=0,
            orelse=[],
        )

        return ast.Module(body=[for_loop], type_ignores=[])
