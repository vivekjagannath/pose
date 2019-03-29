import dxl
import math
from advay import *

a = dxl.get_available_ports()
print(a)
d = dxl.dxl(a[0], 1000000)
print(d.scan())

