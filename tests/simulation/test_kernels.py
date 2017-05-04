# -*- coding: utf-8 -*-
"""
Test script for and pyvi.simulation.kernels

Notes
-----
@author: bouvier (bouvier@ircam.fr)
         Damien Bouvier, IRCAM, Paris

Last modified on 04 May 2017
Developed for Python 3.6.1
"""

#==============================================================================
# Importations
#==============================================================================

import numpy as np
from pyvi.system.dict import test, nl_damping
from pyvi.utilities.plotbox import plot_kernel_time, plot_kernel_freq


#==============================================================================
# Main script
#==============================================================================

if __name__ == '__main__':
    """
    Main script for testing.
    """

    # Parameters
    options = {'fs': 2000,
               'nl_order_max': 2,
               'holder_order': 1}
    T = 0.03

    # Test system
    system_test = test(mode='numeric')
    t_kernels = system_test.compute_kernels(T, which='time', **options)
    t_kernels, f_kernels = system_test.compute_kernels(T, which='both',
                                                       **options)
    f_kernels = system_test.compute_kernels(T, which='freq', **options)

    # Second-order system with nonlinear damping
    system = nl_damping(gain=1, f0=100, damping=0.2, nl_coeff=[1e-1, 3e-5])
    time_kernels, freq_kernels_from_time = system.compute_kernels(T,
                                                                  which='both',
                                                                  **options)
    freq_kernels = system.compute_kernels(T, which='freq', **options)

    N = len(time_kernels[1])
    time_vec = np.linspace(0, (N-1)/options['fs'], num=N)
    freq_vec = np.fft.fftshift(np.fft.fftfreq(N, d=1/options['fs']))

    plot_kernel_time(time_vec, time_kernels[1])
    plot_kernel_time(time_vec, time_kernels[2], style='wireframe')
    plot_kernel_freq(freq_vec, freq_kernels_from_time[1],
                     title='Transfer kernel of order 1 ' + \
                           '(computed from Volterra kernel).')
    plot_kernel_freq(freq_vec, freq_kernels_from_time[2], style='wireframe',
                     title='Transfer kernel of order 2 ' + \
                           '(computed from Volterra kernel).')
    plot_kernel_freq(freq_vec, freq_kernels[1],
                     title='Transfer kernel of order 1')
    plot_kernel_freq(freq_vec, freq_kernels[2], style='wireframe',
                     title='Transfer kernel of order 2')