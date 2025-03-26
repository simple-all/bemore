from typing import TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from noodle.core.connectors import Connector
    from noodle.core.node import Node

from typing import TYPE_CHECKING, Mapping, Union
import logging

if TYPE_CHECKING:
    from noodle.core.connectors import Connector
    from noodle.core.node import Node


def _get_qualified_name(obj: object) -> str:
    return f"{obj.__module__}.{obj.__class__.__name__}"


def _get_qualified_node_name(node: "Node") -> str:
    assert hasattr(node, "name"), f"Node {node} does not have an assigned name."
    qualified_name = _get_qualified_name(node)
    return f"{qualified_name}.{hash(node)}_{node.name}"


def _get_qualified_connector_name(connector: "Connector") -> str:
    assert hasattr(connector, "node"), f"Connector {connector} does not have an assigned node."
    assert hasattr(connector, "name"), f"Connector {connector} does not have an assigned name."
    node_name = _get_qualified_node_name(connector.node)
    qualified_name = _get_qualified_name(connector)
    return f"{node_name}.{qualified_name}_{hash(connector)}_{connector.name}"


class NodeLogger(logging.LoggerAdapter):
    def __init__(self, logger: logging.Logger, node: "Node"):
        super().__init__(logger)
        self._node = node

    def _log(
        self,
        *args,
        extra: Union[Mapping[str, object], None] = None,
        **kwargs,
    ) -> None:
        if extra is not None:
            assert "connector" not in extra, (
                "Keyword 'connector' is reserved in the extra logging fields "
                f"when using a {type(self)} logger."
            )

            # Maybe not necessary? Not garaunteed we can modify the incoming "extra" field.
            new_extra = {k: v for k, v in extra.items()}
        else:
            new_extra = {}

        new_extra["node"] = self._node

        return super()._log(*args, extra=extra, **kwargs)


class ConnectorLogger(logging.LoggerAdapter):
    def __init__(self, logger: logging.Logger, connector: "Connector"):
        super().__init__(logger)
        self._connector = connector

    def _log(
        self,
        *args,
        extra: Union[Mapping[str, object], None] = None,
        **kwargs,
    ) -> None:
        if extra is not None:
            assert "connector" not in extra, (
                "Keyword 'connector' is reserved in the extra logging fields "
                f"when using a {type(self)} logger."
            )

            # Maybe not necessary? Not garaunteed we can modify the incoming "extra" field.
            new_extra = {k: v for k, v in extra.items()}
        else:
            new_extra = {}

        new_extra["connector"] = self._connector

        return super()._log(*args, extra=extra, **kwargs)


# General loggers
def get_node_logger(node: "Node") -> NodeLogger:
    qualified_name = _get_qualified_node_name(node)
    logger = logging.getLogger(qualified_name)
    return NodeLogger(logger, node)


def get_connector_logger(connector: "Connector") -> ConnectorLogger:
    qualified_name = _get_qualified_connector_name(connector)
    logger = logging.getLogger(qualified_name)
    return ConnectorLogger(logger, connector)


# Runtime loggers
def get_node_runtime_logger(node: "Node") -> NodeLogger:
    qualified_name = _get_qualified_node_name(node)
    logger_name = f"{qualified_name}.runtime"
    logger = logging.getLogger(logger_name)
    return NodeLogger(logger, node)


def get_connector_runtime_logger(connector: "Connector") -> ConnectorLogger:
    qualified_name = _get_qualified_connector_name(connector)
    logger_name = f"{qualified_name}.runtime"
    logger = logging.getLogger(logger_name)
    return ConnectorLogger(logger, connector)


# Validation loggers
def get_node_validation_logger(node: "Node") -> NodeLogger:
    qualified_name = _get_qualified_node_name(node)
    logger_name = f"{qualified_name}.validation"
    logger = logging.getLogger(logger_name)
    return NodeLogger(logger, node)


def get_connector_validation_logger(connector: "Connector") -> ConnectorLogger:
    qualified_name = _get_qualified_connector_name(connector)
    logger_name = f"{qualified_name}.validation"
    logger = logging.getLogger(logger_name)
    return ConnectorLogger(logger, connector)
