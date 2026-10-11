import numpy as np, math
from scipy.special import logsumexp
def labf(beta,se,sd):
    V=se**2; z=beta/se; r=sd**2/(sd**2+V)
    return .5*(np.log1p(-r)+r*z*z)
x=np.array([0.0,0.05,0.3,0.0]); se=np.array([0.1,0.1,0.03,0.1])
a=labf(x,se,0.2)
assert int(np.argmax(a))==2
print("R6A2B0_synthetic_ABF=PASS")
