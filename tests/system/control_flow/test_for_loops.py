from typing import Dict, Tuple

from bemore import BasicSystem, Float, connect, generate_code
from bemore.control_flow.for_loop import For
from bemore.math.basic import Product
from bemore.types.basic import List
from bemore.types.operators import Append


def make_for_loop_system() -> Tuple[BasicSystem, List[float]]:
    # Inner system multiplies inputs
    producter = Product()
    appender: Append[float] = Append()

    # Outer system does the looping
    outer_sys = BasicSystem("outer")
    my_list: List[float] = List()
    my_list.value = [0.5, 1.0, 2.0, 3.0, 3.5]

    new_list: List[float] = List()
    factor = Float(2.0)
    loop: For[float] = For()

    inner_sys = loop.subsystem
    inner_sys.add_nodes(producter, appender)
    outer_sys.add_nodes(my_list, factor, loop, new_list)

    iterator_input, subsystem_iterator_node = loop.add_input("iterator", list)
    loop.make_iterable("iterator")
    factor_input, subsystem_factor_node = loop.add_input("factor", float)
    new_list_input, subsystem_new_list_node = loop.add_input("new_list", list)

    # Make all connections for the inner system
    connect(producter.output, appender.value)
    connect(subsystem_new_list_node.output, appender.list)
    connect(subsystem_iterator_node.output, producter.input)
    connect(subsystem_factor_node.output, producter.input)

    # Make all connections for the outer system
    connect(my_list.output, iterator_input)
    connect(factor.output, factor_input)
    connect(new_list.output, new_list_input)

    return outer_sys, new_list


def test_for_loop() -> None:

    system, new_list = make_for_loop_system()
    system.run()

    assert new_list.output.get_value() == [1.0, 2.0, 4.0, 6.0, 7.0]


def test_for_loop_code_gen() -> None:
    system, new_list = make_for_loop_system()

    code = generate_code(system)

    globals: Dict[str, object] = {}
    locals: Dict[str, object] = {}
    exec(code, globals, locals)

    assert locals[new_list.output.code_gen_name] == [1.0, 2.0, 4.0, 6.0, 7.0]
