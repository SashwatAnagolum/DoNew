# -*- coding: utf-8 -*-

"""
times_main.py: Driver script for the quantum multiplication algorithm 
using the Quantum Fourier Transform. 
"""

from qiskit import register
import qft_times

def times(first, second):
    """
    Computes the product of two bit strings first and second.
    Parameters:
    first, second: Bit strings representing the numbers to be multiplied
    Returns:
    prod: Bit string representing the product of first and second
    """
    l1 = len(first)
    l2 = len(second)
    #Here we ensure that the variable 'first' always contains
    #the longer bit string
    if l1 > l2:
        n = l1
        m = l2
    else:
        first, second = second, first
        n = l2
        m = l1
    #Initially setting the product of the two numbers to zero
    prod = ("0")*(m+n)

    import Qconfig
    #We use a while loop to keep calling the times.multiply function
    #until the 
    #multiplier is zero
    while int(second) is not 0:
        #The times.multiply function returns the new values of the 
        #accumulator and 
        #the multiplier
        second, prod = qft_times.multiply(first, second, prod, n, m)
    return prod