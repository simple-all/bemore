import ast
from typing import Any, Dict, Iterable, List, Protocol, TypeVar, runtime_checkable

import networkx as nx

from bemore.core.code_gen import CodeGeneratorProto
from bemore.core.connectors import OutputConnectorProto
from bemore.core.node import NodeProto

T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)


@runtime_checkable
class InputProto(NodeProto, Protocol[T_contra]):

    output: OutputConnectorProto[Any]

    @property
    def is_required(self) -> bool:
        raise NotImplementedError

    # @property
    # def output(self) -> OutputConnectorProto: ...

    def set_value(self, value: T_contra) -> None:
        raise NotImplementedError()


@runtime_checkable
class OutputProto(NodeProto, Protocol[T_co]):
    def get_value(self) -> T_co:
        raise NotImplementedError()


class SystemProto(CodeGeneratorProto, Protocol):
    @property
    def name(self) -> str: ...

    @name.setter
    def name(self, name: str) -> None: ...

    @property
    def nodes(self) -> List[NodeProto]: ...

    def add_node(self, node: NodeProto) -> None: ...
    def add_nodes(self, *nodes: NodeProto) -> None: ...
    def get_inputs(self) -> Iterable[InputProto[Any]]: ...
    def get_outputs(self) -> Iterable[OutputProto[Any]]: ...
    def remove_node(self, node: NodeProto) -> None: ...
    def remove_nodes(self, *nodes: NodeProto) -> None: ...
    def validate(self) -> None: ...
    def run(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]: ...


class BasicSystem(SystemProto):
    def __init__(self, name: str) -> None:
        self._name = name
        self._nodes: List[NodeProto] = []

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def nodes(self) -> List[NodeProto]:
        return self._nodes

    def add_node(self, node: NodeProto) -> None:
        assert node not in self._nodes
        node.system = self
        self._nodes.append(node)

    def remove_node(self, node: NodeProto) -> None:
        assert node in self._nodes
        node.system = None
        self._nodes.remove(node)

    def add_nodes(self, *args: NodeProto) -> None:
        for node in args:
            self.add_node(node)

    def remove_nodes(self, *nodes: NodeProto) -> None:
        for node in nodes:
            self.remove_node(node)

    def get_inputs(self) -> Iterable[InputProto[Any]]:
        for node in self._nodes:
            if isinstance(node, InputProto):
                yield node

    def get_outputs(self) -> Iterable[OutputProto[Any]]:
        for node in self._nodes:
            if isinstance(node, OutputProto):
                yield node

    def validate(self) -> None:
        for node in self._nodes:
            assert node.system is self, f"Node {node} does not belong to this system."
            node.validate()

    def _construct_node_graph(self) -> nx.DiGraph:  # type: ignore
        # Construct the node graph
        graph = nx.DiGraph()  # type: ignore
        for node in self._nodes:
            graph.add_node(node)

        for node in self._nodes:
            for input in node.get_inputs():
                for output in input.get_connections():
                    for other in self._nodes:
                        if node is other:
                            continue

                        if output in other.get_outputs():
                            graph.add_edge(other, node)

        return graph

    def run(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        graph = self._construct_node_graph()

        cycles = list(nx.simple_cycles(graph))
        assert not cycles

        input_map = {node.name: node for node in self.get_inputs()}

        required_names = set(name for name, node in input_map.items() if node.is_required)
        given_names = set(kwargs.keys())

        missing_inputs = required_names.difference(given_names)

        if missing_inputs:
            raise Exception(f"Missing inputs: {missing_inputs}.")

        for name, node in input_map.items():
            node.set_value(kwargs.get(name))

        for node in nx.topological_sort(graph):
            node.run()

        outputs = {node.name: node.get_value for node in self.get_outputs()}

        return outputs

    def generate_ast(self) -> ast.Module:
        graph = self._construct_node_graph()

        cycles = list(nx.simple_cycles(graph))
        assert not cycles

        gen_module = ast.Module(body=[], type_ignores=[])

        next_node: NodeProto
        for next_node in nx.topological_sort(graph):
            node_ast = next_node.generate_ast()
            gen_module.body.extend(node_ast.body)

        # Surface imports to the top
        imports = []
        for node in ast.walk(gen_module):
            if isinstance(node, ast.Import):
                imports.append(node)

        gen_module = ast.Module(
            body=imports + gen_module.body,
            type_ignores=gen_module.type_ignores,
        )

        return gen_module
