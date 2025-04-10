from typing import Iterable, Protocol

from bemore.core.code_gen import CodeGenerator
from bemore.core.connectors import Connector
from bemore.core.logging import get_node_logger, get_node_runtime_logger, get_node_validation_logger


class Node(CodeGenerator, Protocol):

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, name: str) -> None: ...

    def run(self) -> None: ...

    def get_inputs(self) -> Iterable[Connector]: ...

    def get_outputs(self) -> Iterable[Connector]: ...

    def is_input(self, connector: Connector) -> bool:
        return connector in self.get_inputs()

    def is_output(self, connector: Connector) -> bool:
        return connector in self.get_outputs()

    def validate(self) -> None: ...


class BasicNode(Node):

    def __init__(self) -> None:
        self._name = type(self).__name__
        self._logger = get_node_logger(self)
        self._runtime_logger = get_node_runtime_logger(self)
        self._validation_logger = get_node_validation_logger(self)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name
