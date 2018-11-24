# -*- coding: utf-8 -*-

"""
times_main.py: Multiply two numbers using repeated fourier 
               transform based addition.
"""

from qforest_matherror import QForestMathError, RegisterError
import add
import subtract


def multiply(multiplicand, multiplier, accumulator,
             c_multiplier, circ, cl_index):
    """
    Multiply two numbers stored in QuantumRegisters multiplicand and 
    multiplier using repeated fourier transform based
    addition.

    """
    try:
        from qiskit import QuantumRegister, ClassicalRegister, \
            QuantumCircuit, execute
        from qiskit import Aer
    except ImportError:
        raise QForestMathError("Please install qiskit! " +
                               "You can install it using the pip tool:" +
                               " pip install qiskit.")

    if isinstance(multiplicand, QuantumRegister) and \
            isinstance(multiplier, QuantumRegister) and \
            isinstance(accumulator, QuantumRegister) and \
            isinstance(c_multiplier, ClassicalRegister) and \
            isinstance(cl_index, int) and \
            isinstance(circ, QuantumCircuit):
        pass
    else:
        raise QForestMathError("Expected three QuantumRegister" +
                               " objects, one ClassicalRegister object, one " +
                               "QuantumCircuit object and an integer! Please check the objects passed" +
                               " to the multiply() function.")

    if len(c_multiplier) < len(multiplier):
        raise RegisterError("Expected ClassicalRegister of same" +
                            " or greater length than associated QuantumRegister!" +
                            " Passed Register objects have lengths " +
                            str(len(multiplier)) + " and " + str(len(c_multiplier)) +
                            ".")

    d = QuantumRegister(1)
    circ.add(d)
    circ.x(d[0])

    multiplier_str = '1'

    while(int(multiplier_str) != 0):
        add.add(accumulator, multiplicand, circ)
        subtract.subtract(multiplier, d, circ)
        for i in range(len(multiplier)):
            circ.measure(multiplier[i], c_multiplier[i])
        result = execute(circ, backend=Aer.get_backend('qasm_simulator'),
                         shots=2).result()
        counts = result.get_counts("qc")
        multiplier_str = list(counts.keys())[0].split()[cl_index]
