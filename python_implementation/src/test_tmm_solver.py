import numpy as np
import pytest

from src.Grid import Grid
from src.Solvers_TMM import Parabolic_TMM  # adjust if needed
from src.Composition import Composition

# ---------- Fixtures ----------

@pytest.fixture
def simple_well():
    arr = [
        [225, 0.2],
        [80, 0.0],
        [225, 0.2]
    ]
    C = Composition.from_array(arr)
    grid = Grid(C, 0.6, "AlGaAs")
    solver = Parabolic_TMM(grid, nEmax=5)
    return solver

# ---------- Basic sanity ----------

def test_no_nan_wavevector(simple_well):
    solver = simple_well
    E = np.mean(solver.V)

    for j in range(1, solver.G.get_nz()):
        k = solver.get_wavevector(j, E)
        assert np.isfinite(k)


def test_wavevector_regimes(simple_well):
    solver = simple_well

    j = 1
    V = solver.V[j]

    k_below = solver.get_wavevector(j, V - 10)
    k_above = solver.get_wavevector(j, V + 10)

    assert np.isreal(k_below)
    assert not np.isreal(k_above)


# ---------- Transfer matrix ----------

def test_matrix_shape(simple_well):
    solver = simple_well
    M = solver.get_matrix_j(1, np.mean(solver.V))

    assert M.shape == (2, 2)


def test_matrix_no_nan(simple_well):
    solver = simple_well
    M = solver.get_matrix_j(1, np.mean(solver.V))

    assert not np.any(np.isnan(M))


def test_matrix_determinant(simple_well):
    solver = simple_well
    E = np.mean(solver.V)

    for j in range(2, solver.G.get_nz()):
        M = solver.get_matrix_j(j, E)
        det = np.linalg.det(M)
        assert np.isfinite(det)
        assert not np.isclose(det, 0)


# ---------- m11 behaviour ----------

def test_m11_positive(simple_well):
    solver = simple_well
    E = np.mean(solver.V)

    m11 = solver.get_m11(E)
    assert m11 >= 0


# ---------- Derivative validation ----------

def numerical_derivative(f, E, h=1e-6):
    return (f(E + h) - f(E - h)) / (2 * h)


def test_m11_derivative_matches_fd(simple_well):
    solver = simple_well
    E = np.mean(solver.V)

    analytic = solver.get_m11_derivative(E)
    numeric = numerical_derivative(solver.get_m11, E)

    assert np.isclose(analytic, numeric, rtol=1e-3, atol=1e-6)


# ---------- Wavefunction ----------

def test_wavefunction_normalized(simple_well):
    solver = simple_well
    energies, psis = solver.get_wavefunctions()

    if len(psis) == 0:
        pytest.skip("No bound states found")

    psi = psis[0]
    norm = np.trapezoid(np.abs(psi)**2)

    assert np.isclose(norm, 1, atol=1e-2)


def test_wavefunction_real(simple_well):
    solver = simple_well
    energies, psis = solver.get_wavefunctions()

    if len(psis) == 0:
        pytest.skip("No bound states found")

    psi = psis[0]
    assert np.all(np.isreal(psi))


# ---------- Energy spectrum ----------

def test_energies_sorted(simple_well):
    solver = simple_well
    energies, _ = solver.get_wavefunctions()

    assert all(np.diff(energies) > 0)


def test_energies_below_barrier(simple_well):
    solver = simple_well
    energies, _ = solver.get_wavefunctions()

    barrier = max(solver.V)

    for E in energies:
        assert E < barrier


# ---------- Stability ----------

def test_no_nan_wavefunction(simple_well):
    solver = simple_well
    energies, psis = solver.get_wavefunctions()

    for psi in psis:
        assert not np.any(np.isnan(psi))