import numpy as np
from math import ceil
def digitize_current(i_trace, t_start, t_end, threshold, sample_rate):
    n_start = ceil(t_start*sample_rate)
    n_end = ceil(t_end*sample_rate)
    i_trace_sub_set =  i_trace[n_start:n_end]
    i_max = np.max(i_trace_sub_set)
    if  i_max >= threshold:
        dig_val = 1
    else:
        dig_val = 0
    return dig_val 
