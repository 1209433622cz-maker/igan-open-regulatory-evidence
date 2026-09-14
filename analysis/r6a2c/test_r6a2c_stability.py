import numpy as np
from pathlib import Path
# Stability gate unit test: identical CS across configs must pass Jaccard>=0.5.
def j(a,b):
 a=set(a);b=set(b);return len(a&b)/len(a|b)
assert j(['a','b','c'],['a','b','d'])==0.5
assert j(['a','b'],['c','d'])==0.0
print('R6A2C_stability_gate_synthetic=PASS')
