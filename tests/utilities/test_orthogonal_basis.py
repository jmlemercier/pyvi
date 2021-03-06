# -*- coding: utf-8 -*-
"""
Test script for pyvi/utilities/orthogonal_basis.py

Notes
-----
Developed for Python 3.6
@author: Damien Bouvier (Damien.Bouvier@ircam.fr)
"""

#==============================================================================
# Importations
#==============================================================================

import unittest
import numpy as np
from pyvi.utilities.orthogonal_basis import (_OrthogonalBasis, LaguerreBasis,
                                             KautzBasis, GeneralizedBasis,
                                             create_orthogonal_basis,
                                             is_valid_basis_instance,
                                             laguerre_pole_optimization)
from pyvi.volterra.combinatorial_basis import projected_volterra_basis
from pyvi.identification.methods import order_method


#==============================================================================
# Test Class
#==============================================================================

class CreateOrthogonalBasisTest(unittest.TestCase):

    K = 6
    unit_delay = False

    def test_real_pole_outputs_laguerre(self):
        for pole in [0.5, 0.5 + 0j, [0.1], [0.1 + 0j]]:
            with self.subTest(i=pole):
                basis = create_orthogonal_basis(pole, K=self.K,
                                                unit_delay=self.unit_delay)
                self.assertIsInstance(basis, LaguerreBasis)

    def test_cplx_pole_outputs_kautz(self):
        for pole in [0.5 + 0.1j, [0.5 + 0.1j]]:
            with self.subTest(i=pole):
                basis = create_orthogonal_basis(pole, K=self.K,
                                                unit_delay=self.unit_delay)
                self.assertIsInstance(basis, KautzBasis)

    def test_list_poles_outputs_generalized(self):
        for poles in [[0.5, 0.4], [0.5 + 0.1j, 0.4 + 0.5j], [0.5, 0.5 + 0.1j]]:
            with self.subTest(i=poles):
                basis = create_orthogonal_basis(poles,
                                                unit_delay=self.unit_delay)
                self.assertIsInstance(basis, GeneralizedBasis)

    def test_zero_len_error(self):
        self.assertRaises(ValueError, create_orthogonal_basis, [])

    def test_no_K_for_laguerre_error(self):
        self.assertRaises(ValueError, create_orthogonal_basis, 0.5)

    def test_no_K_for_kautz_error(self):
        self.assertRaises(ValueError, create_orthogonal_basis, 0.5 + 0.1j)

    def test_wrong_type_error(self):
        self.assertRaises(TypeError, create_orthogonal_basis, None)


class CreateOrthogonalBasisTestWithUnitDelay(CreateOrthogonalBasisTest):

    unit_delay = True


class _OrthogonalBasisGlobalTest():

    params_list = []
    basis = _OrthogonalBasis
    L = 2000
    atol = 1e-14
    rtol = 1e-14
    unit_delay = False

    def setUp(self):
        self.basis_list = []
        for pole, K in self.params_list:
            self.basis_list.append(self.basis(pole, K,
                                              unit_delay=self.unit_delay))

    def test_orthogonality(self):
        input_sig = np.zeros((self.L,))
        input_sig[0] = 1
        for ind, basis in enumerate(self.basis_list):
            with self.subTest(i=ind):
                filters = basis.projection(input_sig)
                orthogonality_mat = np.dot(filters, filters.T)
                self.assertTrue(np.allclose(orthogonality_mat,
                                            np.identity(basis.K),
                                            rtol=self.rtol, atol=self.atol))

    def test_is_valid_basis_obj(self):
        for ind, basis in enumerate(self.basis_list):
            with self.subTest(i=ind):
                self.assertTrue(is_valid_basis_instance(basis))

    def test_cplx_input(self):
        input_real = np.random.normal(size=(100,))
        input_imag = np.random.normal(size=(100,))
        input_sig = input_real + 1j * input_imag
        for ind, basis in enumerate(self.basis_list):
            with self.subTest(i=ind):
                proj_real = basis.projection(input_real)
                proj_imag = basis.projection(input_imag)
                proj_sig = basis.projection(input_sig)
                self.assertTrue(np.allclose(proj_real + 1j * proj_imag,
                                            proj_sig, rtol=self.rtol,
                                            atol=self.atol))


class LaguerreBasisTest(_OrthogonalBasisGlobalTest, unittest.TestCase):
    params_list = [(0.1, 2), (0.1, 5), (0.1, 10), (0.2, 5), (0.5, 5),
                   (0.9, 5), (0.95, 5), (0, 5)]
    basis = LaguerreBasis


class KautzBasisTest(_OrthogonalBasisGlobalTest, unittest.TestCase):
    params_list = [(0.1*np.exp(1j*np.pi/4), 2), (0.1*np.exp(1j*np.pi/4), 10),
                   (0.5*np.exp(1j*np.pi/4), 10), (0.9*np.exp(1j*np.pi/4), 10),
                   (0.95*np.exp(1j*np.pi/4), 10), (0.7 + 0.1j, 10), (0.7, 10),
                   (0, 6)]
    basis = KautzBasis


class GeneralizedBasisTest(_OrthogonalBasisGlobalTest, unittest.TestCase):
    params_list = [[0.1], [0.1, 0.2, 0.5], [0.1, 0.9, 0.1, 0.5, 0.1],
                   [0.1*np.exp(1j*np.pi/4)], [0.1*np.exp(1j*np.pi/4), 0.1],
                   [0.1 + 0.1j, 0.2 + 0.2j, 0.5 + 0.1j, 0.1 + 0.5j],
                   [0.1 + 0.1j, 0.2, 0.5 + 0.1j, 0.5, 0.1 + 0.5j], [0, 0, 0]]
    basis = GeneralizedBasis

    def setUp(self):
        self.basis_list = []
        for poles in self.params_list:
            self.basis_list.append(self.basis(poles,
                                              unit_delay=self.unit_delay))


class LaguerreBasisTestWithUnitDelay(LaguerreBasisTest):

    unit_delay = True


class KautzBasisTestWithUnitDelay(KautzBasisTest):

    unit_delay = True


class GeneralizedBasisTestWithUnitDelay(GeneralizedBasisTest):

    unit_delay = True


class RaisedErrorTest(unittest.TestCase):

    def test_cplx_laguerre_pole(self):
        self.assertRaises(ValueError, LaguerreBasis, 1+1j, 2)

    def test_odd_K_for_kautz_basis(self):
        self.assertRaises(ValueError, KautzBasis, 1+1j, 3)


class LaguerreAndGeneralizedEqualityTest(unittest.TestCase):

    pole = 0.5
    list_K = [1, 2, 5, 10]
    comp_basis = LaguerreBasis
    L = 1000
    atol = 1e-14
    rtol = 0
    unit_delay = False

    def setUp(self):
        input_sig = np.zeros((self.L,))
        input_sig[0] = 1
        self.comp_filters = dict()
        self.gob_filters = dict()
        for K in self.list_K:
            poles = self._pole2poles(K)
            comp_basis = self.comp_basis(self.pole, K,
                                         unit_delay=self.unit_delay)
            self.comp_filters[K] = comp_basis.projection(input_sig)
            generalized_basis = GeneralizedBasis(poles,
                                                 unit_delay=self.unit_delay)
            self.gob_filters[K] = generalized_basis.projection(input_sig)

    def _pole2poles(self, K):
        return (self.pole,)*K

    def test_equality(self):
        for K in self.list_K:
            with self.subTest(i=K):
                self.assertTrue(np.allclose(self.gob_filters[K],
                                            self.comp_filters[K],
                                            rtol=self.rtol, atol=self.atol))


class KautzAndGeneralizedEqualityTest(LaguerreAndGeneralizedEqualityTest):
    pole = 0.5 + 0.1j
    list_K = [2, 4, 10, 20]
    comp_basis = KautzBasis

    def _pole2poles(self, K):
        return (self.pole,)*(K//2)


class LaguerreAndGeneralizedEqualityTest_2(LaguerreAndGeneralizedEqualityTest):

    unit_delay = True


class KautzAndGeneralizedEqualityTest_2(KautzAndGeneralizedEqualityTest):

    unit_delay = True


class LaguerrePoleOptimizationTest(unittest.TestCase):

    L = 3000
    K = 3
    N = 2
    poles = {1: 0.85, 2: 0.9}
    coeff = {1: [1, 0.0, 0.0],
             2: [1, 0.0, 0.00, 0.0, 0.00, 0.0]}
    iter_max = 8
    tests = ['vec']*2 + ['tri']*2 + ['sym']*2
    unit_delay = False
    atol = 1e-12
    rtol = 0

    def setUp(self):
        self.sig = np.random.normal(size=(self.L,))
        basis = [LaguerreBasis(pole, self.K, unit_delay=self.unit_delay)
                 for pole in self.poles.values()]
        phi = projected_volterra_basis(self.sig, self.N, basis, True,
                                       sorted_by='order')
        self.outputs = np.zeros((self.N, self.L))
        for n, val in phi.items():
            self.outputs[n-1, :] = np.dot(val, self.coeff[n])

        self.results = np.zeros((len(self.tests), self.N))
        for ind, form in enumerate(self.tests):
            self.results[ind, :] = self._make_estim(form)


    def _make_estim(self, form):
        poles = np.random.uniform(size=(self.N,))

        for iter_nb in range(self.iter_max):
            basis = [LaguerreBasis(pole, self.K, unit_delay=self.unit_delay)
                     for pole in poles]
            est_kernels = order_method(self.sig, self.outputs, self.N,
                                       orthogonal_basis=basis, out_form=form)
            for n, proj in est_kernels.items():
                poles[n-1] = laguerre_pole_optimization(poles[n-1], proj,
                                                        n, self.K)
        return poles

    def test_convergence(self):
        for n in range(self.N):
            with self.subTest(i=n):
                self.assertTrue(np.allclose(self._compute_error(n), 0,
                                            atol=self.atol, rtol=self.rtol))

    def _compute_error(self, n):
        return self.results[:, n] - self.poles[n+1]


class LaguerrePoleOptimizationTest_Sym(LaguerrePoleOptimizationTest):

    coeff = {1: [1, 0.2, 0.1],
             2: [1, 0.05, 0.02, 0.2, 0.01, 0.1]}
    tests = ['sym']*2
    iter_max = 10
    atol = 1e-8

    def _compute_error(self, n):
        temp = self.results[:, n]
        return temp[:, np.newaxis] - temp[np.newaxis, :]


class LaguerrePoleOptimizationTest_Tri(LaguerrePoleOptimizationTest_Sym):

    tests = ['tri']*2


class LaguerrePoleOptimizationTest_Vec(LaguerrePoleOptimizationTest_Sym):

    tests = ['vec']*2
    iter_max = 20


#==============================================================================
# Main script
#==============================================================================

if __name__ == '__main__':
    """
    Main script for testing.
    """

    unittest.main()
