from typing import TYPE_CHECKING, Optional, Protocol, Any
from collections.abc import Collection

from bemore.core.code_gen import CodeGenerator
from bemore.core.connectors import ConnectorProto, InputConnectorProto, OutputConnectorProto
from bemore.core.logging import get_node_logger, get_node_runtime_logger, get_node_validation_logger

if TYPE_CHECKING:
    from bemore.core.system import SystemProto


class Node(CodeGenerator, Protocol):

    @property
    def name(self) -> str:
        raise NotImplementedError()

    @name.setter
    def name(self, name: str) -> None:
        raise NotImplementedError()

    @property
    def system(self) -> Optional["SystemProto"]:
        raise NotImplementedError()

    @system.setter
    def system(self, system: Optional["SystemProto"]) -> None:
        raise NotImplementedError()

    def run(self) -> None:
        raise NotImplementedError()

    def get_inputs(self) -> Collection[InputConnectorProto[Any]]:
        raise NotImplementedError()

    def get_outputs(self) -> Collection[OutputConnectorProto[Any]]:
        raise NotImplementedError()

    def is_input(self, connector: ConnectorProto) -> bool:
        return connector in self.get_inputs()

    def is_output(self, connector: ConnectorProto) -> bool:
        return connector in self.get_outputs()

    def validate(self) -> None:
        raise NotImplementedError()


class BasicNode(Node):

    def __init__(self) -> None:
        self._name = type(self).__name__
        self._system: Optional["SystemProto"] = None
        self._logger = get_node_logger(self)
        self._runtime_logger = get_node_runtime_logger(self)
        self._validation_logger = get_node_validation_logger(self)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def system(self) -> Optional["SystemProto"]:
        return self._system

    @system.setter
    def system(self, system: Optional["SystemProto"]) -> None:
        self._system = system
