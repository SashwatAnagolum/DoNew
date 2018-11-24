# -*- coding: utf-8 -*-

"""
qft_subtract.py: Subtraction using the quantum Fourier transform.
"""

from math import pi
from qforest_matherror import QForestMathError, RegisterError

def createInputState(qc, reg, n, pie):
    """
    Computes the quantum Fourier transform of reg, one qubit at
    a time.
    Apply one Hadamard gate to the nth qubit of the quantum register reg, and 
    then apply repeated phase rotations with parameters being pi divided by 
    increasing powers of two.
    """ 
    qc.h(reg[n])    
    for i in range(0, n):
        qc.cu1(pie/float(2**(i+1)), reg[n-(i+1)], reg[n])    

def evolveQFTState(qc, reg_a, reg_b, n, pie):
    """
    Evolves the state |F(ψ(reg_a))> to |F(ψ(reg_a-reg_b))> using the quantum 
    Fourier transform conditioned on the qubits of the reg_b.
    Apply repeated phase rotations with parameters being pi divided by 
    increasing powers of two.
    """
    l = len(reg_b)
    for i in range(0, n+1):
        if (n-i) > l - 1:
            pass
        else:
            qc.cu1(-1*pie/float(2**(i)), reg_b[n-i], reg_a[n])

def inverseQFT(qc, reg, n, pie):
    """
    Performs the inverse quantum Fourier transform on a register reg.
    Apply repeated phase rotations with parameters being pi divided by 
    decreasing powers of two, and then apply a Hadamard gate to the nth qubit
    of the register reg.
    """
    for i in range(0, n):
        qc.cu1(-1*pie/float(2**(n-i)), reg[i], reg[n])
    qc.h(reg[n])

def subtract(reg_a, reg_b, circ):
    try:
        from qiskit import QuantumRegister, QuantumCircuit
    except ImportError:
        raise QForestMathError("Please install qiskit! " + \
            "You can install it using the pip tool:" +\
            " pip install qiskit.")

    if isinstance(reg_a, QuantumRegister) and \
     isinstance(reg_b, QuantumRegister) and \
     isinstance(circ, QuantumCircuit):
        pass
    else:
        raise QForestMathError("Expected two QuantumRegister" +
            " objects and one QuantumCircuit object! Please check the"+
            " objects passed to the subtract() function.")

    if len(reg_a) < len(reg_b):
        raise RegisterError("Expected first QuantumRegister object to be" + \
            " of equal or greater length than second! Passed QuantumRegisters have lengths "+ \
            str(len(reg_a)) + " and " + str(len(reg_b)) + ".")
   
    pie = pi
    n = len(reg_a) 

    #Compute the Fourier transform of register a
    for i in range(0, n):
        createInputState(circ, reg_a, n-(i+1), pie)
    #Add the two numbers by evolving the Fourier transform F(ψ(reg_a))>
    #to |F(ψ(reg_a+reg_b))>
    for i in range(0, n):
        evolveQFTState(circ, reg_a, reg_b, n-(i+1), pie) 
    #Compute the inverse Fourier transform of register a
    for i in range(0, n):
        inverseQFT(circ, reg_a, i, pie)
