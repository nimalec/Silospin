import numpy as np
def gauss(x, amp, mu, sig):
    return amp*np.exp(-(x-mu)**2/(2*sig**2))

def rectangular(npoints, amp):
    array = amp*np.ones(npoints)
    array[0] = 0
    array[1] = 0
    array[npoints-1] = 0
    array[npoints-2] = 0
    return array 


##def chirped():
##def adiabatic():
