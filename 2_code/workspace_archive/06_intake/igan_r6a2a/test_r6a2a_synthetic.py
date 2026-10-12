import numpy as np, math
from scipy.special import logsumexp
def labf(beta,se,sd):
    V=se**2; z=beta/se; r=sd**2/(sd**2+V); return .5*(np.log1p(-r)+r*z*z)
x=np.array([0.,0.,0.2,0.]); se=np.array([.1,.1,.03,.1])
a=labf(x,se,.2)
assert np.argmax(a)==2
print("synthetic_abf_basic=PASS")
