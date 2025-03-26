from typing import Type, Any, Callable, Dict, Optional


_to_type_dispatch: Dict[Any, Callable[[Type], bool]] = {}


def to_type_handler(to_what: Any) -> Callable:

    def _add_to_dispatch(handler: Callable[[Type], bool]) -> Callable[[Type], bool]:
        _to_type_dispatch[to_what] = handler
        return handler

    return _add_to_dispatch


def get_type_handler(to_type: Any) -> Optional[Callable[[Type], bool]]:
    return _to_type_dispatch.get(to_type)


@to_type_handler(Any)
def handle_to_any(from_type: Any) -> bool:
    # Any accepts literally anything
    return True


@to_type_handler(float)
def handle_to_float(from_type: Any) -> bool:
    # ints and floats are valid for floats
    valid_types = (int, float)
    return from_type in valid_types


def check_types(from_what: Any, to_what: Any) -> bool:
    # Handle simple cases first
    if from_what == to_what:
        return True

    handler = _to_type_dispatch.get(to_what)
    if handler:
        return handler(from_what)

    return False
