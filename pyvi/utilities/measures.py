# -*- coding: utf-8 -*-
"""
Module for error measure functions.

Functions
---------
separation_error :
    Returns the relative error between nonlinear orders and their estimates.
identification_error :
    Returns the relative error between kernels and their estimates.
evaluation_error :
    Returns the relative error between a reference signal and an estimation.

Developed for Python 3.6
@author: Damien Bouvier (Damien.Bouvier@ircam.fr)
"""

__all__ = ['separation_error', 'identification_error', 'evaluation_error']


#==============================================================================
# Importations
#==============================================================================

from ..utilities.mathbox import rms, safe_db


#==============================================================================
# Functions
#==============================================================================

def separation_error(signals_ref, signals_est, db=True):
    """
    Returns the relative error between nonlinear orders and their estimates.

    This error is computed as the RMS value of the error estimation divided by
    the RMS values of the true orders, for each order.

    Parameters
    ----------
    signals_ref : array_like
        True homogeneous orders.
    signals_est : array_like
        Estimated homogeneous orders.

    Returns
    -------
    numpy.ndarray
        List of normalized-RMS error values.
    """

    rms_error = rms(signals_ref - signals_est, axis=1)
    rms_ref = rms(signals_ref, axis=1)
    rms_ref[rms_ref == 0] = 1
    if db:
        return safe_db(rms_error, rms_ref)
    else:
        return rms_error / rms_ref


def identification_error(kernels_ref, kernels_est, db=True):
    """
    Returns the relative error between kernels and their estimates.

    This error is computed as the RMS value of the error estimation divided by
    the RMS values of the true kernels, for each order.

    Parameters
    ----------
    kernels_ref : dict(int: numpy.ndarray)
        Dictionnary of the true kernels.
    kernels_est : dict(int: numpy.ndarray)
        Dictionnary of the estimated kernels.

    Returns
    -------
    errors : list(floats)
        List of normalized-RMS error values.
    """

    # Initialization
    errors = []

    # Loop on all estimated kernels
    for order, kernel_est in sorted(kernels_est.items()):
        if order in kernels_ref:
            rms_error = rms(kernel_est - kernels_ref[order])
            rms_ref = rms(kernels_ref[order])
            if rms_ref == 0:
                rms_ref = 1
        else:
            rms_error = rms(kernel_est)
            rms_ref = 1

        if db:
            errors.append(safe_db(rms_error, rms_ref))
        else:
            errors.append(rms_error / rms_ref)

    return errors


def evaluation_error(signal_ref, signal_est, db=True):
    """
    Returns the relative error between a reference signal and an estimation.

    Parameters
    ----------
    signal_ref : numpy.ndarray
        Reference signal.
    signal_est : numpy.ndarray
        Estimation of the reference signal

    Returns
    -------
    float
        Normalized-RMS error value.
    """

    rms_error = rms(signal_est - signal_ref)
    rms_ref = rms(signal_ref)

    if db:
        return float(safe_db(rms_error, rms_ref))
    else:
        return float(rms_error / rms_ref)

