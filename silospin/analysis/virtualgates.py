import numpy as np
def slope_offset(r1, r2, t1, t2):
    '''
    Provied slopes and triple points of charge transition lines in a pairwise charge-stability diagram, retunrs the set of
    voltage offsets and slopes for each. \n

    See Fig. 1 of the supplement of Mills, A. R., et al. Nature communications 10.1 (2019) for details of this parameterization.

    Parameters:
                    r1 (float): slope of the (0,0) -> (1,0) charge transition line (a.u.)
                    r2 (float): slope of the (0,0) -> (0,1) charge transition line (a.u.)
                    t1 (tuple): triple point at the (0,0)-(1,0)-(0,1) transition regions. first element corresponds to the V_{P,i+1} dot voltage and  V_{P,i} dot voltage
                    t2 (tuple): triple point at the (1,0)-(0,1)-(1,1) transition regions. first element corresponds to the V_{P,i+1} dot voltage and  V_{P,i} dot voltage

    Returns:
       r (array): Array of 3 charge transition line slopes, corresponding to (0,0) -> (1,0), (0,0) -> (0,1), and (0,1) -> (1,0) charge transitions.
       b (array): Array of 3 charge transition line interscepts, corresponding to (0,0) -> (1,0), (0,0) -> (0,1), and (0,1) -> (1,0) charge transitions.
    '''
    r = np.array([r1, r2, (t1[1]-t2[1])/(t1[0]-t2[0])])
    b = np.array([t1[1]-t1[0]*r1, t1[1]-t1[0]*r2,t1[1]-r[2]*t1[0], t2[1]-r2*t2[0], t2[1]-r1*t2[0]])
    return (r,b)

def extract_capacitance(r,i,CvgExp):
    '''
    Helper function to calculate capacitance matrix, used by make_cap_matrix.

    Parameters:
                    r (array): array of slopes of charge transition lines. Computed by slope_offset.
                    i (int): index of current quantum dot
                    CvgExp (array) : array of NxN capacitance matrix at the current iteration.

    Returns:
        CvgExp (array) : array of updated capacitance matrix.
    '''
    Cvg = np.array(CvgExp)
    if Cvg[i][i] !=0:
        Cvgii = Cvg[i][i]
    else:
        Cvg[i][i] = 1
        Cvgii = 1
    Cvg[i][i+1] = -r[0]*Cvgii
    Cvg[i+1][i+1] = Cvgii*(r[2]-r[0])/((1-r[2]/r[1]))
    Cvg[i+1][i] = Cvgii*(r[0]-r[2])/(r[1]-r[2])
    CvgExp = Cvg
    return CvgExp

def make_cap_matrix(N,r1,r2,t1,t2,DelVG21,VG,CvgGuess=None):
    '''
    Generates a set of capacitance matrices and virtual gate parameters.

    Parameters:
                    N (int): total number of dots
                    r1 (list): N-dim list of slopes of the (0,0) -> (1,0) charge transition line (a.u.) for each dot
                    r2 (list):  N-dim list of slope of the (0,0) -> (0,1) charge transition line (a.u.)for each dot
                    t1 (list):  N-dim list of tuples of triple points at the (0,0)-(1,0)-(0,1) transition regions. first element corresponds to the V_{P,i+1} dot voltage and  V_{P,i} dot voltage
                    t2 (list):  N-dim list of tuples of triple points at the (1,0)-(0,1)-(1,1) transition regions. first element corresponds to the V_{P,i+1} dot voltage and  V_{P,i} dot voltage
                    DelVG21 (array): Nx1 array of single dot charging energy for (1,0) -> (2,0) transition, for each dot.
                    VG (array): array of gate voltages applied to the left of each dot.
                    CvgGuess (array): initial capacitance matrix estimate. Default set to the identity.

    Returns:
        virtual_gate_params (dict): dictionary of virtual gate parameters. These inlcude "CG" (the normalized gate capacitance matrix used to transform from virtual to physical gates),  "slope_offset" (list of tuples of charge transition slopes and offsets), "DotPotModes" (inverse of the CVgExp matrix),
        "CvgExp" (Cvg matrix),  "v" (the nearest neighboor dot interaction), "Voff" (offset voltage vector for physical gates), "Uoff" (offset voltage vector for virtual gates).
    '''

    if CvgGuess is not None:
        CvgGuess = CvgGuess
    else:
        CvgGuess = np.identity(N)
    CvgExp = np.identity(N)
    u_off = np.zeros((N,1))
    v = np.zeros((N,N))
    Voff = np.zeros((N+2,1))
    slope_offset = []

    for n in range(N-1):
        (r,b) = slopeoffset(r1[n],r2[n], t1[n],t2[n])
        slope_offset.append((r,b))
        CvgExp = extract_capacitance(r,n, CvgExp)
        v[n,n+1] = (b[4]-b[0])*CvgExp[n,n]/2
        v[n+1,n] = v[n,n+1]
        v[n,n] = CvgExp[n,n]*DelVG21[n]/2
        if n == 0:
            u_off[n] = (CvgExp[n][n]*b[0]-v[n][n])
        else:
            u_off[n] = (CvgExp[n][n]*b[0]-v[n][n]+CvgExp[n][n-1]*VG[n-1])
    v[N-1,N-1] = CvgExp[N-1,N-1]*DelVG21[N-1]/2
    u_off[N-1] = CvgExp[N-1][N-2]*b[1]-v[N-1][N-1]
    CvgExp = np.matmul(CvgExp,np.array(CvgGuess))
    DotPotModes = np.linalg.inv(CvgExp)
    Voff[1:N+1] = np.matmul(np.linalg.pinv(CvgExp), u_off)
    Cg = -np.matmul(np.linalg.inv(v), Cv)/np.linalg.norm(np.matmul(np.linalg.inv(v), Cv))
    virtual_gate_params = {"CG": Cg.tolist(), "slope_offset": slope_offset,  "DotPotModes": DotPotModes.tolist(), "CvgExp": CvgExp.tolist(), "v": v.tolist(), "Voff":  Voff[1:N+1].flatten().tolist(), "Uoff": u_off.tolist()}
    return virtual_gate_params

def virtual_to_physical(virtual_gate, virtual_gate_params):
    '''
    Provided a vector of virtual gates and virtual_gate_params produced from make_cap_matrix, compute the physical gates to be addressed on a DAC.
    '''
    virtual_gate = np.array(virtual_gate)
    CG = np.array(virtual_gate_params["CG"])
    VOff = np.array(virtual_gate_params["Voff"]).flatten()
    N = len(VOff)
    physical_gate = np.matmul(CG, virtual_gate) + VOff
    return physical_gate
