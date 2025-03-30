import ast
from typing import Any, Dict, Generic, Iterable, List, Sequence, TypeVar

from bemore import BasicNode, BasicSystem, Connector, DynamicTypeVar, RequiredInput, System
from bemore.core.connectors import (
    AccumulatingOutput,
    BasicOutput,
    InputRelay,
    OutputRelay,
    connect_relays,
)

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


class Accumulator(BasicNode, Generic[_T]):
    def __init__(self) -> None:
        super().__init__()
        _t = DynamicTypeVar()
        self._input: RequiredInput[_T] = RequiredInput(self, "input", _t)
        self._output: AccumulatingOutput[_T] = AccumulatingOutput(self, "output", _t)

    def reset(self) -> None:
        self._output.reset()

    def run(self) -> None:
        new_value = self._input.get_value()
        self._output.accumulate(new_value)

    def validate(self) -> None:
        pass

    def generate_ast(self) -> ast.Module:
        line = f"{self._output.code_gen_name}.append({self._input.code_gen_name})\n"
        return ast.parse(line)

    def get_inputs(self) -> Sequence[Connector]:
        return [self._input]

    def get_outputs(self) -> Sequence[Connector]:
        return [self._output]


class For(BasicNode, Generic[_T]):
    def __init__(self) -> None:
        super().__init__()
        _t = DynamicTypeVar()
        self.iterator: RequiredInput[Iterable[_T]] = RequiredInput(self, "input", _t)

        # Iteration based I/O
        self._iterator_relay: IteratorRelay[_T] = IteratorRelay()
        self._accumulators: Dict[str, Accumulator[Any]] = {}

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

        for accumulator_relay in self._accumulators.values():
            self._system.remove_node(accumulator_relay)

        # Remove passthrough based I/O
        for input_relay in self._inputs.values():
            self._system.remove_node(input_relay)

        for output_relay in self._outputs.values():
            self._system.remove_node(output_relay)

        # Set the new system
        self._system = system

        # Add iteration based I/O
        self._system.add_node(self._iterator_relay)
        self._system.add_nodes(*self._accumulators.values())
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

    def add_accumulator(self, name: str) -> Accumulator[Any]:
        assert name not in self._accumulators, f"Accumulator with the name {name} already exists."
        assert (
            name not in self._outputs
        ), f"Accumulator name {name} conflicts with an existing output."
        new_accumulator_relay: Accumulator[Any] = Accumulator()
        new_accumulator_relay.name = name
        self._accumulators[name] = new_accumulator_relay
        self._system.add_node(new_accumulator_relay)
        return new_accumulator_relay

    def remove_accumulator(self, name: str) -> None:
        assert name in self._accumulators, f"Accumulator with the name {name} does not exist."
        self._system.remove_node(self._accumulators[name])
        del self._accumulators[name]

    def add_output(self, name: str) -> BasicRelay[Any]:
        assert name not in self._outputs, f"Output with the name {name} already exists."
        assert (
            name not in self._accumulators
        ), f"Output name {name} conflicts with an existing accumulator."
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
        accumulator_outputs: List[Connector] = [
            accumulator_relay._output for accumulator_relay in self._accumulators.values()
        ]
        passthrough_outputs: List[Connector] = [
            output_relay._output for output_relay in self._outputs.values()
        ]
        return accumulator_outputs + passthrough_outputs

    def run(self) -> None:
        for input_relay in self._inputs.values():
            input_relay.run()

        for accumulator_relay in self._accumulators.values():
            accumulator_relay.reset()

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

        for accumulator in self._accumulators.values():
            accumulator.validate()

    def generate_ast(self) -> ast.Module:
        body = []
        for accumulator in self._accumulators.values():
            accum_module = ast.parse(f"{accumulator._output.code_gen_name} = []")
            body.extend(accum_module.body)

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

        body.append(for_loop)

        return ast.Module(body=body, type_ignores=[])
