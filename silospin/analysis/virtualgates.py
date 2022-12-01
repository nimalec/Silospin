import numpy as np
def slope_offset(r1, r2, t1,t2):
    r = np.array([r1, r2, (t1[1]-t2[1])/(t1[0]-t2[0])])
    b = np.array([t1[1]-t1[0]*r1, t1[1]-t1[0]*r2,t1[1]-r[2]*t1[0], t2[1]-r2*t2[0], t2[1]-r1*t2[0]])
    return (r,b)

def extractcapp1(r,i,CvgExp):
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
    if CvgGuess:
        CvgGuess = CvgGuess
    else:
        CvgGuess = np.identity(N)
    ##Initialize all matrices
    CvgExp = np.identity(N) # Capacitance matrix
    u_off = np.zeros((N,1)) #Dot i offset in eV/CG^11
    v = np.zeros((N,N)) #nxn array used to define capacitnace matrix
    Voff = np.zeros((N+2,1)) #Offset voltage for each dot in Volts

    #Loops over ==> computes offsets for each dot
    for n in range(N-1):
        (r,b) = slopeoffset(r1[n],r2[n], t1[n],t2[n]) #compute slope at each step
        CvgExp = extractcapp1(r,n, CvgExp)  #extracts cap matrix

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
    return [DotPotModes, CvgExp, v, Voff, u_off]
