"""
loadNormDist.py: Given a probability density function and 2^n adjacent 
intervals, discretizes the distribution over the given intervals and 
encodes it as a quantum superposition state.
"""

from qiskit import QuantumRegister, ClassicalRegister
from qiskit import Aer, execute, QuantumCircuit
from qiskit.circuit.library.standard_gates import RYGate
from numpy import pi, e, sqrt, arccos, log2
from scipy.integrate import quad
import matplotlib.pyplot as plt

# Take the distribution given by N(0, 2) discretized into 16 parts labelled 0-15
# covering [, -7], [-7, -6], [-6, -5], [-5, -4], ...., [7,]

# The region probablities are given by:
# probs = [2.3263e-04, 1.1173e-03, 4.8598e-03, 
#     0.01654046, 0.04405706, 0.09184805, 0.14988228, 0.19146246, 
#     0.19146246, 0.14988228, 0.09184805, 0.04405706, 0.01654046, 
#     4.8598e-03, 1.1173e-03, 2.3263e-04]

def distribution(x):
    """
    Returns the value of a chosen probability distribution at the given value
    of x. Mess around with this function to see how the encoder works!

    The current distribution being used is N(0, 2).
    """
    # Use these with normal distributions
    mu = 0
    sigma = 2
    return (((e ** (-0.5 * ((x - mu) / sigma) ** 2)) / (sigma * sqrt(2 * pi))) / 0.99993665)

def integrate(dist, lower, upper):
    """
    Perform integration using numpy's quad method. We can use parametrized
    distributions as well by using this syntax instead:
    quad(integrand, lower, upper, args=(tupleOfArgsForIntegrand))
    """
    return quad(dist, lower, upper)[0]


def computeRegionProbability(dist, regBounds, numRegions, j):
    """
    Given a distribution dist, a list of adjacent regions regBounds, the
    current level of discretization numRegions, a region number j, computes
    the probability that the value random variable following dist lies in
    region j given that it lies in the larger region made up of regions
    [(j // 2) * 2, ((j + 2) // 2) * 2]
    """
    totalRegions = len(regBounds) - 1
    k = 2 * j

    prob = integrate(dist, regBounds[(totalRegions // numRegions) * k],
        regBounds[(totalRegions // numRegions) * (k + 1)]) / integrate(
        dist, regBounds[(totalRegions // numRegions) * ((k // 2) * 2)],
        regBounds[(totalRegions // numRegions) * (((k + 2) // 2) * 2)])

    return prob


def getFlipList(i, j, numQubits):
    """
    Given the current level of desired level of discretization, the
    current level of discretization i and a region number j,
    returns the binary bit string associated with j in the form of
    a list of bits to be flipped.
    """
    binString = str(bin(j))[2:]
    binString = ("0" * (numQubits - len(binString))) + binString
    bitFlips = []

    for k in range(numQubits - i, numQubits):
        if binString[k] == '0':
            bitFlips.append(3 * numQubits - 3 - k - i)

    return bitFlips


def pad(x, numQubits):
    """
    Utility function that returns a left padded version of the bit string
    passed.
    """
    string = str(x)[2:]
    string = ('0' * (numQubits - len(string))) + string
    return string


def encodeDist(dist, regBounds):
    """
    Discretize the distribution dist into multiple regions with boundaries
    given by regBounds, and store the associated quantum superposition
    state in a new quantum register reg. Please make sure the number of 
    regions is a power of 2, i.e. len(regBounds) = (2 ** n) + 1.

    Additionally, the number of regions is limited to a maximum of
    2^(n // 2 + 1), where n is the number of qubits available in the backend
    being used - this is due to the requirement of (n - 2) ancilla qubits in
    order to perform (n - 1) control operations with minimal possible depth.

    Returns a new quantum circuit containing the instructions and registers
    needed to create the superposition state, along with the size of the
    quantum register.
    """
    numQubits = int(log2(len(regBounds) - 1))

    a = QuantumRegister(2 * numQubits - 2)
    c = ClassicalRegister(numQubits)
    qc = QuantumCircuit(a, c)

    for i in range(numQubits):
        numRegions = int(2 ** (i + 1))

        for j in range(numRegions // 2):
            prob = computeRegionProbability(dist, regBounds, numRegions, j)

            if not i:
                qc.ry(2 * arccos(sqrt(prob)), a[2 * numQubits - 3])
            else:
                cGate = RYGate(2 * arccos(sqrt(prob))).control(i)
                listOfFlips = getFlipList(i, j, numQubits)

                for k in listOfFlips:
                    qc.x(a[k])

                qubitsUsed = [a[k] for k in
                    range(2 * numQubits - 2 - i, 2 * numQubits - 2)]

                qubitsUsed.append(a[2 * numQubits - 3 - i])
                qc.append(cGate, qubitsUsed)

                for k in listOfFlips:
                    qc.x(a[k])

    return qc, a, c


regBounds = [i for i in range(-16, 17)]
qc, a, c = encodeDist(distribution, regBounds)
numQubits = (qc.num_qubits + 2) // 2

for i in range(numQubits - 2, 2 * numQubits - 2):
    qc.measure(a[i], c[i - (numQubits - 2)])

backend = Aer.get_backend('qasm_simulator')
shots = 100000
job = execute(qc, backend=backend, shots=shots)
results = job.result().get_counts()
resultsX = []
resultsY = []

for i in [pad(bin(x), numQubits) for x in range(2 ** (numQubits))]:
    resultsX.append(i)
    if i in results.keys():
        resultsY.append(results[i])
    else:
        resultsY.append(0)

truthDisc = [integrate(distribution, regBounds[i], regBounds[i + 1]) * shots for i in range(
    len(regBounds) - 1)]

plt.figure(figsize=[16, 9])
plt.plot(resultsX, resultsY)
plt.plot(resultsX, truthDisc, '--')
plt.show()
print(results)
