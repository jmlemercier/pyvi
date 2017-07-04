# -*- coding: utf-8 -*-
"""
Test script for and pyvi.separation.order_separation

Notes
-----
@author: bouvier (bouvier@ircam.fr)
         Damien Bouvier, IRCAM, Paris

Last modified on 12 June 2017
Developed for Python 3.6.1
"""

#==============================================================================
# Importations
#==============================================================================

import numpy as np
import pyvi.separation.separation as sep
import matplotlib.pyplot as plt
from pyvi.system.dict import create_nl_damping
from pyvi.simulation.simu import SimulationObject
from pyvi.utilities.plotbox import plot_sig_coll


#==============================================================================
# Main script
#==============================================================================


if __name__ == '__main__':
    """
    Main script for testing.
    """

    print()

    ################
    ## Parameters ##
    ################

    fs = 4410
    T = 0.2
    time_vec = np.arange(0, T, 1/fs)
    f1 = 100
    f2 = 133
    input_cplx = np.exp(2j * np.pi * f1 * time_vec) + \
                 np.exp(2j * np.pi * f2 * time_vec)
    input_real = np.real(input_cplx)

    nl_order_max = 3
    system = SimulationObject(create_nl_damping(nl_coeff=[1e-1, 3e-5]), fs=fs,
                              nl_order_max=nl_order_max)


    ################
    ## Separation ##
    ################

    print('Computing PS method ...', end=' ')
    PS = sep.PS(N=nl_order_max)
    out_order_cplx = system.simulation(input_cplx, out_opt='output_by_order')
    input_coll = PS.gen_inputs(input_cplx)
    output_coll = np.zeros(input_coll.shape, dtype='complex128')
    for ind in range(input_coll.shape[0]):
        output_coll[ind] = system.simulation(input_coll[ind])
    out_order_est_cplx = PS.process_outputs(output_coll)
    print('Done.')

    out_order_amp = system.simulation(input_real, out_opt='output_by_order')

    print('Computing AS method ...', end=' ')
    AS = sep.AS(N=nl_order_max)
    input_coll = AS.gen_inputs(input_real)
    output_coll = np.zeros(input_coll.shape)
    for ind in range(input_coll.shape[0]):
        output_coll[ind] = system.simulation(input_coll[ind])
    out_order_est_amp = AS.process_outputs(output_coll)
    print('Done.')

    out_order_phase = system.simulation(2*input_real, out_opt='output_by_order')

    print('Computing PAS method ...', end=' ')
    PAS = sep.PAS(N=nl_order_max)
    input_coll = PAS.gen_inputs(input_cplx)
    output_coll = np.zeros(input_coll.shape)
    for ind in range(input_coll.shape[0]):
        output_coll[ind] = system.simulation(input_coll[ind])
    out_order_est_phase = PAS.process_outputs(output_coll)
    out_order_est_phase_raw = PAS.process_outputs(output_coll, raw_mode=True)
    print('Done.')

    print('Computing PAS_v2 method ...', end=' ')
    PAS_v2 = sep.PAS_v2(N=nl_order_max)
    input_coll = PAS_v2.gen_inputs(input_cplx)
    output_coll = np.zeros(input_coll.shape)
    for ind in range(input_coll.shape[0]):
        output_coll[ind] = system.simulation(input_coll[ind])
    out_order_est_phasev2 = PAS_v2.process_outputs(output_coll)
    out_order_est_phasev2_raw = PAS_v2.process_outputs(output_coll,
                                                       raw_mode=True)
    print('Done.')

    print('Computing realPS method ...', end=' ')
    realPS = sep.realPS(N=nl_order_max)
    input_coll = realPS.gen_inputs(input_cplx)
    output_coll = np.zeros(input_coll.shape)
    for ind in range(input_coll.shape[0]):
        output_coll[ind] = system.simulation(input_coll[ind])
    out_phase_est = realPS.process_outputs(output_coll)
    print('Done.')


    ##################
    ## Signal plots ##
    ##################

    print('Printing plots ...', end=' ')

    plt.figure('Method PS - True and estimated orders')
    plt.clf()
    for n in range(nl_order_max):
        plt.subplot(nl_order_max, 2, 2*n+1)
        plt.plot(time_vec, np.real(out_order_cplx[n]), 'b')
        plt.subplot(nl_order_max, 2, 2*n+2)
        plt.plot(time_vec, np.real(out_order_est_cplx[n]), 'r')
    plt.show()

    plt.figure('Method PS - True orders and error')
    plt.clf()
    for n in range(nl_order_max):
        plt.subplot(nl_order_max, 2, 2*n+1)
        plt.plot(time_vec, np.real(out_order_cplx[n]), 'b')
        plt.subplot(nl_order_max, 2, 2*n+2)
        plt.plot(time_vec, np.real(out_order_cplx - out_order_est_cplx)[n], 'r')
    plt.show()

    plt.figure('Method AS - True and estimated orders')
    plt.clf()
    for n in range(nl_order_max):
        plt.subplot(nl_order_max, 2, 2*n+1)
        plt.plot(time_vec, out_order_amp[n], 'b')
        plt.subplot(nl_order_max, 2, 2*n+2)
        plt.plot(time_vec, out_order_est_amp[n], 'r')
    plt.show()

    plt.figure('Method AS - True orders and error')
    plt.clf()
    for n in range(nl_order_max):
        plt.subplot(nl_order_max, 2, 2*n+1)
        plt.plot(time_vec, out_order_amp[n], 'b')
        plt.subplot(nl_order_max, 2, 2*n+2)
        plt.plot(time_vec, (out_order_amp - out_order_est_amp)[n], 'r')
    plt.show()

    plt.figure('Method PAS - True and estimated orders')
    plt.clf()
    for n in range(nl_order_max):
        plt.subplot(nl_order_max, 2, 2*n+1)
        plt.plot(time_vec, out_order_phase[n], 'b')
        plt.subplot(nl_order_max, 2, 2*n+2)
        plt.plot(time_vec, out_order_est_phase[n], 'r')
    plt.show()

    plt.figure('Method PAS - True orders and error')
    plt.clf()
    for n in range(nl_order_max):
        plt.subplot(nl_order_max, 2, 2*n+1)
        plt.plot(time_vec, out_order_phase[n], 'b')
        plt.subplot(nl_order_max, 2, 2*n+2)
        plt.plot(time_vec, (out_order_phase - out_order_est_phase)[n], 'r')
    plt.show()

    plt.figure('Method raw-PAS - Estimated terms')
    plt.clf()
    nb_col = 2*(nl_order_max+1)
    shape = (nl_order_max, nb_col)
    for n in range(1, nl_order_max+1):
        for q in range(0, n+1):
            pos = (n-1, nl_order_max - n + 2*q)
            ax = plt.subplot2grid(shape, pos, colspan=2)
            ax.plot(time_vec, np.real(out_order_est_phase_raw[(n, q)]), 'b')
            ax.plot(time_vec, np.imag(out_order_est_phase_raw[(n, q)]), 'r')

    plt.figure('Method PAS_v2 - True and estimated orders')
    plt.clf()
    for n in range(nl_order_max):
        plt.subplot(nl_order_max, 2, 2*n+1)
        plt.plot(time_vec, out_order_phase[n], 'b')
        plt.subplot(nl_order_max, 2, 2*n+2)
        plt.plot(time_vec, out_order_est_phasev2[n], 'r')
    plt.show()

    plt.figure('Method PAS_v2 - True orders and error')
    plt.clf()
    for n in range(nl_order_max):
        plt.subplot(nl_order_max, 2, 2*n+1)
        plt.plot(time_vec, out_order_phase[n], 'b')
        plt.subplot(nl_order_max, 2, 2*n+2)
        plt.plot(time_vec, (out_order_phase - out_order_est_phasev2)[n], 'r')
    plt.show()

    plt.figure('Method raw-PAS_v2 - Estimated terms')
    plt.clf()
    nb_col = 2*(nl_order_max+1)
    shape = (nl_order_max, nb_col)
    for n in range(1, nl_order_max+1):
        for q in range(0, n+1):
            pos = (n-1, nl_order_max - n + 2*q)
            ax = plt.subplot2grid(shape, pos, colspan=2)
            ax.plot(time_vec, np.real(out_order_est_phasev2_raw[(n, q)]), 'b')
            ax.plot(time_vec, np.imag(out_order_est_phasev2_raw[(n, q)]), 'r')

    plt.figure('Method realPS - Estimated terms')
    plt.clf()
    title_plots = []
    for n in range(nl_order_max+1):
        title_plots.append('Phase {}'.format(n))
    plot_sig_coll(time_vec, out_phase_est[:nl_order_max+1],
                  title='Method realPS - Estimated terms',
                  title_plots=title_plots)
    print('Done.')