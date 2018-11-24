# -*- coding: utf-8 -*-

"""
div_main.py: Driver script for the quantum integer division algorithm 
using the Quantum Fourier Transform. 
"""

from qforest_matherror import QForestMathError, ZeroError
import add
import subtract


def divide(dividend, divisor, accumulator,
           c_dividend, circ, cl_index):
    """
    Divide QuantumRegister dividend by QuantumRegister divisor, and store the
    product in QuantumRegister accumulator.

    """
    try:
        from qiskit import QuantumRegister, ClassicalRegister, \
            QuantumCircuit
        from qiskit import Aer, execute
    except ImportError:
        install = """Please install qiskit! You can install it using the 
                     pip tool: pip install qiskit."""
        raise QForestMathError(install)

    if isinstance(divisor, QuantumRegister) and \
            isinstance(dividend, QuantumRegister) and \
            isinstance(accumulator, QuantumRegister) and \
            isinstance(c_dividend, ClassicalRegister) and \
            isinstance(cl_index, int) and \
            isinstance(circ, QuantumCircuit):
        pass
    else:
        raise QForestMathError("Expected three QuantumRegister" +
                               " objects, one ClassicalRegister object, one " +
                               "QuantumCircuit object and an integer! Please check the objects passed" +
                               " to the multiply() function.")

    d = QuantumRegister(1)
    circ.add(d)
    circ.x(d[0])

    c_dividend_str = '0'

    while c_dividend_str[0] == '0':
        subtract.subtract(dividend, divisor, circ)
        add.add(accumulator, d, circ)
        for i in range(len(dividend)):
            circ.measure(dividend[i], c_dividend[i])
        result = execute(circ, backend=Aer.get_backend('qasm_simulator'),
                         shots=2).result()
        counts = result.get_counts("qc")
        c_dividend_str = list(counts.keys())[0].split()[cl_index]

    subtract.subtract(accumulator, d, circ)
