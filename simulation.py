# -*- coding: utf-8 -*-
"""
Set of functions for the numerical simulation of a nonlinear systems given
its state-space representation.

@author:    bouvier@ircam.fr
            Damien Bouvier, IRCAM, Paris

Developed for Python 3.5.1
"""

#==============================================================================
# Importations
#==============================================================================

import numpy as np
from scipy  import fftpack, linalg
from matplotlib import pyplot as plt


#==============================================================================
# Functions
#==============================================================================

def simulation(input_sig, matrices,
               m_pq=(lambda p,q: False, lambda p,q: None),
               n_pq=(lambda p,q: False, lambda p,q: None),
               sizes=(1, 1, 1), sym_bool=True,
               fs=44100, nl_order_max=1):

    ## Init ##
    # Unpack values
    A_m = matrices[0]
    B_m = matrices[1]
    C_m = matrices[2]
    D_m = matrices[3]

    input_dim = sizes[0]
    state_dim = sizes[1]
    output_dim = sizes[2]

    h_mpq_bool = m_pq[0]
    h_mpq = m_pq[1]
    h_npq_bool = n_pq[0]
    h_npq = n_pq[1]
    
    # Compute parameters
    sig_len = np.shape(input_sig)[0]
    sampling_time = 1/fs
    w_filter = linalg.expm(A_m*sampling_time)
    holder_bias_state = np.dot(np.linalg.inv(A_m),
                               w_filter - np.identity(state_dim))
    holder_bias_input = np.dot(holder_bias_state, B_m)
    
    # State and output initialization
    state_sig = np.zeros((state_dim, sig_len))
    state_by_order = np.zeros((nl_order_max, state_dim, sig_len))
    output_sig = np.zeros((output_dim, sig_len))

    # Enforce good shape when dimension is 1
    if input_dim == 1:
        input_sig.shape = (input_dim, sig_len)
        holder_bias_input.shape = (state_dim, input_dim)

    ## Numerical simulation ##
    # Main loop (on time indexes)
    for k in np.arange(sig_len-1):
        state_by_order[0,:,k+1] = \
                    np.dot(w_filter, state_by_order[0,:,k]) +\
                    np.dot(holder_bias_input, input_sig[:,k])
    
    state_sig = state_by_order.sum(0)
    output_sig = np.dot(C_m, state_sig) + np.dot(D_m, input_sig)
    return output_sig.transpose()

    
def hp_parameters():
    """
    Gives the linear matrices and nonlinear operators of the state-space
    representation for the loudspeaker SICA Z000900 
    """ 

    state_dim = 3
    input_dim = 1
    output_dim = 1
    sym_bool = True
    
    ## Linear part ##

    # Electric parameters
    Bl = 2.99 # Electodynamic driving parameter [T.m]
    Re = 5.7 # Electrical resistance of voice coil   [Ohm]
    Le  =   0.11e-3 # Coil inductance [H]
    # Mechanical parameters
    Mms = 1.9e-3; # Mechanical mass [kg]
    Cms = 544e-6; # Mechanical compliance [m.N-1]
    Qms = 4.6;
    k = 1 / Cms # Suspension stiffness [N.m-1]
    Rms = np.sqrt(k * Mms)/Qms; # Mechanical damping and drag force [kg.s-1]   
    # State-space matrices
    A_m = np.array([[-Re/Le, 0, -Bl/Le],
                    [0, 0, 1],
                    [Bl/Mms, -k/Mms, -Rms/Mms]]) # State-to-state matrix
    B_m = np.array([1/Le, 0, 0]); # Input-to-state matrix
    C_m = np.array([[1, 0, 0]]) # State-to-output matrix  
    D_m = np.zeros((output_dim, input_dim)) # Input-to-output matrix    

    ## Nonlinear part ##
    
    # Suspension stiffness polynomial expansion
    k_poly_coeff_v = np.array([k, -554420.0, 989026000])
    mpq_coeff = k_poly_coeff_v/Mms
    # Handles for fonction saying if Mpq and Npq functions are used
    h_mpq_bool = (lambda p, q: q==0) 
    h_npq_bool = (lambda p, q: False)
    # Handles for fonction giving the Mpq tensor
    h_mpq = (lambda p, q: hp_mpq_tensor(p, q, state_dim,  mpq_coeff(p)))
    h_npq = (lambda p, q: None)

    def hp_mpq_tensor(p, q, state_dim, coeff_value):
        """
        Gives the tensor form of the Mpq function (with q = 0)
        """ 
        if q==0:
            Mpq_tensor = np.zeros((state_dim,)*(p+1))
            idx = np.concatenate((np.array([2], dtype=int), np.ones(p, dtype=int)))
            Mpq_tensor[tuple(idx)] = coeff_value
            return Mpq_tensor
        else:
            return None
            
    return (A_m, B_m, C_m, D_m), (h_mpq_bool, h_mpq), (h_npq_bool, h_npq), \
    (input_dim, state_dim, output_dim), sym_bool


#==============================================================================
# Main script
#==============================================================================

if __name__ == '__main__':
    """
    Main script for testing
    """
    
    plt.close("all")
    
    # Input signal
    fs = 44100 # Sampling frequency
    T = 2 # Duration 
    f1 = 400 # Starting fundamental frequency
    f2 = 50 # Ending fundamental frequency
    A = 1 # Amplitude    
    
    time_vector = np.arange(0, T, step=1/fs)
    f0_vector = np.linspace(f1, f2, num=len(time_vector))
    sig = np.cos(2 * np.pi * f0_vector * time_vector)
    
    plt.figure(0)
    plt.plot(time_vector, sig)
    plt.xlim([0, 0.05])
    plt.show

    # Loudspeakers parameters
    matrices, m_pq, n_pq, sizes, sym_bool = hp_parameters()
    
    # Simulation
    output = simulation(sig, matrices, m_pq, n_pq, sizes, sym_bool, fs)
    
    plt.figure(1)
    plt.plot(time_vector, output)
    plt.xlim([0, 0.05])
    plt.show