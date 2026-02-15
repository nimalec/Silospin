"""Strang-split integrator for piecewise-constant Lindblad dynamics.

Exploits the fact that H(t) is constant within each time step:
  - Hamiltonian step: exact via batched 10x10 matrix exponential
  - Dissipator step: Euler half-steps
  - Combined: 2nd order Strang splitting

This reduces H evaluations from 4/step (RK4) to 1/step, and replaces
approximate ODE integration with exact unitary evolution for the
Hamiltonian part.
"""
import logging

import torch
import cupy as cp
import numpy as np

from .batched_expm import BatchedExpmWorkspace

logger = logging.getLogger(__name__)


class StrangSplitIntegrator:
    """
    Strang-split propagator for batched Lindblad dynamics.

    Per time step:
        rho_1 = rho + (dt/2) * L_D[rho]           # half-step dissipation
        U = expm(-2*pi*i * H(t_i) * dt)            # batched 10x10 expm
        rho_2 = U * rho_1 * U^dag                  # exact Hamiltonian step
        rho_3 = rho_2 + (dt/2) * L_D[rho_2]        # half-step dissipation
    """

    def __init__(self, H_callback, collapse_ops_raw, batch_size, dim, state):
        """
        Parameters
        ----------
        H_callback : callable(ti, B, arr_out)
            Fills arr_out[d, d, B] with Hamiltonian at time index ti.
            This is the fused kernel or CuPy callback.
        collapse_ops_raw : list of (L_k, rate_k)
            L_k: cp.ndarray [d, d, B], rate_k: cp.ndarray [B]
        batch_size : int
        dim : int
        state : DenseMixedState
            Template state for .clone()
        """
        self.H_callback = H_callback
        self.collapse_ops = collapse_ops_raw
        self.B = batch_size
        self.d = dim
        self.state_template = state

        # Pre-allocate workspace
        self._H_buf = cp.zeros((dim, dim, batch_size), dtype=cp.complex128, order='F')
        self._A_buf = cp.zeros((dim, dim, batch_size), dtype=cp.complex128, order='F')
        self._U = cp.zeros_like(self._H_buf)
        self._Udag = cp.zeros_like(self._H_buf)
        self._drho = cp.zeros_like(self._H_buf)
        self._tmp = cp.zeros_like(self._H_buf)

        # Pre-allocated expm workspace (avoids memory fragmentation over 10K steps)
        self._expm_ws = BatchedExpmWorkspace(dim, batch_size, xp=cp)

        # Pre-compute L†L and L† for each collapse operator (static)
        self._LdagL = []
        self._Ldag = []
        for L_k, rate_k in self.collapse_ops:
            Ldag = L_k.conj().transpose(1, 0, 2)  # [d, d, B]
            LdL = cp.einsum('ijb,jkb->ikb', Ldag, L_k)  # [d, d, B]
            self._LdagL.append(LdL)
            self._Ldag.append(Ldag)

        # Pre-allocate dissipator temporaries
        self._L_rho = cp.zeros_like(self._H_buf)
        self._LrhoLdag = cp.zeros_like(self._H_buf)
        self._LdL_rho = cp.zeros_like(self._H_buf)
        self._rho_LdL = cp.zeros_like(self._H_buf)

    def _compute_dissipator_action(self, rho, drho_out):
        """
        Compute L_D[rho] = sum_k gamma_k * (L_k rho L_k^dag - 0.5 * {L_k^dag L_k, rho}).

        Parameters
        ----------
        rho : cp.ndarray [d, d, B]
        drho_out : cp.ndarray [d, d, B], output (overwritten)
        """
        drho_out[:] = 0.0

        for idx, (L_k, rate_k) in enumerate(self.collapse_ops):
            Ldag = self._Ldag[idx]
            LdL = self._LdagL[idx]

            # L_k rho -> pre-allocated buffer
            cp.einsum('ijb,jkb->ikb', L_k, rho, out=self._L_rho)
            # L_k rho L_k^dag
            cp.einsum('ijb,jkb->ikb', self._L_rho, Ldag, out=self._LrhoLdag)
            # L†L rho
            cp.einsum('ijb,jkb->ikb', LdL, rho, out=self._LdL_rho)
            # rho L†L
            cp.einsum('ijb,jkb->ikb', rho, LdL, out=self._rho_LdL)

            # D[L_k] rho = rate * (L rho L† - 0.5 * (L†L rho + rho L†L))
            drho_out += rate_k[None, None, :] * (
                self._LrhoLdag - 0.5 * self._LdL_rho - 0.5 * self._rho_LdL
            )

    def _compute_step_propagator(self, ti, dt):
        """Compute U = expm(-2*pi*i * H(ti) * dt) for all batch elements."""
        # Fill H buffer via callback
        self.H_callback(ti, self.B, self._H_buf)

        # A = -2*pi*i * H * dt  (in-place into pre-allocated buffer)
        cp.multiply(self._H_buf, -2.0j * np.pi * dt, out=self._A_buf)

        # Batched matrix exponential (zero-allocation workspace)
        self._expm_ws.compute(self._A_buf)
        self._U[:] = self._expm_ws.result
        self._Udag[:] = self._U.conj().transpose(1, 0, 2)

    def _hamiltonian_step(self, rho):
        """rho -> U rho U† (exact unitary evolution)."""
        self._tmp[:] = cp.einsum('ijb,jkb->ikb', self._U, rho)
        rho[:] = cp.einsum('ijb,jkb->ikb', self._tmp, self._Udag)

    def _rho_to_flat(self, rho):
        """Convert [d, d, B] Fortran -> [B, d²] contiguous."""
        return cp.ascontiguousarray(
            rho.transpose(2, 0, 1).reshape(self.B, self.d * self.d)
        )

    def integrate(self, T, Nt, rho0_cupy, chunk_size=500):
        """
        Full Strang-split integration of Lindblad equation.

        Parameters
        ----------
        T : float
            Total time
        Nt : int
            Number of time steps
        rho0_cupy : cp.ndarray [d, d, B] Fortran order
            Initial density matrix
        chunk_size : int
            Store to CPU every chunk_size steps to limit GPU memory.

        Returns
        -------
        torch.Tensor [Nt, B, d^2] on CPU
        """
        B, d = self.B, self.d
        dt = T / (Nt - 1)

        rho = cp.array(rho0_cupy, dtype=cp.complex128, order='F')

        # Pre-allocate full solution on CPU
        sol_cpu = torch.empty(Nt, B, d * d, dtype=torch.complex128, device='cpu')
        sol_cpu[0] = torch.as_tensor(self._rho_to_flat(rho).get())

        logger.info("Integrating Lindblad (Strang): %d steps, dt=%.2e, batch=%d, dim=%d",
                     Nt, dt, B, d)

        for i in range(Nt - 1):
            # Half-step dissipation
            self._compute_dissipator_action(rho, self._drho)
            rho += (dt / 2.0) * self._drho

            # Full-step Hamiltonian (exact)
            self._compute_step_propagator(i, dt)
            self._hamiltonian_step(rho)

            # Half-step dissipation
            self._compute_dissipator_action(rho, self._drho)
            rho += (dt / 2.0) * self._drho

            # Store snapshot
            sol_cpu[i + 1] = torch.as_tensor(self._rho_to_flat(rho).get())

            if (i + 1) % 1000 == 0:
                logger.info("  ... %d / %d steps done", i + 1, Nt - 1)

        # NaN check on final state
        if cp.isnan(rho).any() or cp.isinf(rho).any():
            raise RuntimeError("Strang solver failed: NaN/Inf detected")

        return sol_cpu

    def integrate_tme(self, T, Nt, rho0_cupy, J_callback, chunk_size=500):
        """
        Strang-split integration of tangent master equation.

        Coupled system:
            d rho/dt = L[rho]
            d(drho)/dt = L[drho] + J[rho]

        Parameters
        ----------
        T : float
        Nt : int
        rho0_cupy : cp.ndarray [d, d, B]
        J_callback : cuQuantum Operator
            J_action with .compute_action(t, dummy, in_state, out_state)
        chunk_size : int

        Returns
        -------
        torch.Tensor [Nt, B, 2*d^2] on CPU
        """
        B, d = self.B, self.d
        dt = T / (Nt - 1)
        dummy = cp.zeros((1, B), dtype=cp.float64, order='F')

        rho = cp.array(rho0_cupy, dtype=cp.complex128, order='F')
        drho = cp.zeros_like(rho)  # delta_rho_0 = 0

        drho_L = cp.zeros_like(rho)  # L[drho] workspace
        j_rho = cp.zeros_like(rho)   # J[rho] workspace

        # DenseMixedState wrappers for cuQuantum J action
        # clone() shares the underlying buffer, so compute_action reads current rho
        rho_s = self.state_template.clone(rho)
        j_out_s = self.state_template.clone(j_rho)

        # Pre-allocate solution on CPU
        sol_cpu = torch.empty(Nt, B, 2 * d * d, dtype=torch.complex128, device='cpu')

        # Store initial state
        rho_flat = self._rho_to_flat(rho).get()
        drho_flat = self._rho_to_flat(drho).get()
        sol_cpu[0] = torch.as_tensor(np.concatenate([rho_flat, drho_flat], axis=1))

        logger.info("Integrating TME (Strang): %d steps, dt=%.2e, batch=%d, dim=%d",
                     Nt, dt, B, d)

        for i in range(Nt - 1):
            t = i * dt

            # --- Half-step dissipation for rho ---
            self._compute_dissipator_action(rho, self._drho)
            rho += (dt / 2.0) * self._drho

            # --- Half-step dissipation for drho + J[rho] source ---
            self._compute_dissipator_action(drho, drho_L)
            # J[rho]: use cuQuantum action for the dH/db commutator
            J_callback.compute_action(t, dummy, rho_s, j_out_s)
            drho += (dt / 2.0) * (drho_L + j_rho)

            # --- Full-step Hamiltonian (exact) for both rho and drho ---
            self._compute_step_propagator(i, dt)
            self._hamiltonian_step(rho)
            # drho propagates with same U: drho -> U drho U†
            self._tmp[:] = cp.einsum('ijb,jkb->ikb', self._U, drho)
            drho[:] = cp.einsum('ijb,jkb->ikb', self._tmp, self._Udag)

            # --- Half-step dissipation for rho ---
            self._compute_dissipator_action(rho, self._drho)
            rho += (dt / 2.0) * self._drho

            # --- Half-step dissipation for drho + J[rho] source ---
            self._compute_dissipator_action(drho, drho_L)
            J_callback.compute_action(t + dt, dummy, rho_s, j_out_s)
            drho += (dt / 2.0) * (drho_L + j_rho)

            # Store snapshot
            rho_flat = self._rho_to_flat(rho).get()
            drho_flat = self._rho_to_flat(drho).get()
            sol_cpu[i + 1] = torch.as_tensor(np.concatenate([rho_flat, drho_flat], axis=1))

            if (i + 1) % 1000 == 0:
                logger.info("  ... %d / %d steps done", i + 1, Nt - 1)

        if cp.isnan(rho).any() or cp.isinf(rho).any():
            raise RuntimeError("Strang TME solver failed: NaN/Inf detected")

        return sol_cpu
