import numpy as np
import pytest

from src.Grid import Grid
from src.Solvers_TMM import Parabolic_TMM  # adjust if needed
from src.Composition import Composition
import src.ConstAndScales

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

def test_matrix_derivative_single_j(simple_well):
    solver = simple_well
    E = np.mean(solver.V)
    j = 2  # test one interface

    def f(E):
        return solver.get_matrix_j(j, E)[0, 0]

    analytic = solver.get_matrix_derivative_j(j, E)[0, 0]
    numeric = (f(E + 1e-6) - f(E - 1e-6)) / (2e-6)

    print("analytic:", analytic)
    print("numeric :", numeric)

    assert np.isclose(analytic, numeric, rtol=1e-2, atol=1e-4)

# ---------- m11 behaviour ----------

def test_m11_positive(simple_well):
    solver = simple_well
    E = np.mean(solver.V)

    m11 = solver.get_m11(E)
    assert m11 >= 0

def test_m11_has_variation(simple_well):
    solver = simple_well

    E_vals = np.linspace(min(solver.V), max(solver.V), 50)
    m11_vals = [solver.get_m11(E) for E in E_vals]

    assert np.std(m11_vals) > 0

def test_m11_has_local_minima(simple_well):
    solver = simple_well

    E_vals = np.linspace(min(solver.V), max(solver.V), 100)
    m11_vals = np.array([solver.get_m11(E) for E in E_vals])

    mins = (m11_vals[1:-1] < m11_vals[:-2]) & (m11_vals[1:-1] < m11_vals[2:])

    assert np.any(mins)

# ---------- Derivative validation ----------

def numerical_derivative(f, E, h=1e-6):
    return (f(E + h) - f(E - h)) / (2 * h)


def test_m11_derivative_matches_fd(simple_well):
    solver = simple_well
    E = np.mean(solver.V)

    analytic = solver.get_m11_derivative(E)
    numeric = numerical_derivative(solver.get_m11, E)

    assert np.isclose(analytic, numeric, rtol=1e-2, atol=1e-4)

# ---------- Wavefunction ----------

def test_wavefunction_normalized(simple_well):
    solver = simple_well
    energies, psis = solver.get_wavefunctions()

    if len(psis) == 0:
        pytest.skip("No bound states found")

    psi = psis[0]
    dz = solver.G.get_dz()
    angstrom = src.ConstAndScales.ANGSTROM

    norm = np.trapezoid(np.abs(psi)**2, dx=dz/angstrom)
    assert np.isclose(norm, 1, atol=1e-2)

def test_wavefunction_real(simple_well):
    solver = simple_well
    energies, psis = solver.get_wavefunctions()

    if len(psis) == 0:
        pytest.skip("No bound states found")

    psi = psis[0]
    assert np.all(np.isreal(psi))

def test_wavefunction_decay(simple_well):
    solver = simple_well
    energies, psis = solver.get_wavefunctions()

    if len(psis) == 0:
        pytest.skip()

    psi = psis[0]

    # edges should be small (bound state)
    assert abs(psi[0]) < abs(psi[len(psi)//2])
    assert abs(psi[-1]) < abs(psi[len(psi)//2])

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

def test_energy_sensitivity(simple_well):
    solver = simple_well

    E = np.mean(solver.V)

    m1 = solver.get_m11(E)
    m2 = solver.get_m11(E + 1e-3)

    assert not np.isclose(m1, m2)

def test_wavefunctions_exist(simple_well):
    solver = simple_well
    energies, psis = solver.get_wavefunctions()

    assert len(energies) > 0
    assert len(psis) > 0

# ---------- Stability ----------

def test_no_nan_wavefunction(simple_well):
    solver = simple_well
    energies, psis = solver.get_wavefunctions()

    for psi in psis:
        assert not np.any(np.isnan(psi))