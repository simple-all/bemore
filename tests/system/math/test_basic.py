from typing import Dict

import pytest

from bemore import BasicSystem, Float, Int, connect, generate_code
from bemore.math.basic import Divide, Modulo, Product, Subtract, Sum

FLOAT_ABS_TOL = 1e-12


def test_sum_floats() -> None:
    a = Float(1.2)
    b = Float(4.75)
    c = Float(9.87)
    summer = Sum()

    connect(a.output, summer.input)
    connect(b.output, summer.input)
    connect(c.output, summer.input)

    system = BasicSystem()
    system.add_nodes(a, b, c, summer)

    system.validate()
    system.run()

    assert summer.output.get_value() == pytest.approx(1.2 + 4.75 + 9.87, abs=FLOAT_ABS_TOL)


def test_code_gen() -> None:
    a = Float(1.2)
    b = Float(4.75)
    c = Float(9.87)
    summer = Sum()

    connect(a.output, summer.input)
    connect(b.output, summer.input)
    connect(c.output, summer.input)

    system = BasicSystem()
    system.add_nodes(a, b, c, summer)

    code = generate_code(system)

    globals: Dict[str, object] = {}
    locals: Dict[str, object] = {}
    exec(code, globals, locals)

    assert locals[summer.output.code_gen_name] == pytest.approx(
        1.2 + 4.75 + 9.87,
        abs=FLOAT_ABS_TOL,
    )


def test_sum_ints() -> None:
    a = Int(1)
    b = Int(4)
    c = Int(9)

    summer = Sum()

    connect(a.output, summer.input)
    connect(b.output, summer.input)
    connect(c.output, summer.input)

    system = BasicSystem()
    system.add_nodes(a, b, c, summer)

    system.validate()
    system.run()

    assert summer.output.get_value() == 1 + 4 + 9


def test_product_floats() -> None:
    a = Float(1.2)
    b = Float(4.75)
    c = Float(9.87)
    proder = Product()

    connect(a.output, proder.input)
    connect(b.output, proder.input)
    connect(c.output, proder.input)

    system = BasicSystem()
    system.add_nodes(a, b, c, proder)

    system.validate()
    system.run()

    assert proder.output.get_value() == pytest.approx(1.2 * 4.75 * 9.87, abs=FLOAT_ABS_TOL)


def test_product_ints() -> None:
    a = Int(2)
    b = Int(4)
    c = Int(9)
    proder = Product()

    connect(a.output, proder.input)
    connect(b.output, proder.input)
    connect(c.output, proder.input)

    system = BasicSystem()
    system.add_nodes(a, b, c, proder)

    system.validate()
    system.run()

    assert proder.output.get_value() == 2 * 4 * 9


def test_subtract_floats() -> None:
    a = Float(1.2)
    b = Float(4.75)
    subtracter = Subtract()

    connect(a.output, subtracter.left)
    connect(b.output, subtracter.right)

    system = BasicSystem()
    system.add_nodes(a, b, subtracter)

    system.validate()
    system.run()

    assert subtracter.output.get_value() == 1.2 - 4.75


def test_subtract_ints() -> None:
    a = Int(13)
    b = Int(-12)
    subtracter = Subtract()

    connect(a.output, subtracter.left)
    connect(b.output, subtracter.right)

    system = BasicSystem()
    system.add_nodes(a, b, subtracter)

    system.validate()
    system.run()

    assert subtracter.output.get_value() == 13 - -12


def test_divide_floats() -> None:
    a = Float(1.2)
    b = Float(4.75)
    divider = Divide()

    connect(a.output, divider.numerator)
    connect(b.output, divider.denominator)

    system = BasicSystem()
    system.add_nodes(a, b, divider)

    system.validate()
    system.run()

    assert divider.output.get_value() == 1.2 / 4.75


def test_divide_ints() -> None:
    a = Int(7)
    b = Int(3)
    divider = Divide()

    connect(a.output, divider.numerator)
    connect(b.output, divider.denominator)

    system = BasicSystem()
    system.add_nodes(a, b, divider)

    system.validate()
    system.run()

    assert divider.output.get_value() == 7 / 3


def test_modulo_floats() -> None:
    a = Float(53.634)
    b = Float(11.4)
    moduloer = Modulo()

    connect(a.output, moduloer.dividend)
    connect(b.output, moduloer.divisor)

    system = BasicSystem()
    system.add_nodes(a, b, moduloer)

    system.validate()
    system.run()

    assert moduloer.output.get_value() == 53.634 % 11.4


def test_modulo_ints() -> None:
    a = Int(53)
    b = Int(11)
    moduloer = Modulo()

    connect(a.output, moduloer.dividend)
    connect(b.output, moduloer.divisor)

    system = BasicSystem()
    system.add_nodes(a, b, moduloer)

    system.validate()
    system.run()

    assert moduloer.output.get_value() == 53 % 11
