# QForestMath

A small wrapper for basic arithmetic operations using QISkit.

## Installation

Install QForestMath using pip, the python package management tool:
pip install QForestMath

### Prerequisites

Please ensure that you have qiskit installed before you try to run any
programs using QForestMath, as all functionality involves the use of
various qiskit modules such as QuantumRegister, ClassicalRegister, and CompostiteGate.

## Getting Started

Functions:

add.add(addend, addend, circ)

subtract.subtract(minuend, subtrahend, circ)

multiply.multiply(multiplicand, multiplier, accumulator, ancillary, 	circ, anc_index)

divide.divide(dividend, divisor, accumulator, ancillary, circ, anc_index)

## Description

QForestMath abstracts the process of constructing quantum circuits for
elementary arithmetic operations by substituting them with function calls. 

Every function in the library is meant to be used as a smaller part of a larger quantum circuit, and hence does not return any values, but simply adds an appropriate gate sequence to the QuantumCircuit object's QASM string.

The addition and subtraction functions are implemented using the quantum Fourier transform, and the multiplication and division functions are implemented using repeated addition and subtraction, repsectively. The GCD function uses a combination of these operations to acheive the equivalent result.

## Authors

Akash Rao
Mohit Gaggar
Sashwat Anagolum

## License

This project is licensed under the MIT License.






