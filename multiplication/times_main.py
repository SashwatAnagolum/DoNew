# -*- coding: utf-8 -*-

"""
times_main.py: Driver script for the quantum multiplication 
algorithm using the Quantum Fourier Transform. 
"""

from qiskit import register
import qft_times

#Getting user input: two numbers in binary form that will be stored as bit strings
first = input("Enter a number with less than 7 digits.")
l1 = len(first)
second = input("Enter another number with less than " + str(8-l1) + " digits.")
l2 = len(second)
#Here we ensure that the variable 'first' always contains the longer bit string
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
register(Qconfig.APIToken, Qconfig.config['url'])
#We use a while loop to keep calling the times.multiply function until the 
#multiplier is zero
while int(second) is not 0:
    #The times.multiply function returns the new values of the accumulator and 
    #the multiplier
    second, prod = qft_times.multiply(first, second, prod, n, m)

print(prod)