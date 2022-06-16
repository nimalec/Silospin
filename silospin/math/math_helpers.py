import numpy as np
def gauss(x, amp, mu, sig):
    return amp*np.exp(-(x-mu)**2/(2*sig**2))

def rectangular(npoints, amp, min_points = 48):
    array = amp*np.ones(npoints)
    if npoints < min_points:
        npoints_pad = min_points - npoints
        if npoints_pad%2 == 0:
            zero_pad_l = np.zeros(int(npoints_pad/2))
            zero_pad_r = np.zeros(int(npoints_pad/2))
        elif 2*int(npoints_pad/2) + npoints < min_points:
            zero_pad_l = np.zeros(int(npoints_pad/2))
            zero_pad_r = np.zeros(int(npoints_pad/2) + 1)
        else:
            zero_pad_l = np.zeros(int(npoints_pad/2))
            zero_pad_r = np.zeros(int(npoints_pad/2)-1)
        array = np.concatenate((zero_pad_l, array,zero_pad_r), axis=None)
    else:
        array = amp*np.ones(npoints)

    return array

##def chirped():
##def adiabatic():
