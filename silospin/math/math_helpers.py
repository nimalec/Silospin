import numpy as np
from math import ceil
def gauss(x, amp, mu, sig):
    return amp*np.exp(-(x-mu)**2/(2*sig**2))

def rectangular(npoints, amp, min_points = 48):
    #min_npoints = ceil(min_points/16)*16
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

def rectangular_add_padding(npoints, amp, min_points = 48):
    #min_npoints = ceil(min_points/16)*16
    #net_pad = min_points - npoints  (if npoints < min_points)
    #net_pad  = 0 (if n_points = min_points)
    #add assert for npoints > min_points ==> cannot have st npoitns > min_poitns
    #additional_pad = (2*side_pad*sample_rate/16)*16
    #if net_pad = 0 , min_points ->  min_points + additional_pad
    #else (net_pad !=0), pad_prime = ceil(net_pad/16)*16 - additional_pad
    #min_points -> min_points + pad_prime

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


def compute_accumulated_phase(gt, phi_l):
    phi_d_gt = {"x":  0, "y": 90, "xx":  0, "yy": 90 , "xxx":  180, "yyy": -90, "mxxm": 180, "myym": -90}
    phi_d = phi_d_gt[gt]
    phi_a = phi_d - phi_l
    phi_l = phi_l + phi_a
    return phi_l, phi_a
