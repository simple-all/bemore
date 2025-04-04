from bemore.math import Float, Sum, Printer, String, Int, Product, Indexer
from bemore.core.system import System
from bemore.core.connectors import connect
from bemore.cli.logging import basic_setup


basic_setup()

one = Float(1.0)
two = Float(2.0)
five = Int(5)
string = String("test")

summer = Sum()
producter = Product()

sum_printer = Printer()
sum_printer.name = "Sum"

product_printer = Printer()
product_printer.name = "Product"

indexer: Indexer[float] = Indexer()

connect(one.output, summer.input)
connect(two.output, summer.input)
connect(five.output, summer.input)

connect(one.output, producter.input)
connect(two.output, producter.input)
connect(five.output, producter.input)

connect(summer.output, sum_printer.input)
connect(producter.output, product_printer.input)

sys = System()
sys.add_node(sum_printer)
sys.add_node(product_printer)
sys.add_node(one)
sys.add_node(two)
sys.add_node(string)
sys.add_node(summer)
sys.add_node(five)
sys.add_node(producter)

for node in sys._nodes:
    node.validate()

sys.run()
