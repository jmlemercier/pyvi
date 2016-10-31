# -*- coding: utf-8 -*-
"""
Toolbox for nonlinear order separation.

@author: bouvier (bouvier@ircam.fr)
         Damien Bouvier, IRCAM, Paris

Last modified on 31 Oct. 2016
Developed for Python 3.5.1
"""

#==============================================================================
# Importations
#==============================================================================

import numpy as np

#==============================================================================
# Functions
#==============================================================================

def separation_measure(signals_ref, signals_est):
    """
    Measure the efficiency of source separation using SDR, SIR and SAR metrics
    defined in:
    [#vincent2006performance] Emmanuel Vincent, Rémi Gribonval, and Cédric
    Févotte, "Performance measurement in blind audio source separation," IEEE
    Trans. on Audio, Speech and Language Processing, 14(4):1462-1469, 2006.
    """

    nb_src = signals_est.shape[0]

    def sig_projection(signal_est):
        """
        Projection of estimated signal on the reference signals.
        """
        A = np.corrcoef(signals_ref, y=signal_est )
        G = A[0:3, 0:3]
        D = A[3, 0:3]
        try:
            C = np.linalg.solve(G, D).reshape(nb_src, order='F')
        except np.linalg.linalg.LinAlgError:
            C = np.linalg.lstsq(G, D)[0].reshape(nb_src, order='F')
        return np.dot(C, signals_ref)
    
    sdr = []
    sir = []
    sar = []

    for i in range(nb_src):
        interference_err = sig_projection(signals_est[i]) - signals_ref[i]
        artificial_err = - signals_ref[i] - interference_err
        sdr.append(safe_db(np.sum(signals_ref[i]**2),
                           np.sum((interference_err + artificial_err)**2)))
        sir.append(safe_db(np.sum(signals_ref[i]**2),
                           np.sum((interference_err)**2)))
        sar.append(safe_db(np.sum((signals_ref[i] + interference_err)**2),
                           np.sum((artificial_err)**2)))

    return (sdr, sir, sar)


def safe_db(num, den):
    """
    dB computation with verification that the denominator is not zero.
    """
    if den == 0:
        return np.Inf
    return 10 * np.log10(num / den)

