import ast
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, List, Optional, Protocol, Sequence, Tuple, TypeVar

from bemore.core.code_gen import CodeGeneratorProto
from bemore.core.logging import (
    get_connector_logger,
    get_connector_runtime_logger,
    get_connector_validation_logger,
)
from bemore.core.type_checking import check_types

if TYPE_CHECKING:
    from bemore.core.node import NodeProto

T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)


class ConnectResult(Enum):
    SUCCESS = auto()
    ALREADY_CONNECTED = auto()
    FAIL = auto()


# Connector protocols


class ConnectorProto(CodeGeneratorProto, Protocol):

    @property
    def node(self) -> "NodeProto": ...

    name: str

    @property
    def signature(self) -> Any: ...

    @property
    def code_gen_name(self) -> str: ...

    def connect(self, other: Any) -> ConnectResult: ...
    def get_connections(self) -> Sequence["ConnectorProto"]: ...
    def validate(self) -> None: ...

    def __str__(self) -> str:
        return f"{self.__module__}.{self.__class__.__name__}[{self.signature}]"


class InputConnectorProto(ConnectorProto, Protocol[T_contra]):
    def connect(self, other: "OutputConnectorProto[T_contra]") -> ConnectResult: ...
    def get_value(self) -> Any: ...


class RequiredInputConnectorProto[T](InputConnectorProto[T]):
    def get_value(self) -> T:
        raise NotImplementedError()


class OptionalConnectorProto[T](InputConnectorProto[T]):
    def get_value(self) -> Optional[T]: ...


class OutputConnectorProto(ConnectorProto, Protocol[T_co]):
    def connect(self, other: "InputConnectorProto[T_co]") -> ConnectResult: ...
    def set_value(self, value: Any) -> None: ...
    def get_value(self) -> T_co: ...


def connect[T](
    output: OutputConnectorProto[T],
    input: InputConnectorProto[T],
) -> Tuple[ConnectResult, ConnectResult]:
    if output.node.system is not input.node.system:
        raise Exception("Connectors do not belong to the same system.")

    output_result = output.connect(input)
    input_result = input.connect(output)

    return output_result, input_result


# Input types


class SingleInput[T](InputConnectorProto[T]):
    def __init__(self, node: "NodeProto", name: str, signature: Any) -> None:
        self._node = node
        self._name = name
        self._signature = signature
        self._connection: Optional[OutputConnectorProto[T]] = None

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
    def node(self) -> "NodeProto":
        return self._node

    @property
    def signature(self) -> Any:
        return self._signature

    def connect(self, other: "OutputConnectorProto[T]") -> ConnectResult:
        self._connection = other
        return ConnectResult.SUCCESS

    def get_connections(self) -> Sequence[ConnectorProto]:
        if self._connection:
            return [self._connection]

        return []


class RequiredInput[T](SingleInput[T]):

    def get_value(self) -> T:
        if self._connection is None:
            self._logger.error(
                f"Nothing connected to input '{self.name}' of node {self.node.name}, "
                "cannot retrieve value."
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


class OptionalInput[T](SingleInput[T]):

    def get_value(self) -> Optional[T]:
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


class MultiInput[T](InputConnectorProto[T]):
    def __init__(self, node: "NodeProto", name: str, signature: Any) -> None:
        self._node = node
        self._name = name
        self._signature = signature
        self._connections: List[OutputConnectorProto[T]] = []

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
    def node(self) -> "NodeProto":
        return self._node

    @property
    def signature(self) -> Any:
        return self._signature

    def connect(self, other: "OutputConnectorProto[T]") -> ConnectResult:
        if other in self._connections:
            return ConnectResult.ALREADY_CONNECTED

        self._connections.append(other)
        return ConnectResult.SUCCESS

    def get_connections(self) -> Sequence[ConnectorProto]:
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


class RequiredMultiInput[T](MultiInput[T]):

    def get_value(self) -> List[T]:
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


class OptionalMultiInput[T](MultiInput[T]):

    def get_value(self) -> List[T]:
        return [connection.get_value() for connection in self._connections]

    def validate(self) -> None:
        pass


# Output types
NULL_VALUE_SENTINEL = object()


class BasicOutput[T](OutputConnectorProto[T]):
    def __init__(self, node: "NodeProto", name: str, signature: Any) -> None:
        self._node = node
        self._name = name
        self._signature = signature
        self._connections: List[InputConnectorProto[T]] = []
        self._value: T = NULL_VALUE_SENTINEL  # type: ignore

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
    def node(self) -> "NodeProto":
        return self._node

    @property
    def signature(self) -> Any:
        return self._signature

    def get_value(self) -> T:
        assert self._value is not NULL_VALUE_SENTINEL
        return self._value

    def set_value(self, value: T) -> None:
        self._value = value

    def connect(self, other: "InputConnectorProto[T]") -> ConnectResult:
        if other in self._connections:
            return ConnectResult.ALREADY_CONNECTED

        self._connections.append(other)
        return ConnectResult.SUCCESS

    def get_connections(self) -> Sequence[ConnectorProto]:
        return self._connections

    def validate(self) -> None:
        pass

    def generate_ast(self) -> ast.Module:
        return ast.Module(body=[], type_ignores=[])

    @property
    def code_gen_name(self) -> str:
        return f"{self.name}_{hash(self)}"
