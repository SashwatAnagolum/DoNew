# -*- coding: utf-8 -*-

"""
gcd.py: Finds the greatest common divisor of two given numbers.
"""

import math
from qiskit import ClassicalRegister, QuantumRegister
from qiskit import QuantumCircuit, CompositeGate
from qiskit import register
import gcd_main
import subtract
import times_main

def compute_gcd(first, second, n, gcd_factor):
    """
    Computes the GCD of two numbers stored in QuantumRegisters a and b.
    Parameters:
    first, second, gcd_factor: Bit strings
    n: integer representing the length of the bit strings
    Returns:
    zero_status, gcd_factor, a_value, equality_status, b_value: Bit strings
     representing whether one or both of the numbers are equal to zero, 
     the factor by which to multiply b_value to obtain the GCD, the value
     stored in register a, whether the two numbers are equal to each other, 
     and the value stored in register b, respectively. 
    """  
    a = QuantumRegister(n, "aq")
    b = QuantumRegister(n, "bq")
    anc = QuantumRegister(2, "ancq")
    res = QuantumRegister(n, "resq")
    zero = QuantumRegister(2, "zq")
    anc_cl = ClassicalRegister(2, "anccl")
    zero_cl = ClassicalRegister(2, "zcl")
    a_cl = ClassicalRegister(n, "acl")
    b_cl = ClassicalRegister(n, "bcl")    
    res_cl = ClassicalRegister(n, "cl")
    qc = QuantumCircuit(a, b, anc, res, zero, anc_cl, zero_cl, 
        res_cl, a_cl, b_cl, name="qc")

    for i in range(0, n):
        if first[i] == "1":
            qc.x(a[n-(i+1)])
 
    for i in range(0, n):
        if second[i] == "1":
            qc.x(b[n-(i+1)])

    for i in range(0, n):
        if gcd_factor[i] == "1":
             qc.x(res[n-(i+1)])           

    qc.measure(a,res_cl)
    qc.x(zero[0]).c_if(res_cl, 0)
    qc.measure(b, res_cl)
    qc.x(zero[1]).c_if(res_cl, 0)
    qc.measure(zero, zero_cl)
    #Resetting the zero qreg to 0, with zero_cl holding the zero status    
    qc.x(zero[0]).c_if(res_cl, 0)  
    qc.measure(a,res_cl) 
    qc.x(zero[1]).c_if(res_cl, 0)   
    #Resetting res_cl to zero again.
    for i in range(n):
        qc.measure(zero[0], res_cl[i]) 

    #Checking for equality
    args = [a[x] for x in range(n)] + [b[x] for x in range(n)]
    csub = CompositeGate("csub", [math.pi], args, circuit ="qc")
    csub = subtract.subtract(qc, n, math.pi, a, b, csub, -1)
    qc.measure(a, res_cl)
    qc.x(zero[0]).c_if(res_cl, 0)
    cadd = CompositeGate("csub", [math.pi], args, circuit ="qc")
    cadd = subtract.subtract(qc, n, math.pi, a, b, cadd, 1)

    #Checking if either b, a or both are zero - if they are, then swap
    #the 1 in res_q out for a zero
    qc.swap(res[0], zero[0]).c_if(zero_cl, 1)
    qc.swap(res[0], zero[0]).c_if(zero_cl, 2)
    qc.swap(res[0], zero[0]).c_if(zero_cl, 3)
    #flip the 1 in zero_q to make zero_q on the zero state again.
    qc.x(zero[0]).c_if(zero_cl, 1)
    qc.x(zero[0]).c_if(zero_cl, 2)
    qc.x(zero[0]).c_if(zero_cl, 3)        

    zero_status, gcd_factor, b_value, equality_status, a_value  =  \
     gcd_main.gcd(qc, a, b, res, anc, zero, zero_cl, anc_cl, res_cl,
      n, a_cl, b_cl)

    return zero_status, gcd_factor, b_value, equality_status, a_value


first = input("Enter a binary number.")
second = input("Enter another binary number.")

l1 = len(first)
l2 = len(second)

#Add a zero to the left of each bit string after making them
#the same length
if l1>l2:
    second = ("0")*(l1 - l2) + second
elif l2>l1 or l1 == l2:
    first = ("0")*(l2 - l1) + first

first_temp = first if int(first) > int(second) else second
second_temp = first if int(first) < int(second) else second

first = first_temp
second = second_temp

gcd_factor = ("0")*(len(first) - 1) + "1"

import Qconfig
register(Qconfig.APIToken, Qconfig.config['url'])

zero_status = 0
equality_status = 0

while int(zero_status)  == 0 and int(equality_status) == 0:
    if first < second:
         first, second = second, first
    zero_status, gcd_factor, second, equality_status, first = \
     compute_gcd(first , second, max(l1, l2), gcd_factor)

print(times_main.times(second, gcd_factor))