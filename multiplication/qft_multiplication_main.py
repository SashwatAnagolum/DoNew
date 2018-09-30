# -*- coding: utf-8 -*-

"""
qft_multiplication_main.py: Driver script for quantum mulitplication algorithm 
using the Quantum Fourier Transform. 
"""

from qiskit import register
import qft_multiplication

#Getting user input: two numbers in binary form that will be stored as bit strings
first = input("Enter a number with less than 7 digits.")
l1 = len(first)
second = input("Enter another number with less than " + str(8-l1) + " digits.")
l2 = len(second)
#Here we ensure that the variable first always contains the longer bit string
if l1 > l2:
    n = l1
    m = l2
else:
    first, second = second, first
    n = l2
    m = l1

#Initially setting the product of the two numbers to zero
prod = ("0")*(m+n)

Qconfig = {
    "APItoken": "f9be8ebe6cc0b5c9970ca5ae86acad18c1dfb3844ed12b381a458536fcbf46499d62dbb33da9a07627774441860c64ac44e76a6f27dc6f09bba7e0f2ce68e9ff",
    "url": "https://quantumexperience.ng.bluemix.net/api"
}

register(Qconfig['APItoken'], Qconfig['url'])
#We use a while loop to keep calling the times.multiply function until the 
#multiplier is zero
while int(second) is not 0:
    #The times.multiply function returns the new values of the accumulator and 
    #the multiplier
    second, prod = times.multiply(first, second, prod, n, m)
