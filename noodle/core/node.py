from typing import TYPE_CHECKING, Iterable, Optional, Protocol

from noodle.core.code_gen import CodeGenerator
from noodle.core.connectors import Connector
from noodle.core.logging import get_node_logger, get_node_runtime_logger, get_node_validation_logger

if TYPE_CHECKING:
    from noodle.core.system import System


class Node(CodeGenerator, Protocol):

    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, name: str) -> None: ...

    @property
    def system(self) -> Optional["System"]: ...

    @system.setter
    def system(self, system: Optional["System"]) -> None: ...

    def run(self) -> None: ...

    def get_inputs(self) -> Iterable[Connector]: ...

    def get_outputs(self) -> Iterable[Connector]: ...

    def validate(self) -> None: ...


class BasicNode(Node):

    def __init__(self) -> None:
        self._name = type(self).__name__
        self._system: Optional["System"] = None
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
    def system(self) -> Optional["System"]:
        return self._system

    @system.setter
    def system(self, system: Optional["System"]) -> None:
        self._system = system
