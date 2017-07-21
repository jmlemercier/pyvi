# -*- coding: utf-8 -*-
"""
Test script for pyvi.separation.methods

Notes
-----
@author: bouvier (bouvier@ircam.fr)
         Damien Bouvier, IRCAM, Paris

Last modified on 19 July 2017
Developed for Python 3.6.1
"""

#==============================================================================
# Importations
#==============================================================================

import argparse
import numpy as np
import matplotlib.pyplot as plt
import pyvi.separation.methods as sep
from pyvi.system.dict import create_nl_damping
from pyvi.simulation.simu import SimulationObject
from pyvi.utilities.plotbox import plot_sig, plot_coll


#==============================================================================
# Main script
#==============================================================================


if __name__ == '__main__':
    """
    Main script for testing.
    """

    #####################
    ## Parsing options ##
    #####################

    parser = argparse.ArgumentParser()
    parser.add_argument('-ind', '--indentation', type=int, default=0)
    args = parser.parse_args()
    indent = args.indentation
    ss = ' ' * indent


    ################
    ## Parameters ##
    ################

    # System specification
    f0_voulue = 200
    damping = 0.7
    system = create_nl_damping(gain=1, f0=f0_voulue/(np.sqrt(1 - damping**2)),
                               damping=damping, nl_coeff=[3, 7e-4])

    # Input signal specification
    fs = 4410
    T = 0.2
    time_vec = np.arange(0, T, 1/fs)
    f1 = 100
    f2 = 133
    input_cplx = (1/4) * (np.exp(2j * np.pi * f1 * time_vec) + \
                          np.exp(2j * np.pi * f2 * time_vec))
    input_real = 2 * np.real(input_cplx)

    # Simulation specification
    nl_order_max = 3
    system = SimulationObject(system, fs=fs, nl_order_max=nl_order_max)


    ################
    ## Separation ##
    ################

    order_cplx = system.simulation(input_cplx, out_opt='output_by_order')
    order = system.simulation(input_real, out_opt='output_by_order')

    print(ss + 'Testing _PS method...', end=' ')
    _PS = sep._PS(N=nl_order_max)
    input_coll = _PS.gen_inputs(input_cplx)
    output_coll = np.zeros(input_coll.shape, dtype='complex128')
    for ind in range(input_coll.shape[0]):
        output_coll[ind] = system.simulation(input_coll[ind])
    order_est_PS = _PS.process_outputs(output_coll)
    assert np.allclose(order_cplx, order_est_PS), \
        'Separation error in _PS method.'
    print('Done.')

    print(ss + 'Testing AS method...', end=' ')
    AS = sep.AS(N=nl_order_max)
    input_coll = AS.gen_inputs(input_real)
    output_coll = np.zeros(input_coll.shape)
    for ind in range(input_coll.shape[0]):
        output_coll[ind] = system.simulation(input_coll[ind])
    order_est_AS = AS.process_outputs(output_coll)
    assert np.allclose(order, order_est_AS), 'Separation error in AS method.'
    print('Done.')

    print(ss + 'Testing PS method...', end=' ')
    PS = sep.PS(N=nl_order_max)
    input_coll = PS.gen_inputs(input_cplx)
    output_coll = np.zeros(input_coll.shape)
    for ind in range(input_coll.shape[0]):
        output_coll[ind] = system.simulation(input_coll[ind])
    sig_est_PS = PS.process_outputs(output_coll)
    assert np.allclose(order_cplx[nl_order_max-2:],
                       sig_est_PS[nl_order_max-1:nl_order_max+1]), \
        'Separation error in PS method.'
    print('Done.')

    print(ss + 'Testing PAS method...', end=' ')
    PAS = sep.PAS(N=nl_order_max)
    input_coll = PAS.gen_inputs(input_cplx)
    output_coll = np.zeros(input_coll.shape)
    for ind in range(input_coll.shape[0]):
        output_coll[ind] = system.simulation(input_coll[ind])
    order_est_PAS, term_est_PAS = PAS.process_outputs(output_coll,
                                                      raw_mode=True)
    assert np.allclose(order, order_est_PAS), 'Separation error in PAS method.'
    print('Done.')

    print(ss + 'Testing PAS_v2 method...', end=' ')
    PAS_v2 = sep.PAS_v2(N=nl_order_max)
    input_coll = PAS_v2.gen_inputs(input_cplx)
    output_coll = np.zeros(input_coll.shape)
    for ind in range(input_coll.shape[0]):
        output_coll[ind] = system.simulation(input_coll[ind])
    order_est_PASv2, term_est_PASv2 = PAS_v2.process_outputs(output_coll,
                                                             raw_mode=True)
    assert np.allclose(order, order_est_PASv2), \
        'Separation error in PASv2 method.'
    print('Done.')
