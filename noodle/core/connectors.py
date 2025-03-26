from typing import Type, TypeVar, Generic, Optional, TYPE_CHECKING, Any, List, Protocol, Sequence
from enum import Enum, auto
from abc import ABC, abstractmethod
from noodle.core.logging import (
    get_connector_logger,
    get_connector_runtime_logger,
    get_connector_validation_logger,
)
from noodle.core.type_checking import check_types

if TYPE_CHECKING:
    from noodle.core.node import Node

_T = TypeVar("_T")
_T_co = TypeVar("_T_co", covariant=True)
_T_contra = TypeVar("_T_contra", contravariant=True)


class ConnectResult(Enum):
    SUCCESS = auto()
    ALREADY_CONNECTED = auto()
    FAIL = auto()


# Connector protocols


class Connector(Protocol):
    @property
    def node(self) -> "Node": ...

    @property
    def name(self) -> str: ...

    @property
    def signature(self) -> Any: ...
    def connect(self, other: Any) -> ConnectResult: ...
    def get_connections(self) -> Sequence["Connector"]: ...
    def validate(self): ...

    def __str__(self) -> str:
        return f"{self.__module__}.{self.__class__.__name__}[{self.signature}]"


class Input(Connector, Protocol[_T_contra]):
    def connect(self, other: "Output[_T_contra]") -> ConnectResult: ...


class Output(Connector, Protocol[_T_co]):
    def connect(self, other: "Input[_T_co]") -> ConnectResult: ...
    def get_value(self) -> _T_co: ...


def connect(output: Output[_T], input: Input[_T]):
    output.connect(input)
    input.connect(output)


# Input types


class SingleInput(Input[_T]):
    def __init__(self, node: "Node", name: str, signature: Any):
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
            self._logger.error(f"Nothing connected to input '{self.name}', cannot retreive value.")
            raise Exception()

        return self._connection.get_value()

    def validate(self):
        if self._connection:
            if not check_types(self._connection.signature, self.signature):
                self._validation_logger.warning(
                    f"Signature '{self._signature}' does not match connection's "
                    f"signature '{self._connection}'."
                )
        else:
            self._validation_logger.error(f"Nothing connected to input '{self.name}'.")


class OptionalInput(SingleInput[_T]):

    def get_value(self) -> Optional[_T]:
        if self._connection:
            return self._connection.get_value()

        return None

    def validate(self):
        if self._connection:
            if not check_types(self._connection.signature, self.signature):
                self._validation_logger.warning(
                    f"Signature '{self._signature}' does not match connection's "
                    f"signature '{self._connection}'."
                )


class MultiInput(Input[_T]):
    def __init__(self, node: "Node", name: str, signature: Any):
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

    def validate(self):
        for connection in self._connections:
            if not check_types(connection.signature, self.signature):
                self._validation_logger.warning(
                    f"Signature '{self._signature}' does not match connection's "
                    f"signature '{connection}'."
                )


class RequiredMultiInput(MultiInput[_T]):

    def get_value(self) -> List[_T]:
        if not self._connections:
            self._logger.error(f"Nothing connected to input '{self.name}', cannot retreive value.")
            raise Exception()

        return [connection.get_value() for connection in self._connections]

    def validate(self):
        super().validate()
        if not self._connections:
            self._validation_logger.error(f"Nothing connected to input '{self.name}'.")


class OptionalMultiInput(MultiInput[_T]):

    def get_value(self) -> List[_T]:
        return [connection.get_value() for connection in self._connections]

    def validate(self):
        pass


# Output types
NULL_VALUE_SENTINEL = object()


class SharedOutput(Output[_T]):
    def __init__(self, node: "Node", name: str, signature: Any):
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

    @property
    def node(self) -> "Node":
        return self._node

    @property
    def signature(self) -> Any:
        return self._signature

    def get_value(self) -> _T:
        assert self._value is not NULL_VALUE_SENTINEL
        return self._value

    def set_value(self, value: _T):
        self._value = value

    def connect(self, other: "Input[_T]") -> ConnectResult:
        if input in self._connections:
            return ConnectResult.ALREADY_CONNECTED

        self._connections.append(other)
        return ConnectResult.SUCCESS

    def get_connections(self) -> Sequence[Connector]:
        return self._connections

    def validate(self):
        pass
