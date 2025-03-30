from typing import Dict, Tuple

from bemore import BasicSystem, Float, connect, generate_code
from bemore.control_flow.basic import Accumulator, For
from bemore.math.basic import Product
from bemore.types.basic import ConstantList


def make_for_loop_system() -> Tuple[BasicSystem, Accumulator[float]]:
    # Inner system multiplies inputs
    inner_sys = BasicSystem()
    producter = Product()
    inner_sys.add_node(producter)

    # Outer system does the looping
    outer_sys = BasicSystem()
    my_list = ConstantList([0.5, 1.0, 2.0, 3.0, 3.5])
    factor = Float(2.0)
    loop: For[float] = For()
    outer_sys.add_nodes(my_list, factor, loop)

    loop.system = inner_sys
    factor_relay = loop.add_input("factor")
    accumulator_relay: Accumulator[float] = loop.add_accumulator("accumulator")

    # Make all connections for the inner system
    connect(loop._iterator_relay._output, producter.input)
    connect(factor_relay._output, producter.input)
    connect(producter.output, accumulator_relay._input)

    # Make all connections for the outer system
    connect(my_list.output, loop.iterator)
    connect(factor.output, factor_relay._input)

    return outer_sys, accumulator_relay


def test_for_loop() -> None:

    system, accumulator_relay = make_for_loop_system()
    system.run()

    assert accumulator_relay._output.get_value() == [1.0, 2.0, 4.0, 6.0, 7.0]


def test_for_loop_code_gen() -> None:
    system, accumulator_relay = make_for_loop_system()

    code = generate_code(system)

    globals: Dict[str, object] = {}
    locals: Dict[str, object] = {}
    exec(code, globals, locals)

    assert locals[accumulator_relay._output.code_gen_name] == [1.0, 2.0, 4.0, 6.0, 7.0]
