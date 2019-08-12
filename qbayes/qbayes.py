"""
qbayes.py: implements a simple bayesian network on a quantum computer and performs quantum rejection
sampling.
"""

from qiskit import QuantumRegister, ClassicalRegister 
from qiskit import QuantumCircuit, Aer
from qiskit import execute
from math import pi

from numpy import arcsin, sqrt

def probToAngle(prob):
    """
    Converts a given P(1) value into an equivalent theta value.
    """
    return 2*arcsin(sqrt(prob))


def oracle(circ):
    """
    Implements an oracle that flips the sign of states that contain P = 1.
    """
    circ.cu3(pi, pi, 0, net[0], net[1])
    circ.cu3(pi, pi, 0, net[0], net[1])    
    return circ


def u_gate(circ):
    """
    Implements the U gate that flips states about the average amplitude.
    """
    # Implements the quantum circuit that converts ψ -> |000...0>
    circ.u3(-1*probToAngle(0.35), 0, 0, net[0])
    circ.u3(-1*probToAngle(0.76), 0, 0, net[1])
    circ.u3(-1*probToAngle(0.39), 0, 0, net[2])

    # Flipping the |000...0> state using a triple controlled Z gate condtioned on P, E and H, 
    # and applied to the ancilla
    circ.x(net)
    circ.cu1(pi/4, net[0], net[3])
    circ.cx(net[0], net[1])
    circ.cu1(-pi/4, net[1], net[3])
    circ.cx(net[0], net[1])
    circ.cu1(pi/4, net[1], net[3])
    circ.cx(net[1], net[2])
    circ.cu1(-pi/4, net[2], net[3])
    circ.cx(net[0], net[2])
    circ.cu1(pi/4, net[2], net[3])
    circ.cx(net[1], net[2])
    circ.cu1(-pi/4, net[2], net[3])
    circ.cx(net[0], net[2])
    circ.cu1(pi/4, net[2], net[3])
    circ.x(net)

    # Implements the quantum circuit that converts |000...0> -> ψ 
    circ.u3(probToAngle(0.35), 0, 0, net[0])
    circ.u3(probToAngle(0.76), 0, 0, net[1])
    circ.u3(probToAngle(0.39), 0, 0, net[2])

    return circ


# Create one 4 qubit QuantumRegister to hold the Bayesian network and an ancilla qubit,
# and a 3 bit ClassicalRegister to hold the sampled values
net = QuantumRegister(4, 'qreg')
cl = ClassicalRegister(3, 'creg')

circ = QuantumCircuit(net, cl, name='circ')

# Setting up a qubit to represent the variable P
circ.u3(probToAngle(0.35), 0, 0, net[0])

# Since we have P = 1, we use the second row of the probability table for the variable E
circ.u3(probToAngle(0.76), 0, 0, net[1])

# Setting up the qubit representing H assuming that E = 0
circ.u3(probToAngle(0.39), 0, 0, net[2])

# Apply oracle and U gate twice
circ = oracle(circ)
circ = u_gate(circ)
circ = oracle(circ)
circ = u_gate(circ)
circ.x(net[0])

# Measure E, and rotate H to the P(1) value in the second row of the P(H|E) table condtioned on E
circ.measure(net[1], cl[1])
circ.u3(probToAngle(0.82) - probToAngle(0.39), 0, 0, net[2]).c_if(cl, 2)

# Sample by measuring the rest of the qubits
circ.measure(net[0], cl[0])
circ.measure(net[2], cl[2])

# Get backend from Aer provider
backend = Aer.get_backend('qasm_simulator')

# Run job many times to get multiple samples
samples_list = []
n_samples = 500

for i in range(n_samples):
    job = execute(circ, backend=backend, shots=1)
    result = list(job.result().get_counts(circ).keys())[0]
    if result[2] == '1':
        samples_list.append(result)

# Printing the number of useful samples and percentage of samples rejected
print()
print(n_samples, 'samples drawn:', len(samples_list), 'samples accepted,', n_samples-len(samples_list), 'samples rejected.' )
print('Percentage of samples accepted: ', 100*((len(samples_list)/n_samples)), '%')

# Computing P(H = 0| P = 1)
p_H = 0

for i in samples_list:
    if i[0] == '0':
        p_H += 1

p_H /= len(samples_list)

print('P(H = 0| P = 1) =', p_H)
print()
