
from dataclasses import dataclass

@dataclass(frozen=True)
class Ty: name: str
I64 = Ty("i64"); F64 = Ty("f64"); STR = Ty("str"); BOOL = Ty("bool")

def typeof_lit_int(text: str): return I64
def typeof_lit_float(text: str): return F64
