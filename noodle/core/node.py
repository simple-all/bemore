from noodle.core.connectors import Input, Output, Connector
from typing import Iterable
from abc import ABC, abstractmethod
from noodle.core.logging import get_node_logger, get_node_runtime_logger, get_node_validation_logger


class Node(ABC):

    def __init__(self) -> None:
        self._name = type(self).__name__
        self._logger = get_node_logger(self)
        self._runtime_logger = get_node_runtime_logger(self)
        self._validation_logger = get_node_validation_logger(self)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @abstractmethod
    def run(self) -> None: ...

    @abstractmethod
    def get_inputs(self) -> Iterable[Connector]: ...

    @abstractmethod
    def get_outputs(self) -> Iterable[Connector]: ...

    @abstractmethod
    def validate(self) -> None: ...

    def __str__(self) -> str:
        return self._name
