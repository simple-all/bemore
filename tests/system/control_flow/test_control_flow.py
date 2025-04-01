from typing import Dict, Tuple

from bemore import BasicSystem, Float, connect, generate_code
from bemore.control_flow.basic import For, If
from bemore.math.basic import Product, Modulo
from bemore.types.operators import Append
from bemore.types.basic import List, Int


def make_for_loop_system() -> Tuple[BasicSystem, List[float]]:
    # Inner system multiplies inputs
    inner_sys = BasicSystem("inner")
    producter = Product()
    appender: Append[float] = Append()
    inner_sys.add_nodes(producter, appender)

    # Outer system does the looping
    outer_sys = BasicSystem("outer")
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
    connect(loop._iterator_relay.output, producter.input)
    connect(factor_relay.output, producter.input)
    connect(producter.output, appender.value)
    connect(new_list_relay.output, appender.list)

    # Make all connections from the outer system to the inner system
    connect(my_list.output, loop.iterator, assert_same_system=False)
    connect(factor.output, factor_relay.input, assert_same_system=False)
    connect(new_list.output, new_list_relay.input, assert_same_system=False)

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


def make_for_if_loop_system() -> Tuple[BasicSystem, List[int], List[int]]:

    # True system, append even values
    even_sys = BasicSystem("even")
    even_append: Append[float] = Append()
    even_sys.add_node(even_append)

    # False system, append odd values
    odd_sys = BasicSystem("odd")
    odd_append: Append[float] = Append()
    odd_sys.add_node(odd_append)

    # If conditional
    if_sys = BasicSystem("if")
    if_node = If()
    if_node.true_system = odd_sys
    if_node.false_system = even_sys
    even_list_relay_pair = if_node.add_input("even")
    odd_list_relay_pair = if_node.add_input("odd")
    value_relay_pair = if_node.add_input("value")
    mod = Modulo()
    two = Int(2)
    if_sys.add_nodes(if_node, mod, two)

    # Outer system does the looping
    outer_sys = BasicSystem("outer")
    all_list: List[int] = List()
    all_list.value = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    even_list: List[int] = List()
    odd_list: List[int] = List()
    loop: For[float] = For()
    outer_sys.add_nodes(all_list, even_list, odd_list, loop)

    loop.system = if_sys
    even_list_relay = loop.add_input("even_list")
    odd_list_relay = loop.add_input("odd_list")

    # Make all connections from the if system to the even system
    connect(value_relay_pair.true.output, even_append.value, assert_same_system=False)
    connect(even_list_relay_pair.true.output, even_append.list, assert_same_system=False)

    # Make all connections from the if system to the odd system
    connect(value_relay_pair.false.output, odd_append.value, assert_same_system=False)
    connect(odd_list_relay_pair.false.output, odd_append.list, assert_same_system=False)

    # Make all connections for the if system
    connect(loop._iterator_relay.output, mod.dividend)
    connect(loop._iterator_relay.output, value_relay_pair.true.input, assert_same_system=False)
    connect(loop._iterator_relay.output, value_relay_pair.false.input, assert_same_system=False)
    connect(two.output, mod.divisor)
    connect(mod.output, if_node.condition)

    connect(even_list_relay.output, even_list_relay_pair.true.input, assert_same_system=False)
    connect(even_list_relay.output, even_list_relay_pair.false.input, assert_same_system=False)

    connect(odd_list_relay.output, odd_list_relay_pair.true.input, assert_same_system=False)
    connect(odd_list_relay.output, odd_list_relay_pair.false.input, assert_same_system=False)

    # Make all connections for the loop
    connect(all_list.output, loop.iterator, assert_same_system=False)
    connect(even_list.output, even_list_relay.input, assert_same_system=False)
    connect(odd_list.output, odd_list_relay.input, assert_same_system=False)

    return outer_sys, even_list, odd_list


def test_for_if_loop() -> None:

    system, even_list, odd_list = make_for_if_loop_system()
    system.run()

    assert even_list.output.get_value() == [0, 2, 4, 6, 8]
    assert odd_list.output.get_value() == [1, 3, 5, 7, 9]


def test_for_if_loop_code_gen() -> None:

    system, even_list, odd_list = make_for_if_loop_system()

    code = generate_code(system)

    globals: Dict[str, object] = {}
    locals: Dict[str, object] = {}
    exec(code, globals, locals)

    assert locals[even_list.output.code_gen_name] == [0, 2, 4, 6, 8]
    assert locals[odd_list.output.code_gen_name] == [1, 3, 5, 7, 9]
