from typing import List, Protocol

import networkx as nx

from noodle.core.node import Node


class System(Protocol):
    @property
    def nodes(self) -> List[Node]: ...
    def add_node(self, node: Node) -> None: ...
    def add_nodes(self, *nodes: Node) -> None: ...
    def validate(self) -> None: ...
    def run(self) -> None: ...


class BasicSystem(System):
    def __init__(self) -> None:
        self._nodes: List[Node] = []

    @property
    def nodes(self) -> List[Node]:
        return self._nodes

    def add_node(self, node: Node) -> None:
        assert node not in self._nodes
        self._nodes.append(node)

    def add_nodes(self, *args: Node) -> None:
        for node in args:
            self.add_node(node)

    def validate(self) -> None:
        for node in self._nodes:
            node.validate()

    def run(self) -> None:
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

        cycles = list(nx.simple_cycles(graph))
        assert not cycles

        for node in nx.topological_sort(graph):
            node.run()
