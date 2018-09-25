# -*- coding: utf-8 -*-

"""
qft_multiplication.py: Multiplication using the Quantum Fourier Transform.
"""

import math
import operator
from qiskit import ClassicalRegister, QuantumRegister
from qiskit import QuantumCircuit
from qiskit import execute
from qiskit import register, available_backends, get_backend


def createInputState(qc, reg, n, pie):
    """
    Creates the input state for the given qubits, i.e. the qubits from register a.
    Note that the parameter 'n' is used to identify two things:
    n is the qubit to be operated upon within the register passed;
    n is the number of controlled phase rotation gates to be applied onto the qubit.
    The gates can be represented as follows:

    [1 0 0     0    ]
    [0 1 0     0    ]
    [0 0 1     0    ]
    [0 0 0 e^(1/2^k)]

    """
    qc.h(reg[n])    
    for i in range(0, n):
        qc.cu1(pie/float(2**(i+1)), reg[n-(i+1)], reg[n])

def evolveQFTState(qc, reg_a, reg_b, n, pie):
    """
    Evolves the QFT state of the register reg_a into the state reg_a + reg_b using
    controlled phase rotations conditioned on the qubits of reg_b.
    The parameter 'n' is used in the same manner as in the function createInputState.
    """ 
    for i in range(0, n+1):
        qc.cu1(pie/float(2**(i)), reg_b[n-i], reg_a[n])

def inverseQFT(qc, reg, n, pie):
    """
    Performs the inverse QFT operation on the passed qubit, i.e. performs
    the set of operations applied in the createInputState function in reverse order.
    """
    for i in range(0, n):
        qc.cu1(-1*pie/float(2**(n-i)), reg[n-(i+1)], reg[n])
    qc.h(reg[n])

def decrement(qc, reg_c, reg_d, n, pie):
    """
    Performs the decrement operation using the QFT conditioned on bit register d,
    i.e. 00...001, and negative phase rotation gates as outlined in
    the function createInputState.
    """
    for i in range(0, n+1):
        qc.cu1(-1*pie/float(2**(i)), reg_d[n-i], reg_c[n])               

def multiply(first, second, product, n, m):
    """
    Driver function for the multiplication implementation. Register a is the 
    accumulator. Register b holds the multiplicand, and c is used as to hold the
    multiplier. Register d holds the value 00...001, and is used to decrement 
    the multiplier. Classical registers cl and cl2 hold the final output and
    intermediary multiplier outputs respectively.

    Parameters:
    first: bit string representing the multiplicand
    second: bit string representing the multiplier
    product: bit string representing the current accumulator value
    n: integer representing the length of bit string first
    m: integer representing the length of bit string second

    Returns:
    multiplier: the value of the multiplier after decrementing
    accumulator: the value stored in the accumulator after addition
    """
    pie = math.pi

    a = QuantumRegister(m+n, "a") 
    b = QuantumRegister(m+n, "b") 
    c = QuantumRegister(m, "c") 
    d = QuantumRegister(m, "d") 
    cl = ClassicalRegister(m+n, "cl") 
    cl2 = ClassicalRegister(m, "cl2") 
    qc = QuantumCircuit(a, b, c, d, cl, cl2, name="qc")
    #Setting up register a to store the value of the accumulator
    for i in range(0, m+n):
        if product[i] == "1":  
            qc.x(a[m+n-(i+1)])
    #Setting up register b to store the value of the multiplicand
    for i in range(0, n):
        if first[i] == "1":
            qc.x(b[n-(i+1)])
    #Setting up register c to store the value of the multiplier
    for i in range(0, m):
        if second[i] == "1":
            qc.x(c[m-(i+1)])
    #Setting up register d to store value 00...001
    qc.x(d[0])
    #Applying the QFT to register a
    for i in range(0, m+n):
        createInputState(qc, a, m+n-(i+1), pie)
    #Applying the QFT to register c
    for i in range(m):
        createInputState(qc, c, m-(i+1), pie)
    #Evolving the register a from |a> to |a+b>
    for i in range(0, m+n):
        evolveQFTState(qc, a, b, m+n-(i+1), pie) 
    #Evolving the register c from |c> to |c-1>
    for i in range(0, m):
        decrement(qc, c, d, m-(i+1), pie)
    #Performing the inverse QFT on register c
    for i in range(0, m):
        inverseQFT(qc, c, i, pie)
    #Performing the inverse QFT on register a
    for i in range(0, m+n):
        inverseQFT(qc, a, i, pie)
    #Measuring the value of register a and storing it in register cl;
    #Note that as the bits were in superposition, the noise present in the 
    #circuit will result in the possible returning of 1s instead of 0s and
    #vice versa
    for i in range(0, m+n):
        qc.measure(a[i], cl[i])
    #Measuring the value of register c and storing it in register cl2
    for i in range(0, m):
        qc.measure(c[i], cl2[i])
    #We repeat the experiment 1024 times to ensure that the correct result,
    #which will have the highest probability of occuring, has occured a 
    #sufficiently larger amount of times than other results
    result = execute(qc, backend='ibmq_qasm_simulator', 
                      shots=1024).result()
    counts = result.get_counts("qc")
    #Get the key(values of cl/cl2) which have occured the maximum amount of times
    output = max(counts.items(), key=operator.itemgetter(1))[0]
    #Split the result in the values of cl2 and cl
    multiplier, accumulator = str(output).split(" ")    
    return multiplier, accumulator

