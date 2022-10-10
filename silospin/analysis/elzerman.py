import numpy as np
from math import ceil
def digitize_current(i_trace, t_start, t_end, threshold, sample_rate):
    n_start = ceil(t_start*sample_rate)
    n_end = ceil(t_end*sample_rate)
    i_trace_sub_set =  i_trace[n_start:n_end]
    count = np.count_nonzero(i_trace_sub_set  > threshold)
    if count == 0:
        dig_val = 0
    else:
        dig_val = 1 
    return dig_val
