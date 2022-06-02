import numpy as np
def gauss(x, amp, mu, sig):
    return amp*np.exp(-(x-mu)**2/(2*sig**2))

def rectangular(npoints, amp):
    array = amp*np.ones(npoints)
    zr = np.zeros(48)
    return np.concatenate((zr, array,zr), axis=None)


##def chirped():
##def adiabatic():
