import ast
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
        _t = DynamicTypeVar()
        self.iterator: RequiredInput[Iterable[_T]] = RequiredInput(self, "input", _t)

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
        for input_relay in self._inputs.values():
            input_relay.run()

        for value in self.iterator.get_value():
            self._iterator_relay.set_value(value)
            self._system.run()

        for output_relay in self._outputs.values():
            output_relay.run()

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
