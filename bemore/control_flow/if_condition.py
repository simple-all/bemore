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
