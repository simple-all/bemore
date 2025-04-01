import ast
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, List, Optional, Protocol, Sequence, Tuple, TypeVar

from bemore import CodeGenerator
from bemore.core.logging import (
    get_connector_logger,
    get_connector_runtime_logger,
    get_connector_validation_logger,
)
from bemore.core.type_checking import check_types

if TYPE_CHECKING:
    from bemore.core.node import Node

_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)
_T_contra = TypeVar("_T_contra", contravariant=True)


class ConnectResult(Enum):
    SUCCESS = auto()
    ALREADY_CONNECTED = auto()
    FAIL = auto()


# Connector protocols


class Connector(CodeGenerator, Protocol):

    @property
    def node(self) -> "Node": ...

    name: str

    @property
    def signature(self) -> Any: ...

    @property
    def code_gen_name(self) -> str: ...

    def connect(self, other: Any) -> ConnectResult: ...
    def get_connections(self) -> Sequence["Connector"]: ...
    def validate(self) -> None: ...

    def __str__(self) -> str:
        return f"{self.__module__}.{self.__class__.__name__}[{self.signature}]"


class Input(Connector, Protocol[_T_contra]):
    def connect(self, other: "Output[_T_contra]") -> ConnectResult: ...


class Output(Connector, Protocol[_T_co]):
    def connect(self, other: "Input[_T_co]") -> ConnectResult: ...
    def get_value(self) -> _T_co: ...


def connect(
    output: Output[_T],
    input: Input[_T],
    assert_same_system: bool = True,
) -> Tuple[ConnectResult, ConnectResult]:
    if assert_same_system and output.node.system is not input.node.system:
        raise Exception("Connectors do not belong to the same system.")
    output_result = output.connect(input)
    input_result = input.connect(output)

    return output_result, input_result


# Input types


class SingleInput(Input[_T]):
    def __init__(self, node: "Node", name: str, signature: Any) -> None:
        self._node = node
        self._name = name
        self._signature = signature
        self._connection: Optional[Output[_T]] = None

        self._logger = get_connector_logger(self)
        self._runtime_logger = get_connector_runtime_logger(self)
        self._validation_logger = get_connector_validation_logger(self)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def node(self) -> "Node":
        return self._node

    @property
    def signature(self) -> Any:
        return self._signature

    def connect(self, other: "Output[_T]") -> ConnectResult:
        self._connection = other
        return ConnectResult.SUCCESS

    def get_connections(self) -> Sequence[Connector]:
        if self._connection:
            return [self._connection]

        return []


class RequiredInput(SingleInput[_T]):

    def get_value(self) -> _T:
        if self._connection is None:
            self._logger.error(
                f"Nothing connected to input '{self.name}' of node {self.node.name}, "
                "cannot retreive value."
            )
            raise Exception()

        return self._connection.get_value()

    def validate(self) -> None:
        if self._connection:
            if not check_types(self._connection.signature, self.signature):
                self._validation_logger.warning(
                    f"Signature '{self._signature}' does not match connection's "
                    f"signature '{self._connection}'."
                )
        else:
            self._validation_logger.error(f"Nothing connected to input '{self.name}'.")

    def generate_ast(self) -> ast.Module:
        # Required single input delegates code gen to its connection
        return ast.Module(body=[], type_ignores=[])

    @property
    def code_gen_name(self) -> str:
        assert self._connection is not None
        return self._connection.code_gen_name


class OptionalInput(SingleInput[_T]):

    def get_value(self) -> Optional[_T]:
        if self._connection:
            return self._connection.get_value()

        return None

    def validate(self) -> None:
        if self._connection:
            if not check_types(self._connection.signature, self.signature):
                self._validation_logger.warning(
                    f"Signature '{self._signature}' does not match connection's "
                    f"signature '{self._connection}'."
                )

    def generate_ast(self) -> ast.Module:
        # Optional single input delegates code gen to its connection if connected
        if self._connection:
            return ast.Module(body=[], type_ignores=[])

        line = f"{self.code_gen_name} = None\n"
        return ast.parse(line)

    @property
    def code_gen_name(self) -> str:
        if self._connection:
            return self._connection.code_gen_name

        return f"{self.name}_{hash(self)}"


class MultiInput(Input[_T]):
    def __init__(self, node: "Node", name: str, signature: Any) -> None:
        self._node = node
        self._name = name
        self._signature = signature
        self._connections: List[Output[_T]] = []

        self._logger = get_connector_logger(self)
        self._runtime_logger = get_connector_runtime_logger(self)
        self._validation_logger = get_connector_validation_logger(self)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def node(self) -> "Node":
        return self._node

    @property
    def signature(self) -> Any:
        return self._signature

    def connect(self, other: "Output[_T]") -> ConnectResult:
        if other in self._connections:
            return ConnectResult.ALREADY_CONNECTED

        self._connections.append(other)
        return ConnectResult.SUCCESS

    def get_connections(self) -> Sequence[Connector]:
        return self._connections

    def validate(self) -> None:
        for connection in self._connections:
            if not check_types(connection.signature, self.signature):
                self._validation_logger.warning(
                    f"Signature '{self._signature}' does not match connection's "
                    f"signature '{connection}'."
                )

    def generate_ast(self) -> ast.Module:
        input_vars = ", ".join([connection.code_gen_name for connection in self._connections])
        line = f"{self.code_gen_name} = [{input_vars}]\n"
        return ast.parse(line)

    @property
    def code_gen_name(self) -> str:
        return f"{self.name}_{hash(self)}"


class RequiredMultiInput(MultiInput[_T]):

    def get_value(self) -> List[_T]:
        if not self._connections:
            self._logger.error(
                f"Nothing connected to input '{self.name}' of node {self.node}, "
                "cannot retreive value."
            )
            raise Exception()

        return [connection.get_value() for connection in self._connections]

    def validate(self) -> None:
        super().validate()
        if not self._connections:
            self._validation_logger.error(f"Nothing connected to input '{self.name}'.")


class OptionalMultiInput(MultiInput[_T]):

    def get_value(self) -> List[_T]:
        return [connection.get_value() for connection in self._connections]

    def validate(self) -> None:
        pass


# Output types
NULL_VALUE_SENTINEL = object()


class BasicOutput(Output[_T]):
    def __init__(self, node: "Node", name: str, signature: Any) -> None:
        self._node = node
        self._name = name
        self._signature = signature
        self._connections: List[Input[_T]] = []
        self._value: _T = NULL_VALUE_SENTINEL  # type: ignore

        self._logger = get_connector_logger(self)
        self._runtime_logger = get_connector_runtime_logger(self)
        self._validation_logger = get_connector_validation_logger(self)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def node(self) -> "Node":
        return self._node

    @property
    def signature(self) -> Any:
        return self._signature

    def get_value(self) -> _T:
        assert self._value is not NULL_VALUE_SENTINEL
        return self._value

    def set_value(self, value: _T) -> None:
        self._value = value

    def connect(self, other: "Input[_T]") -> ConnectResult:
        if other in self._connections:
            return ConnectResult.ALREADY_CONNECTED

        self._connections.append(other)
        return ConnectResult.SUCCESS

    def get_connections(self) -> Sequence[Connector]:
        return self._connections

    def validate(self) -> None:
        pass

    def generate_ast(self) -> ast.Module:
        return ast.Module(body=[], type_ignores=[])

    @property
    def code_gen_name(self) -> str:
        return f"{self.name}_{hash(self)}"


# Relays


class InputRelay(RequiredInput[_T]):
    def __init__(self, node: "Node", name: str, signature: Any) -> None:
        super().__init__(node, name, signature)
        self._output_relay: Optional["OutputRelay[_T]"] = None

    def connect_relay(self, other: "OutputRelay[_T]") -> None:
        self._output_relay = other


class OutputRelay(Output[_T]):
    def __init__(self, node: "Node", name: str, signature: Any) -> None:
        self._node = node
        self._name = name
        self._signature = signature
        self._connections: List[Connector] = []
        self._input_relay: Optional["InputRelay[_T]"] = None

    def connect(self, other: "Input[_T]") -> ConnectResult:
        if other in self._connections:
            return ConnectResult.ALREADY_CONNECTED

        self._connections.append(other)
        return ConnectResult.SUCCESS

    def get_connections(self) -> Sequence["Connector"]:
        return self._connections

    def connect_relay(self, other: "InputRelay[_T]") -> None:
        self._input_relay = other

    def get_value(self) -> _T:
        assert self._input_relay is not None
        return self._input_relay.get_value()

    @property
    def node(self) -> "Node":
        return self._node

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def signature(self) -> Any:
        return self._signature

    @property
    def code_gen_name(self) -> str:
        assert self._input_relay is not None
        return self._input_relay.code_gen_name

    def generate_ast(self) -> ast.Module:
        return ast.Module(body=[], type_ignores=[])

    def validate(self) -> None:
        pass


def connect_relays(input_relay: InputRelay[_T], output_relay: OutputRelay[_T]) -> None:
    assert input_relay.node is output_relay.node
    input_relay.connect_relay(output_relay)
    output_relay.connect_relay(input_relay)
