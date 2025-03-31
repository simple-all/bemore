import ast
from dataclasses import dataclass
from typing import Any, Dict, Generic, Iterable, List, TypeVar

from bemore import BasicNode, BasicSystem, Connector, DynamicTypeVar, RequiredInput, System
from bemore.core.connectors import BasicOutput, InputRelay, OutputRelay, connect_relays

_T = TypeVar("_T")


class Relay(BasicNode, Generic[_T]):
    pass


class BasicRelay(Relay[_T]):
    def __init__(self) -> None:
        super().__init__()
        _t = DynamicTypeVar()
        self._input: InputRelay[_T] = InputRelay(self, "input", _t)
        self._output: OutputRelay[_T] = OutputRelay(self, "output", _t)
        connect_relays(self._input, self._output)

    def get_inputs(self) -> Iterable[Connector]:
        return [self._input]

    def get_outputs(self) -> Iterable[Connector]:
        return [self._output]

    def run(self) -> None:
        pass

    def validate(self) -> None:
        pass

    def generate_ast(self) -> ast.Module:
        return ast.Module(body=[], type_ignores=[])


class IteratorRelay(Relay[_T]):
    def __init__(self) -> None:
        BasicNode.__init__(self)
        self._output: BasicOutput[_T] = BasicOutput(self, "output", DynamicTypeVar())

    def set_value(self, value: _T) -> None:
        self._output.set_value(value)

    def run(self) -> None:
        pass

    def get_inputs(self) -> Iterable[Connector]:
        return []

    def get_outputs(self) -> Iterable[Connector]:
        return [self._output]

    def validate(self) -> None:
        pass

    def generate_ast(self) -> ast.Module:
        return ast.Module(body=[], type_ignores=[])


class For(BasicNode, Generic[_T]):
    def __init__(self) -> None:
        super().__init__()
        self.iterator: RequiredInput[Iterable[_T]] = RequiredInput(self, "input", DynamicTypeVar())

        # Iteration based I/O
        self._iterator_relay: IteratorRelay[_T] = IteratorRelay()

        # Passthrough I/O
        self._inputs: Dict[str, BasicRelay[Any]] = {}
        self._outputs: Dict[str, BasicRelay[Any]] = {}

        self._system: System = BasicSystem()
        self._system.add_node(self._iterator_relay)

    @property
    def system(self) -> System:
        return self._system

    @system.setter
    def system(self, system: System) -> None:
        # Remove iteration based I/O
        self._system.remove_node(self._iterator_relay)

        # Remove passthrough based I/O
        for input_relay in self._inputs.values():
            self._system.remove_node(input_relay)

        for output_relay in self._outputs.values():
            self._system.remove_node(output_relay)

        # Set the new system
        self._system = system

        # Add iteration based I/O
        self._system.add_node(self._iterator_relay)
        self._system.add_nodes(*self._inputs.values())
        self._system.add_nodes(*self._outputs.values())

    def add_input(self, name: str) -> BasicRelay[Any]:
        assert name not in self._inputs, f"Input with the name {name} already exists."
        new_relay: BasicRelay[Any] = BasicRelay()
        new_relay.name = name
        self._inputs[name] = new_relay
        self._system.add_node(new_relay)
        return new_relay

    def remove_input(self, name: str) -> None:
        assert name in self._inputs, f"Input with the name {name} does not exist"
        self._system.remove_node(self._inputs[name])
        del self._inputs[name]

    def add_output(self, name: str) -> BasicRelay[Any]:
        assert name not in self._outputs, f"Output with the name {name} already exists."
        new_output: BasicRelay[Any] = BasicRelay()
        new_output.name = name
        self._outputs[name] = new_output
        self._system.add_node(new_output)
        return new_output

    def remove_output(self, name: str) -> None:
        assert name in self._outputs, f"Output with the name {name} does not exist."
        self._system.remove_node(self._outputs[name])
        del self._outputs[name]

    def get_inputs(self) -> Iterable[Connector]:
        all_inputs = [self.iterator]
        for input_relay in self._inputs.values():
            all_inputs.append(input_relay._input)

        return all_inputs

    def get_outputs(self) -> Iterable[Connector]:
        passthrough_outputs: List[Connector] = [
            output_relay._output for output_relay in self._outputs.values()
        ]
        return passthrough_outputs

    def run(self) -> None:
        for value in self.iterator.get_value():
            self._iterator_relay.set_value(value)
            self._system.run()

    def validate(self) -> None:
        self.iterator.validate()
        for input_relay in self._inputs.values():
            input_relay.validate()

        for output_relay in self._outputs.values():
            output_relay.validate()

    def generate_ast(self) -> ast.Module:
        for_loop = ast.For(
            iter=ast.Name(self.iterator.code_gen_name),
            target=ast.Name(self._iterator_relay._output.code_gen_name),
            body=self._system.generate_ast().body,
            col_offset=0,
            end_col_offset=None,
            end_lineno=None,
            lineno=0,
            orelse=[],
        )

        return ast.Module(body=[for_loop], type_ignores=[])


@dataclass(frozen=True)
class IfRelayPair(Generic[_T]):
    true: BasicRelay[_T]
    false: BasicRelay[_T]


class If(BasicNode):
    def __init__(self) -> None:
        super().__init__()
        self.condition: RequiredInput[Any] = RequiredInput(self, "condition", bool)
        self._true_system: System = BasicSystem()
        self._false_system: System = BasicSystem()
        self._inputs: Dict[str, IfRelayPair[Any]] = {}
        self._outputs: Dict[str, IfRelayPair[Any]] = {}

    @property
    def true_system(self) -> System:
        return self._true_system

    @true_system.setter
    def true_system(self, system: System) -> None:
        # Remove I/O
        for relay_pair in self._inputs.values():
            self._true_system.remove_node(relay_pair.true)

        for relay_pair in self._outputs.values():
            self._true_system.remove_node(relay_pair.true)

        # Set the new system
        self._true_system = system

        # Add I/O
        for relay_pair in self._inputs.values():
            self._true_system.add_node(relay_pair.true)

        for relay_pair in self._outputs.values():
            self._true_system.add_node(relay_pair.true)

    @property
    def false_system(self) -> System:
        return self._false_system

    @false_system.setter
    def false_system(self, system: System) -> None:
        # Remove I/O
        for relay_pair in self._inputs.values():
            self._false_system.remove_node(relay_pair.false)

        for relay_pair in self._outputs.values():
            self._false_system.remove_node(relay_pair.false)

        # Set the new system
        self._false_system = system

        # Add I/O
        for relay_pair in self._inputs.values():
            self._false_system.add_node(relay_pair.false)

        for relay_pair in self._outputs.values():
            self._false_system.add_node(relay_pair.false)

    def add_input(self, name: str) -> IfRelayPair[Any]:
        assert name not in self._inputs, f"Input with the name {name} already exists."

        true_relay: BasicRelay[Any] = BasicRelay()
        true_relay.name = name
        self._true_system.add_node(true_relay)

        false_relay: BasicRelay[Any] = BasicRelay()
        false_relay.name = name
        self._false_system.add_node(false_relay)

        new_pair = IfRelayPair(true=true_relay, false=false_relay)
        self._inputs[name] = new_pair

        return new_pair

    def remove_input(self, name: str) -> None:
        assert name in self._inputs, f"Input with the name {name} does not exist"
        relay_pair = self._inputs[name]
        self._true_system.remove_node(relay_pair.true)
        self._false_system.remove_node(relay_pair.false)
        del self._inputs[name]

    def add_output(self, name: str) -> IfRelayPair[Any]:
        assert name not in self._outputs, f"Output with the name {name} already exists."

        true_relay: BasicRelay[Any] = BasicRelay()
        true_relay.name = name
        self._true_system.add_node(true_relay)

        false_relay: BasicRelay[Any] = BasicRelay()
        false_relay.name = name
        self._false_system.add_node(false_relay)

        new_pair = IfRelayPair(true=true_relay, false=false_relay)
        self._inputs[name] = new_pair

        return new_pair

    def remove_output(self, name: str) -> None:
        assert name in self._outputs, f"Input with the name {name} does not exist"
        relay_pair = self._outputs[name]
        self._true_system.remove_node(relay_pair.true)
        self._false_system.remove_node(relay_pair.false)
        del self._outputs[name]

    def get_inputs(self) -> Iterable[Connector]:
        all_inputs: List[Connector] = []
        for relay_pair in self._inputs.values():
            all_inputs.extend([relay_pair.true._input, relay_pair.false._input])

        return all_inputs

    def get_outputs(self) -> Iterable[Connector]:
        all_outputs = []
        for relay_pair in self._outputs.values():
            all_outputs.extend([relay_pair.true._input, relay_pair.false._input])

        return all_outputs

    def run(self) -> None:
        if self.condition.get_value():
            self._true_system.run()
        else:
            self._false_system.run()

    def validate(self) -> None:
        self._true_system.validate()
        self._false_system.validate()

    def generate_ast(self) -> ast.Module:
        if_statememt = ast.If(
            test=ast.Name(self.condition.code_gen_name),
            body=self._true_system.generate_ast().body,
            orelse=self._false_system.generate_ast().body,
            col_offset=0,
            end_col_offset=None,
            end_lineno=None,
            lineno=0,
        )

        return ast.Module(body=[if_statememt], type_ignores=[])
