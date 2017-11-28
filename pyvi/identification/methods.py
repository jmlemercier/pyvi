# -*- coding: utf-8 -*-
"""
Toolbox for nonlinear system identification.

This package creates functions for Volterra kernel identification via
Least-Squares methods usign QR decomposition.

Functions
---------
KLS :
    Kernel identification via Least-Squares method using a QR decomposition.
orderKLS :
    Performs KLS method on each nonlinear homogeneous order.
termKLS :
    Performs KLS method on each combinatorial term.
phaseKLS :
    Performs KLS method on homogeneous-phase signals.
iterKLS :
    Performs KLS method recursively on homogeneous-phase signals.

Notes
-----
@author: bouvier (bouvier@ircam.fr)
         Damien Bouvier, IRCAM, Paris

Last modified on 25 Oct. 2017
Developed for Python 3.6.1
"""

#==============================================================================
# Importations
#==============================================================================

import warnings
import numpy as np
import scipy.linalg as sc_lin
from .tools import (volterra_basis_by_order, volterra_basis_by_term,
                    nb_coeff_in_kernel, nb_coeff_in_all_kernels,
                    assert_enough_data_samples, vector_to_kernel,
                    vector_to_all_kernels)
from ..utilities.mathbox import binomial


#==============================================================================
# Functions
#==============================================================================

def KLS(input_sig, output_sig, M, N, phi=None, form='sym'):
    """
    Kernel identification via Least-Squares method using a QR decomposition.

    Parameters
    ----------
    input_sig : numpy.ndarray
        Input signal.
    output_sig : numpy.ndarray
        Output signal.
    M : int
        Memory length of kernels (in samples).
    N : int
        Highest kernel order.
    phi : {dict(int: numpy.ndarray), numpy.ndarray}, optional (default=None)
        If None, ``phi`` is computed from ``input_sig``; else, ``phi`` is used.
    form : {'sym', 'tri', 'symmetric', 'triangular'}, optional (default='sym')
        Form of the returned Volterra kernel (symmetric or triangular).

    Returns
    -------
    kernels : dict(int: numpy.ndarray)
        Dictionnary linking the Volterra kernel of order ``n`` to key ``n``.
    """

    # Checking that there is enough data samples
    _KLS_check_feasability(input_sig.shape[0], M, N, form=form)

    # Input combinatoric
    phi = _KLS_construct_phi(input_sig, M, N, phi=phi)

    # Identification
    f = _KLS_core_computation(phi, output_sig)

    # Re-arranging vector f into volterra kernels
    kernels = vector_to_all_kernels(f, M, N, form=form)

    return kernels


def _KLS_check_feasability(nb_data, M, N, form='sym'):
    """Auxiliary function of KLS() for checking feasability."""

    nb_coeff = nb_coeff_in_all_kernels(M, N, form=form)
    assert_enough_data_samples(nb_data, nb_coeff, M, N, name='KLS')


def _KLS_construct_phi(signal, M, N, phi=None):
    """Auxiliary function of KLS() for Volterra basis computation."""

    if phi is None:
        phi_dict = volterra_basis_by_order(signal, M, N)
    elif isinstance(phi, dict):
        phi_dict = phi
    elif isinstance(phi, np.ndarray):
        return phi
    return np.concatenate([val for n, val in sorted(phi_dict.items())], axis=1)


def _KLS_core_computation(combinatorial_matrix, output_sig):
    """Auxiliary function of KLS() for the core computation."""

    # QR decomposition
    q, r = sc_lin.qr(combinatorial_matrix, mode='economic')

    # Projection on combinatorial basis
    y = np.dot(q.T, output_sig)

    # Forward inverse
    return sc_lin.solve_triangular(r, y)


#=============================================#

def orderKLS(input_sig, output_by_order, M, N, phi=None, form='sym'):
    """
    Performs KLS method on each nonlinear homogeneous order.

    Parameters
    ----------
    input_sig : numpy.ndarray
        Input signal.
    output_by_order : numpy.ndarray
        Output signal separated in ``N`` nonlinear homogeneous orders.
    M : int
        Memory length of kernels (in samples).
    N : int
        Highest kernel order.
    phi : {None, dict(int: numpy.ndarray)}, optional (default=None)
        If None, ``phi`` is computed from ``input_sig``; else, ``phi`` is used.
    form : {'sym', 'tri', 'symmetric', 'triangular'}, optional (default='sym')
        Form of the returned Volterra kernel (symmetric or triangular).

    Returns
    -------
    kernels : dict(int: numpy.ndarray)
        Dictionnary linking the Volterra kernel of order ``n`` to key ``n``.
    """

    # Checking that there is enough data samples
    _orderKLS_check_feasability(input_sig.shape[0], M, N, form=form)

    # Input combinatoric
    if phi is None:
        phi = _orderKLS_construct_phi(input_sig, M, N)

    kernels = dict()

    # Identification on each order
    for n, phi_n in phi.items():
        f_n = _orderKLS_core_computation(phi_n, output_by_order[n-1])

        # Re-arranging vector f_n into volterra kernel of order n
        kernels[n] = vector_to_kernel(f_n, M, n, form=form)

    return kernels


def _orderKLS_check_feasability(nb_data, M, N, form='sym', name='orderKLS'):
    """Auxiliary function of orderKLS() for checking feasability."""

    nb_coeff = nb_coeff_in_kernel(M, N, form=form)
    assert_enough_data_samples(nb_data, nb_coeff, M, N, name=name)


def _orderKLS_construct_phi(signal, M, N):
    """Auxiliary function of orderKLS() for Volterra basis computation."""

    return volterra_basis_by_order(signal, M, N)


def _orderKLS_core_computation(combinatorial_matrix, output_sig):
    """Auxiliary function of orderKLS()) for the core computation."""

    return _KLS_core_computation(combinatorial_matrix, output_sig)


#=============================================#

def termKLS(input_sig, output_by_term, M, N, phi=None, form='sym',
            cast_mode='real-imag', mode='mmse'):
    """
    Performs KLS method on each combinatorial term.

    Parameters
    ----------
    input_sig : numpy.ndarray
        Input signal.
    output_by_term : dict((int, int): numpy.ndarray}
        Output signal separated in nonlinear combinatorial terms.
    M : int
        Memory length of kernels (in samples).
    N : int
        Highest kernel order.
    phi : {None, dict(int: numpy.ndarray)}, optional (default=None)
        If None, ``phi`` is computed from ``input_sig``; else, ``phi`` is used.
    form : {'sym', 'tri', 'symmetric', 'triangular'}, optional (default='sym')
        Form of the returned Volterra kernel (symmetric or triangular).
    cast_mode : {'real', 'imag', 'real-imag'}, optional (default='real-imag')
        Choose how complex number are casted to real numbers.
    mode : {'mean', 'mmse'}, optional (default='mmse')
        Choose how are handled the redundant information from same-order terms.

    Returns
    -------
    kernels : dict(int: numpy.ndarray)
        Dictionnary linking the Volterra kernel of order ``n`` to key ``n``.
    """

    # Checking that there is enough data samples
    _termKLS_check_feasability(input_sig.shape[0], M, N, form=form)

    # Input combinatoric
    if phi is None:
        phi = _termKLS_construct_phi(input_sig, M, N)

    kernels = dict()

    # Identification
    if mode == 'mean':
        f = _termKLS_core_mean_mode(phi, output_by_term, M, N, form, cast_mode)
    elif mode == 'mmse':
        f = _termKLS_core_mmse_mode(phi, output_by_term, N, cast_mode)

    # Re-arranging vector f_n into volterra kernel of order n
    for n in range(1, N+1):
        kernels[n] = vector_to_kernel(f[n], M, n, form=form)

    return kernels


def _termKLS_check_feasability(nb_data, M, N, form='sym'):
    """Auxiliary function of termKLS() for checking feasability."""

    _orderKLS_check_feasability(nb_data, M, N, form=form, name='termKLS')


def _termKLS_construct_phi(signal, M, N):
    """Auxiliary function of termKLS() for Volterra basis computation."""

    return volterra_basis_by_term(signal, M, N)


def _termKLS_core_mean_mode(phi, output_by_term, M, N, form, cast_mode):
    """Auxiliary function of termKLS() using 'mean' mode."""

    f = dict()

    # Initialization
    for n in range(1, N+1):
        f[n] = np.zeros((nb_coeff_in_kernel(M, n, form=form),))

    # Identification  on each combinatorial term
    for (n, k), phi_nk in phi.items():
        f[n] += _KLS_core_computation(
            _cplx_to_real(phi_nk, cast_mode=cast_mode),
            _cplx_to_real(output_by_term[(n, k)], cast_mode=cast_mode))

    # Taking mean of all identifications for each order
    for n in range(1, N+1):
        f[n] /= (1+n//2)

    return f


def _termKLS_core_mmse_mode(phi, output_by_term, N, cast_mode):
    """Auxiliary function of termKLS() using 'mmse' mode."""

    f = dict()

    # Identification on each combinatorial term
    for n in range(1, N+1):
        phi_n = np.concatenate([phi[(n, k)] for k in range(1+n//2)], axis=0)
        sig_n = np.concatenate([output_by_term[(n, k)] for k in range(1+n//2)],
                                axis=0)
        f[n] = _KLS_core_computation(_cplx_to_real(phi_n, cast_mode=cast_mode),
                                     _cplx_to_real(sig_n, cast_mode=cast_mode))

    return f


#=============================================#

def phaseKLS(input_sig, output_by_phase, M, N, phi=None, form='sym',
             cast_mode='real-imag'):
    """
    Performs KLS method on homogeneous-phase signals.

    Parameters
    ----------
    input_sig : numpy.ndarray
        Input signal.
    output_by_phase : numpy.ndarray
        Output signal separated in homogeneous-phase signals.
    M : int
        Memory length of kernels (in samples).
    N : int
        Highest kernel order.
    phi : {None, dict(int: numpy.ndarray)}, optional (default=None)
        If None, ``phi`` is computed from ``input_sig``; else, ``phi`` is used.
    form : {'sym', 'tri', 'symmetric', 'triangular'}, optional (default='sym')
        Form of the returned Volterra kernel (symmetric or triangular).
    cast_mode : {'real', 'imag', 'real-imag'}, optional (default='real-imag')
        Choose how complex number are casted to real numbers.

    Returns
    -------
    kernels : dict(int: numpy.ndarray)
        Dictionnary linking the Volterra kernel of order ``n`` to key ``n``.
    """

    # Checking that there is enough data samples
    _phaseKLS_check_feasability(input_sig.shape[0], M, N, form=form)

    # Input combinatoric
    if phi is None:
        phi = _phaseKLS_construct_phi(input_sig, M, N)

    # Initialization
    q_by_order = dict()
    r_terms = dict()
    size = dict()
    f = dict()
    kernels = dict()
    y_phase = dict()

    # QR decomposition
    for n in range(1, N+1):
        q_by_order[n], r_terms[(n, 0)] = \
                    sc_lin.qr(_cplx_to_real(phi[(n, 0)], cast_mode=cast_mode),
                              mode='economic')
        size[n] = r_terms[(n, 0)].shape[1]
        for k in range((n+1)//2):
            r_terms[(n, k)] = binomial(n, k) * \
                              np.dot(q_by_order[n-2*k].T,
                                     _cplx_to_real(phi[(n, k)],
                                                   cast_mode=cast_mode))

    # Projection on combinatorial basis
    for n, q_n in q_by_order.items():
        y_phase[n] = np.dot(q_n.T, _cplx_to_real(output_by_phase[n],
                                                 cast_mode=cast_mode))

    # Forward inverse
    for is_odd in [False, True]:
        y = np.concatenate([y_phase[n] for n in range(1+is_odd, N+1, 2)])
        r = np.bmat(
            [[r_terms.get((p+2*k, k), np.zeros((size[p], size[p+2*k])))
              for k in range(1-(p+1)//2, 1+(N-p)//2)]
             for p in range(1+is_odd, N+1, 2)])
        f[is_odd] = sc_lin.solve_triangular(r, y)

    # Re-arranging (odd and even) vectors f into volterra kernel of order n
    for is_odd in [False, True]:
        index = 0

        for n in range(1+is_odd, N+1, 2):
            nb_term = nb_coeff_in_kernel(M, n, form=form)
            kernels[n] = vector_to_kernel(f[is_odd][index:index+nb_term],
                                          M, n, form=form)
            index += nb_term

    return kernels


def _phaseKLS_check_feasability(nb_data, M, N, form='sym'):
    """Auxiliary function of phaseKLS() for checking feasability."""

    nb_coeff = 0
    for n in range(2 - N % 2, N+1, 2):
        nb_coeff += nb_coeff_in_kernel(M, n, form=form)
    assert_enough_data_samples(nb_data, nb_coeff, M, N, name='phaseKLS')


def _phaseKLS_construct_phi(signal, M, N):
    """Auxiliary function of phaseKLS() for Volterra basis computation."""

    return _termKLS_construct_phi(signal, M, N)


#=============================================#

def iterKLS(input_sig, output_by_phase, M, N, phi=None, form='sym',
            cast_mode='real-imag'):
    """
    Performs KLS method recursively on homogeneous-phase signals.

    Parameters
    ----------
    input_sig : numpy.ndarray
        Input signal.
    output_by_phase : numpy.ndarray
        Output signal separated in homogeneous-phase signals.
    M : int
        Memory length of kernels (in samples).
    N : int
        Highest kernel order.
    phi : {None, dict(int: numpy.ndarray)}, optional (default=None)
        If None, ``phi`` is computed from ``input_sig``; else, ``phi`` is used.
    form : {'sym', 'tri', 'symmetric', 'triangular'}, optional (default='sym')
        Form of the returned Volterra kernel (symmetric or triangular).
    cast_mode : {'real', 'imag', 'real-imag'}, optional (default='real-imag')
        Choose how complex number are casted to real numbers.

    Returns
    -------
    kernels : dict(int: numpy.ndarray)
        Dictionnary linking the Volterra kernel of order ``n`` to key ``n``.
    """

    # Checking that there is enough data samples
    _iterKLS_check_feasability(input_sig.shape[0], M, N, form=form)

    # Input combinatoric
    if phi is None:
        phi = _iterKLS_construct_phi(input_sig, M, N)

    # Initialization
    kernels = dict()
    f = dict()

    # Identification recursive on each homogeneous-phase signal
    for n in range(N, 0, -1):
        temp_sig = output_by_phase[n].copy()
        for n2 in range(n+2, N+1, 2):
            k = (n2-n)//2
            temp_sig -= binomial(n2, k) * np.dot(phi[(n2, k)], f[n2])
        f[n] = _KLS_core_computation(
            _cplx_to_real(phi[(n, 0)], cast_mode=cast_mode),
            _cplx_to_real(temp_sig, cast_mode=cast_mode))

    # Re-arranging vector f_n into volterra kernel of order n
    for n in range(1, N+1):
        kernels[n] = vector_to_kernel(f[n], M, n, form=form)

    return kernels


def _iterKLS_check_feasability(nb_data, M, N, form='sym'):
    """Auxiliary function of iterKLS() for checking feasability."""

    _orderKLS_check_feasability(nb_data, M, N, form='sym', name='iterKLS')


def _iterKLS_construct_phi(signal, M, N):
    """Auxiliary function of iterKLS() for Volterra basis computation."""

    return _termKLS_construct_phi(signal, M, N)


#=============================================#

def _cplx_to_real(sig_cplx, cast_mode='real-imag'):
    """
    Cast a numpy.ndarray of complex type to real type with a specified mode.

    Parameters
    ----------
    sig_cplx : numpy.ndarray
        Array to cast to real numbers.
    cast_mode : {'real', 'imag', 'real-imag'}, optional (default='real-imag')
        Choose how complex number are casted to real numbers.

    Returns
    -------
    sig_casted : numpy.ndarray
        Array ``sig_cplx`` casted to real numbers following ``cast_mode``.
    """

    if cast_mode not in {'real', 'imag', 'real-imag'}:
        warnings.warn("Unknown cast_mode, mode 'real-imag' used.", UserWarning)
        cast_mode = 'real'

    if cast_mode == 'real':
        return 2 * np.real(sig_cplx)
    elif cast_mode == 'imag':
        return 2 * np.real(sig_cplx)
    elif cast_mode == 'real-imag':
        return np.concatenate((np.real(sig_cplx), np.imag(sig_cplx)), axis=0)
    elif cast_mode == 'cplx':
        return sig_cplx


