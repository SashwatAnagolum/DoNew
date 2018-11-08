# -*- coding: utf-8 -*-

"""
subtract.py: Subtraction using the quantum Fourier transform for 
             the gcd algorithm.
"""

import operator
import math
from qiskit import ClassicalRegister, QuantumRegister
from qiskit import QuantumCircuit
from qiskit import execute, register
from qiskit import available_backends, get_backend

def createInputState(qc, reg, n, pie, cgate, anc =None, num =None):
    """
    Computes the quantum Fourier transform of reg, one qubit at
    a time.
    Apply one Hadamard gate to the nth qubit of the quantum register reg, and 
    then apply repeated phase rotations with parameters being pi divided by 
    increasing powers of two.
    Parameters:
    qc: QuantumCircuit
    reg, anc: QuantumRegisters
    cgate: CompositeGate
    n, num: integers
    pie: float representing pi (3.14....)
    Returns:
    None
    """ 
    #Attach instructions to the CompositeGate cgate to compute the QFT
    #of reg
    if num == None:
        cgate._attach(qc.h(reg[n]))         
        for i in range(0, n):
            cgate._attach(qc.cu1(pie/float(2**(i+1)), reg[n-(i+1)],
             reg[n]))          
    else:
        cgate._attach(qc.h(reg[n]).c_if(anc, num))  
        for i in range(0, n):
            cgate._attach(qc.cu1(pie/float(2**(i+1)), reg[n-(i+1)],
             reg[n]).c_if(anc, num))  

def evolveQFTState(qc, reg_a, reg_b, n, pie, fact, cgate, anc =None, num =None):
    """
    Evolves the state |F(ψ(reg_a))> to |F(ψ(reg_a-reg_b))> using the quantum 
    Fourier transform conditioned on the qubits of the reg_b.
    Apply repeated phase rotations with parameters being pi divided by 
    increasing powers of two.
    Parameters:
    qc: QuantumCircuit
    reg_a, reg_b, anc: QuantumRegisters
    cgate: CompositeGate
    n, num, fact: integers
    pie: float representing pi (3.14....)
    Returns:
    None    
    """
    #Attach instructions to the CompositeGate cgate to evolve the QFT state
    #of reg_a
    if num == None:
        for i in range(0, n+1):
            cgate._attach(qc.cu1(fact*pie/float(2**(i)), reg_b[n-i],
             reg_a[n]))           
    else:    
        for i in range(0, n+1):
            cgate._attach(qc.cu1(fact*pie/float(2**(i)), reg_b[n-i],
             reg_a[n]).c_if(anc, num))

def inverseQFT(qc, reg, n, pie, cgate, anc =None, num =None):
    """
    Performs the inverse quantum Fourier transform on a register reg.
    Apply repeated phase rotations with parameters being pi divided by 
    decreasing powers of two, and then apply a Hadamard gate to the nth qubit
    of the register reg.
    Parameters:
    qc: QuantumCircuit
    reg, anc: QuantumRegisters
    cgate: CompositeGate
    n, num: integers
    pie: float representing pi (3.14....)
    Returns:
    None    
    """
    #Attach instructions to the CompositeGate cgate to compute the inverse
    #QFT of reg
    if num == None:
        for i in range(0, n):
            cgate._attach(qc.cu1(-1*pie/float(2**(n-i)), reg[i],
             reg[n]))
        cgate._attach(qc.h(reg[n]))                
    else:
        for i in range(0, n):
            cgate._attach(qc.cu1(-1*pie/float(2**(n-i)), reg[i],
             reg[n]).c_if(anc, num))
        cgate._attach(qc.h(reg[n]).c_if(anc, num))

def subtract(qc, n, pie, a, b, cgate, fact, anc =None, num =None):
    """
    Computes the difference of two QuantumRegisters a and b.
    Parameters:
    qc: QuantumCircuit
    a, b, anc: QuantumRegisters
    cgate: CompositeGate
    n, num, fact: integers
    pie: float representing pi (3.14....)
    Returns:
    cgate: CompositeGate
    """
    #Compute the Fourier transform of register a
    for i in range(0, n):
        createInputState(qc, a, n-(i+1), pie, cgate, anc, num)
    #Add the two numbers by evolving the Fourier transform F(ψ(reg_a))>
    #to |F(ψ(reg_a-reg_b))>
    for i in range(0, n):
        evolveQFTState(qc, a, b, n-(i+1), pie, fact, cgate, anc, num) 
    #Compute the inverse Fourier transform of register a
    for i in range(0, n):
        inverseQFT(qc, a, i, pie, cgate, anc, num)

    return cgate