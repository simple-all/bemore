import ast
from typing import Any, Collection, Dict, Generic, Set, Tuple, TypeVar

from bemore import BasicNode, BasicSystem, RequiredInput, SystemProto
from bemore.core.connectors import BasicOutput, InputConnectorProto, OutputConnectorProto
from bemore.core.system_nodes import KeywordInput, Output

_T = TypeVar("_T")


class For(BasicNode, Generic[_T]):
    def __init__(self) -> None:
        super().__init__()
        self._inputs: Dict[str, InputConnectorProto[Any]] = {}
        self._iterables: Dict[str, InputConnectorProto[Any]] = {}
        self._outputs: Dict[str, OutputConnectorProto[Any]] = {}

        # Initialize with a basic system
        self._subsystem: SystemProto = BasicSystem("for")

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
        #     for_loop = ast.For(
        #         iter=ast.Name(self.iterator.code_gen_name),
        #         target=ast.Name(self._iterator_relay.output.code_gen_name),
        #         body=self._subsystem.generate_ast().body,
        #         col_offset=0,
        #         end_col_offset=None,
        #         end_lineno=None,
        #         lineno=0,
        #         orelse=[],
        #     )

        #     return ast.Module(body=[for_loop], type_ignores=[])

        return ast.Module(body=[], type_ignores=[])


# @dataclass(frozen=True)
# class IfRelayPair(Generic[_T]):
#     true: BasicRelay[_T]
#     false: BasicRelay[_T]


# class If(BasicNode):
#     def __init__(self) -> None:
#         super().__init__()
#         self.condition: RequiredInput[Any] = RequiredInput(self, "condition", bool)
#         self._true_system: System = BasicSystem("if true")
#         self._false_system: System = BasicSystem("if false")
#         self._inputs: Dict[str, IfRelayPair[Any]] = {}
#         self._outputs: Dict[str, IfRelayPair[Any]] = {}

#     @property
#     def true_system(self) -> System:
#         return self._true_system

#     @true_system.setter
#     def true_system(self, system: System) -> None:
#         # Remove I/O
#         for relay_pair in self._inputs.values():
#             self._true_system.remove_node(relay_pair.true)

#         for relay_pair in self._outputs.values():
#             self._true_system.remove_node(relay_pair.true)

#         # Set the new system
#         self._true_system = system

#         # Add I/O
#         for relay_pair in self._inputs.values():
#             self._true_system.add_node(relay_pair.true)

#         for relay_pair in self._outputs.values():
#             self._true_system.add_node(relay_pair.true)

#     @property
#     def false_system(self) -> System:
#         return self._false_system

#     @false_system.setter
#     def false_system(self, system: System) -> None:
#         # Remove I/O
#         for relay_pair in self._inputs.values():
#             self._false_system.remove_node(relay_pair.false)

#         for relay_pair in self._outputs.values():
#             self._false_system.remove_node(relay_pair.false)

#         # Set the new system
#         self._false_system = system

#         # Add I/O
#         for relay_pair in self._inputs.values():
#             self._false_system.add_node(relay_pair.false)

#         for relay_pair in self._outputs.values():
#             self._false_system.add_node(relay_pair.false)

#     def add_input(self, name: str) -> IfRelayPair[Any]:
#         assert name not in self._inputs, f"Input with the name {name} already exists."

#         true_relay: BasicRelay[Any] = BasicRelay()
#         true_relay.name = name
#         self._true_system.add_node(true_relay)

#         false_relay: BasicRelay[Any] = BasicRelay()
#         false_relay.name = name
#         self._false_system.add_node(false_relay)

#         new_pair = IfRelayPair(true=true_relay, false=false_relay)
#         self._inputs[name] = new_pair

#         return new_pair

#     def remove_input(self, name: str) -> None:
#         assert name in self._inputs, f"Input with the name {name} does not exist"
#         relay_pair = self._inputs[name]
#         self._true_system.remove_node(relay_pair.true)
#         self._false_system.remove_node(relay_pair.false)
#         del self._inputs[name]

#     def add_output(self, name: str) -> IfRelayPair[Any]:
#         assert name not in self._outputs, f"Output with the name {name} already exists."

#         true_relay: BasicRelay[Any] = BasicRelay()
#         true_relay.name = name
#         self._true_system.add_node(true_relay)

#         false_relay: BasicRelay[Any] = BasicRelay()
#         false_relay.name = name
#         self._false_system.add_node(false_relay)

#         new_pair = IfRelayPair(true=true_relay, false=false_relay)
#         self._inputs[name] = new_pair

#         return new_pair

#     def remove_output(self, name: str) -> None:
#         assert name in self._outputs, f"Input with the name {name} does not exist"
#         relay_pair = self._outputs[name]
#         self._true_system.remove_node(relay_pair.true)
#         self._false_system.remove_node(relay_pair.false)
#         del self._outputs[name]

#     def get_inputs(self) -> Iterable[Connector]:
#         all_inputs: List[Connector] = []
#         for relay_pair in self._inputs.values():
#             all_inputs.extend([relay_pair.true.input, relay_pair.false.input])

#         return all_inputs

#     def get_outputs(self) -> Iterable[Connector]:
#         all_outputs = []
#         for relay_pair in self._outputs.values():
#             all_outputs.extend([relay_pair.true.input, relay_pair.false.input])

#         return all_outputs

#     def run(self) -> None:
#         if self.condition.get_value():
#             self._true_system.run()
#         else:
#             self._false_system.run()

#     def validate(self) -> None:
#         self._true_system.validate()
#         self._false_system.validate()

#     def generate_ast(self) -> ast.Module:
#         if_statememt = ast.If(
#             test=ast.Name(self.condition.code_gen_name),
#             body=self._true_system.generate_ast().body,
#             orelse=self._false_system.generate_ast().body,
#             col_offset=0,
#             end_col_offset=None,
#             end_lineno=None,
#             lineno=0,
#         )

#         return ast.Module(body=[if_statememt], type_ignores=[])
