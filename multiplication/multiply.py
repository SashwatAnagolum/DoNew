# -*- coding: utf-8 -*-

"""
multiply.py: Multiply two numbers using repeated fourier 
               transform based addition.
"""

from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister
from qiskit import Aer, execute
from math import pi

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
        qc.cu1(pie / float(2**(i + 1)), reg[n - (i + 1)], reg[n])


def evolveQFTState(qc, reg_a, reg_b, n, pie, factor):
    """  
    Evolves the state |F(ψ(reg_a))> to |F(ψ(reg_a+reg_b))> using the quantum 
    Fourier transform conditioned on the qubits of the reg_b.
    Apply repeated phase rotations with parameters being pi divided by 
    increasing powers of two.
    """
    l = len(reg_b)
    for i in range(0, n + 1):
        if (n - i) > l - 1:
            pass
        else:
            qc.cu1(factor*pie / float(2**(i)), reg_b[n - i], reg_a[n])


def inverseQFT(qc, reg, n, pie):
    """
    Performs the inverse quantum Fourier transform on a register reg.
    Apply repeated phase rotations with parameters being pi divided by 
    decreasing powers of two, and then apply a Hadamard gate to the nth qubit
    of the register reg.
    """
    for i in range(0, n):
        qc.cu1(-1 * pie / float(2**(n - i)), reg[i], reg[n])
    qc.h(reg[n])


def add(reg_a, reg_b, circ, factor):
    """
    Add two quantum registers reg_a and reg_b, and store the result in 
    reg_a.
    """
    pie = pi
    n = len(reg_a) - 1

    # Compute the Fourier transform of register a
    for i in range(0, n + 1):
        createInputState(circ, reg_a, n - i, pie)
    # Add the two numbers by evolving the Fourier transform F(ψ(reg_a))>
    # to |F(ψ(reg_a+reg_b))>
    for i in range(0, n + 1):
        evolveQFTState(circ, reg_a, reg_b, n - i, pie, factor)
    # Compute the inverse Fourier transform of register a
    for i in range(0, n + 1):
        inverseQFT(circ, reg_a, i, pie)


# Take two numbers as user input in binary form
multiplicand_in = input("Enter the multiplicand.")
l1 = len(multiplicand_in)
multiplier_in = input("Enter the multiplier.")
l2 = len(multiplier_in)
# Make sure multiplicand_in holds the larger number
if l2 > l1:
    multiplier_in, multiplicand_in = multiplicand_in, multiplier_in
    l2, l1 = l1, l2

multiplicand = QuantumRegister(l1)
multiplier = QuantumRegister(l2)
accumulator = QuantumRegister(l1 + l2)
cl = ClassicalRegister(l1 + l2)
d = QuantumRegister(1)

circ = QuantumCircuit(accumulator, multiplier, multiplicand,
    d, cl, name="qc")

circ.x(d)
# Store bit strings in quantum registers
for i in range(l1):
    if multiplicand_in[i] == '1':
        circ.x(multiplicand[l1 - i - 1])

for i in range(l2):
    if multiplier_in[i] == '1':
        circ.x(multiplier[l2 - i - 1])

multiplier_str = '1'
# Perform repeated addition until the multiplier
# is zero
while(int(multiplier_str) != 0):
    add(accumulator, multiplicand, circ, 1)
    add(multiplier, d, circ, -1)
    for i in range(len(multiplier)):
        circ.measure(multiplier[i], cl[i])
    result = execute(circ, backend=Aer.get_backend('qasm_simulator'),
                    shots=2).result().get_counts(circ.name)
    multiplier_str = list(result.keys())[0]

circ.measure(accumulator, cl)
result = execute(circ, backend=Aer.get_backend('qasm_simulator'),
            shots=2).result().get_counts(circ.name)

print(result)
