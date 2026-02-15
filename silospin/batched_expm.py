"""Batched matrix exponential for small dense matrices.

Implements Padé[13,13] scaling-and-squaring (Higham 2005) for batched
complex matrices. Designed for d=10 NV Hamiltonian propagators where
B (batch) can be large but d is small.

Both CuPy (GPU) and NumPy (CPU) backends are provided.
"""
import numpy as np

try:
    import cupy as cp
    HAS_CUPY = True
except ImportError:
    HAS_CUPY = False

# Padé[13,13] coefficients from Higham (2005), Table 10.4
_PADE13_COEFFS = [
    1.0,
    0.5,
    0.12,
    1.833333333333333333e-2,
    1.992753623188405797e-3,
    1.630434782608695652e-4,
    1.035196687370600414e-5,
    5.175983436853002070e-7,
    2.043151356652500817e-8,
    6.306022705717595115e-10,
    1.483770048404140027e-11,
    2.529153491597965955e-13,
    2.810170546219962173e-15,
    1.544049750670308885e-17,
]

# theta_13 from Al-Mohy and Higham (2010), Table 2.3
_THETA_13 = 5.371920351148152


def _batched_matmul(A, B, xp):
    """Batched matrix multiply: A[d,d,B] @ B[d,d,B] -> [d,d,B]."""
    return xp.einsum('ijb,jkb->ikb', A, B)


def _batched_matmul_out(A, B, out, xp):
    """Batched matrix multiply with pre-allocated output."""
    xp.einsum('ijb,jkb->ikb', A, B, out=out)
    return out


def _batched_eye(d, B, dtype, xp):
    """Create batched identity: I[d,d,B]."""
    I = xp.zeros((d, d, B), dtype=dtype)
    for i in range(d):
        I[i, i, :] = 1.0
    return I


class BatchedExpmWorkspace:
    """Pre-allocated workspace for batched_expm to avoid memory fragmentation.

    Create once, reuse across all time steps.
    """

    def __init__(self, d, B, xp=None):
        if xp is None:
            xp = cp if HAS_CUPY else np
        self.xp = xp
        self.d = d
        self.B = B
        dtype = np.complex128

        # Padé workspace [d, d, B]
        self.A_scaled = xp.zeros((d, d, B), dtype=dtype)
        self.A2 = xp.zeros((d, d, B), dtype=dtype)
        self.A4 = xp.zeros((d, d, B), dtype=dtype)
        self.A6 = xp.zeros((d, d, B), dtype=dtype)
        self.W1 = xp.zeros((d, d, B), dtype=dtype)
        self.W2 = xp.zeros((d, d, B), dtype=dtype)
        self.W = xp.zeros((d, d, B), dtype=dtype)
        self.U = xp.zeros((d, d, B), dtype=dtype)
        self.V = xp.zeros((d, d, B), dtype=dtype)
        self.p13 = xp.zeros((d, d, B), dtype=dtype)
        self.q13 = xp.zeros((d, d, B), dtype=dtype)
        self.I = _batched_eye(d, B, dtype, xp)
        self.result = xp.zeros((d, d, B), dtype=dtype)
        self.tmp = xp.zeros((d, d, B), dtype=dtype)

        # Transposed workspace for solve [B, d, d]
        self.q13_t = xp.zeros((B, d, d), dtype=dtype)
        self.p13_t = xp.zeros((B, d, d), dtype=dtype)

    def compute(self, A):
        """Compute expm(A) using pre-allocated buffers. Returns self.result."""
        xp = self.xp
        b = _PADE13_COEFFS

        # Scaling
        norms = xp.abs(A).sum(axis=0).max(axis=0)
        max_norm = float(norms.max())

        if max_norm == 0.0:
            self.result[:] = self.I
            return self.result

        s = max(0, int(np.ceil(np.log2(max_norm / _THETA_13))))

        if s > 0:
            self.A_scaled[:] = A * (2.0 ** (-s))
        else:
            self.A_scaled[:] = A

        # Compute powers
        _batched_matmul_out(self.A_scaled, self.A_scaled, self.A2, xp)
        _batched_matmul_out(self.A2, self.A2, self.A4, xp)
        _batched_matmul_out(self.A2, self.A4, self.A6, xp)

        # W1 = b[13]*A6 + b[11]*A4 + b[9]*A2
        self.W1[:] = b[13] * self.A6 + b[11] * self.A4 + b[9] * self.A2
        # W2 = b[7]*A6 + b[5]*A4 + b[3]*A2 + b[1]*I
        self.W2[:] = b[7] * self.A6 + b[5] * self.A4 + b[3] * self.A2 + b[1] * self.I

        # W = A6 @ W1 + W2
        _batched_matmul_out(self.A6, self.W1, self.W, xp)
        self.W += self.W2
        # U = A @ W
        _batched_matmul_out(self.A_scaled, self.W, self.U, xp)

        # V = A6 @ Z1 + Z2 (reuse W1, W2 as Z1, Z2)
        self.W1[:] = b[12] * self.A6 + b[10] * self.A4 + b[8] * self.A2
        self.W2[:] = b[6] * self.A6 + b[4] * self.A4 + b[2] * self.A2 + b[0] * self.I
        _batched_matmul_out(self.A6, self.W1, self.V, xp)
        self.V += self.W2

        # p13 = U + V, q13 = -U + V
        self.p13[:] = self.U + self.V
        self.q13[:] = -self.U + self.V

        # Solve q13 @ X = p13
        self.q13_t[:] = self.q13.transpose(2, 0, 1)
        self.p13_t[:] = self.p13.transpose(2, 0, 1)

        if xp is np:
            result_t = np.linalg.solve(self.q13_t, self.p13_t)
        else:
            result_t = cp.linalg.solve(self.q13_t, self.p13_t)

        self.result[:] = result_t.transpose(1, 2, 0)

        # Repeated squaring
        for _ in range(s):
            self.tmp[:] = self.result
            _batched_matmul_out(self.tmp, self.tmp, self.result, xp)

        return self.result


# --- Original functional API (kept for backward compatibility) ---

def _pade13_batched(A, xp):
    """Compute Padé[13,13] approximation (allocates temporaries)."""
    d = A.shape[0]
    B_batch = A.shape[2]
    dtype = A.dtype
    b = _PADE13_COEFFS

    I = _batched_eye(d, B_batch, dtype, xp)
    A2 = _batched_matmul(A, A, xp)
    A4 = _batched_matmul(A2, A2, xp)
    A6 = _batched_matmul(A2, A4, xp)

    W1 = b[13] * A6 + b[11] * A4 + b[9] * A2
    W2 = b[7] * A6 + b[5] * A4 + b[3] * A2 + b[1] * I
    Z1 = b[12] * A6 + b[10] * A4 + b[8] * A2
    Z2 = b[6] * A6 + b[4] * A4 + b[2] * A2 + b[0] * I

    W = _batched_matmul(A6, W1, xp) + W2
    U = _batched_matmul(A, W, xp)
    V = _batched_matmul(A6, Z1, xp) + Z2

    p13 = U + V
    q13 = -U + V

    q13_t = xp.ascontiguousarray(q13.transpose(2, 0, 1))
    p13_t = xp.ascontiguousarray(p13.transpose(2, 0, 1))

    if xp is np:
        result_t = np.linalg.solve(q13_t, p13_t)
    else:
        result_t = cp.linalg.solve(q13_t, p13_t)

    return result_t.transpose(1, 2, 0)


def batched_expm(A, xp=None):
    """Compute expm(A) for batched matrices (allocates temporaries each call)."""
    if xp is None:
        xp = cp if (HAS_CUPY and hasattr(A, '__cuda_array_interface__')) else np

    d = A.shape[0]
    B_batch = A.shape[2]
    dtype = A.dtype

    norms = xp.abs(A).sum(axis=0).max(axis=0)
    max_norm = float(norms.max())

    if max_norm == 0.0:
        return _batched_eye(d, B_batch, dtype, xp)

    s = max(0, int(np.ceil(np.log2(max_norm / _THETA_13))))

    if s > 0:
        A_scaled = A * (2.0 ** (-s))
    else:
        A_scaled = A

    result = _pade13_batched(A_scaled, xp)

    for _ in range(s):
        result = _batched_matmul(result, result, xp)

    return result


def batched_expm_gpu(A):
    """GPU convenience wrapper."""
    return batched_expm(A, xp=cp)


def batched_expm_cpu(A):
    """CPU convenience wrapper."""
    return batched_expm(A, xp=np)
