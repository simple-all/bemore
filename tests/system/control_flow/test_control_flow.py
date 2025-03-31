from typing import Dict, Tuple

from bemore import BasicSystem, Float, connect, generate_code
from bemore.control_flow.basic import Accumulator, For
from bemore.math.basic import Product
from bemore.types.basic import ConstantList


def make_for_loop_system() -> Tuple[BasicSystem, List[float]]:
    # Inner system multiplies inputs
    inner_sys = BasicSystem()
    producter = Product()
    appender = Append()
    inner_sys.add_nodes(producter, appender)

    # Outer system does the looping
    outer_sys = BasicSystem()
    my_list: List[float] = List()
    my_list.value = [0.5, 1.0, 2.0, 3.0, 3.5]

    new_list: List[float] = List()
    factor = Float(2.0)
    loop: For[float] = For()
    outer_sys.add_nodes(my_list, factor, loop, new_list)

    loop.system = inner_sys
    factor_relay = loop.add_input("factor")
    new_list_relay = loop.add_input("new_list")

    # Make all connections for the inner system
    connect(loop._iterator_relay._output, producter.input)
    connect(factor_relay._output, producter.input)
    connect(producter.output, appender.value)
    connect(new_list_relay._output, appender.list)

    # Make all connections for the outer system
    connect(my_list.output, loop.iterator)
    connect(factor.output, factor_relay._input)
    connect(new_list.output, new_list_relay._input)

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
