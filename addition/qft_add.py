# -*- coding: utf-8 -*-

"""
qft_add.py: Addition using the quantum Fourier transform.
"""

import math
import operator
from qiskit import ClassicalRegister, QuantumRegister
from qiskit import QuantumCircuit
from qiskit import execute
from qiskit import register, available_backends, get_backend

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
    
    Evolves the state |F(ψ(reg_a))> to |F(ψ(reg_a+reg_b))> using the quantum 
    Fourier transform conditioned on the qubits of the reg_b.
    Apply repeated phase rotations with parameters being pi divided by 
    increasing powers of two.
    """
    for i in range(0, n+1):
        qc.cu1(pie/float(2**(i)), reg_b[n-i], reg_a[n])

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

def add(first, second, n):
    pie = math.pi

    a = QuantumRegister(n+1, "a") 
    b = QuantumRegister(n+1, "b")     
    cl = ClassicalRegister(n+1, "cl") 
    qc = QuantumCircuit(a, b, cl, name="qc")
    #Flip the corresponding qubit in register a if a bit in the string
    #first is a 1
    for i in range(0, n):
        if first[i] == "1":
            qc.x(a[n-(i+1)])
    #Flip the corresponding qubit in register b if a bit in the string
    #second is a 1
    for i in range(0, n):
        if second[i] == "1":
            qc.x(b[n-(i+1)])
    #Compute the Fourier transform of register a
    for i in range(0, n+1):
        createInputState(qc, a, n-i, pie)
    #Add the two numbers by evolving the Fourier transform F(ψ(reg_a))>
    #to |F(ψ(reg_a+reg_b))>
    for i in range(0, n+1):
        evolveQFTState(qc, a, b, n-i, pie) 
    #Compute the inverse Fourier transform of register a
    for i in range(0, n+1):
        inverseQFT(qc, a, i, pie)
    #Measure qubits
    for i in range(0, n+1):
        qc.measure(a[i], cl[i])
    print(qc.qasm())
    #Import config file and set API Token and url
    import Qconfig
    register(Qconfig.APIToken, Qconfig.config['url'])
    #Select backend and execute job
    result = execute(qc, backend='ibmq_qasm_simulator', 
                      shots=256).result()
    counts = result.get_counts("qc")
    print(counts)
    #Select result with maximum probabilities
    output = max(counts.items(), key=operator.itemgetter(1))[0]
    print(output)

#Take two numbers as user input in binary form   
first = input("Enter a number with less than 10 digits.")
l1 = len(first)
second = input("Enter another number with less than 10 digits.")
l2 = len(second)
#Making sure that 'first' and 'second' are of the same length 
#by padding the smaller string with zeros
if l2>l1:
    first,second = second, first
    l2, l1 = l1, l2
second = ("0")*(l1-l2) + second

add(first, second, l1)