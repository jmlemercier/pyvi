# -*- coding: utf-8 -*-
"""
Test script for and pyvi.order_separation.tools

@author: bouvier (bouvier@ircam.fr)
         Damien Bouvier, IRCAM, Paris

Last modified on 6 June 2017
Developed for Python 3.6.1
"""

#==============================================================================
# Importations
#==============================================================================

import numpy as np
from pyvi.order_separation.tools import estimation_measure


#==============================================================================
# Main script
#==============================================================================

if __name__ == '__main__':
    """
    Main script for testing.
    """

    N = 3
    L = 1000
    size=(N, L)

    sig = np.random.uniform(low=-1.0, high=1.0, size=size)
    for sigma in [0, 0.001, 0.01, 0.1, 1]:
        sig_est = sig + np.random.normal(scale=sigma, size=size)

        error = estimation_measure(sig, sig_est, db=False)
        error_db = estimation_measure(sig, sig_est)
        print('Added noise factor:', sigma)
        print('Relative error     :', error)
        print('Relative error (dB):', error_db)
        print()
