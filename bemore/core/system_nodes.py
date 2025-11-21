from ast import Module
from typing import Optional, Any
from bemore.core.typing import DynamicTypeVar
from bemore.core.connectors import RequiredInput
from bemore.core.logging import get_node_logger, get_node_runtime_logger, get_node_validation_logger
from bemore.core.system import InputProto, OutputProto, SystemProto
from bemore.core.connectors import BasicOutput, InputConnectorProto, OutputConnectorProto
from collections.abc import Collection


class KeywordInput[_T](InputProto[_T]):
    def __init__(self, name: str):
        self._name = name
        self._system: Optional["SystemProto"] = None
        self._logger = get_node_logger(self)
        self._runtime_logger = get_node_runtime_logger(self)
        self._validation_logger = get_node_validation_logger(self)

        self.output: BasicOutput[_T] = BasicOutput(self, "output", DynamicTypeVar())

    @property
    def is_required(self) -> bool:
        return False

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

    def run(self) -> None:
        # Nothing to do
        pass

    def get_inputs(self) -> Collection[InputConnectorProto[Any]]:
        return []

    def get_outputs(self) -> Collection[OutputConnectorProto[_T]]:
        return [self.output]

    def validate(self) -> None:
        # Nothing to validate
        return

    def set_value(self, value: _T) -> None:
        self.output.set_value(value)

    def generate_ast(self) -> Module:
        return Module(body=[], type_ignores=[])


class PositionalInput[_T](OutputProto[_T]):
    def __init__(self, position: int = 0):
        self._name = type(self).__name__
        self._system: Optional["SystemProto"] = None
        self._logger = get_node_logger(self)
        self._runtime_logger = get_node_runtime_logger(self)
        self._validation_logger = get_node_validation_logger(self)

        self._position: int = position
        self._value: Optional[_T] = None

    @property
    def is_required(self) -> bool:
        return True

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

    def validate(self) -> None:
        # Nothing to validate
        return

    def get_value(self) -> _T:
        if self._value is None:
            raise Exception("Required positional input is None")

        return self._value


class Output[_T](OutputProto[_T]):
    def __init__(self, name: str):
        self._name = name
        self._system: Optional["SystemProto"] = None
        self._logger = get_node_logger(self)
        self._runtime_logger = get_node_runtime_logger(self)
        self._validation_logger = get_node_validation_logger(self)

        self.input: RequiredInput[_T] = RequiredInput(self, "input", DynamicTypeVar())

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

    def run(self) -> None:
        # Nothing to do
        pass

    def get_inputs(self) -> Collection[InputConnectorProto[_T]]:
        return [self.input]

    def get_outputs(self) -> Collection[OutputConnectorProto[Any]]:
        return []

    def validate(self) -> None:
        # Nothing to validate
        return

    def get_value(self) -> _T:
        return self.input.get_value()

    def generate_ast(self) -> Module:
        return Module(body=[], type_ignores=[])
