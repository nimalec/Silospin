import numpy as np
def gauss(x, amp, mu, sig):
    return amp*np.exp(-(x-mu)**2/(2*sig**2))

def rectangular(npoints, amp):
    return amp*np.ones(npoints)




##def chirped():
##def adiabatic():
