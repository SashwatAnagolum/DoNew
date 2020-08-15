"""
qnn.py: a small quantum neural network that acts as a binary
classifier.
"""

from qiskit import QuantumRegister, ClassicalRegister
from qiskit import Aer, execute, QuantumCircuit
from qiskit.extensions import UnitaryGate
import numpy as np


def convertDataToAngles(data):
    prob1 = data[2] ** 2 + data[3] ** 2
    prob0 = 1 - prob1
    angle1 = 2 * np.arcsin(np.sqrt(prob1))
    prob1 = data[3] ** 2 / prob1
    angle2 = 2 * np.arcsin(np.sqrt(prob1))
    prob1 = data[1] ** 2 / prob0
    angle3 = 2 * np.arcsin(np.sqrt(prob1))
    return np.array([angle1, angle2, angle3])


def encodeData(qc, qreg, angles):
    qc.ry(angles[0], qreg[1])
    qc.cry(angles[1], qreg[1], qreg[0])
    qc.x(qreg[1])
    qc.cry(angles[2], qreg[1], qreg[0])
    qc.x(qreg[1])


def GGate(qc, qreg, params):
    u00 = np.exp((0 + 1j) * params[1]) * np.cos(params[0])
    u01 = np.exp((0 + 1j) * params[2]) * np.sin(params[0])
    u10 = np.exp((0 + 1j) * -params[2]) * -np.sin(params[0])
    u11 = np.exp((0 + 1j) * -params[1]) * np.cos(params[0])
    gateLabel = "G({},{}, {})".format(
        params[0], params[1], params[2]
    )
    GGate = UnitaryGate(np.array(
        [[u00, u01], [u10, u11]]
    ), label=gateLabel)
    return GGate


def GLayer(qc, qreg, params):
    for i in range(2):
        qc.append(GGate(qc, qreg, params[i]), [qreg[i]])


def CGLayer(qc, qreg, anc, params):
    for i in range(2):
        qc.append(GGate(
            qc, qreg, params[i]
        ).control(1), [anc[0], qreg[i]])


def CXLayer(qc, qreg, order):
    if order:
        qc.cx(qreg[0], qreg[1])
    else:
        qc.cx(qreg[1], qreg[0])


def CCXLayer(qc, qreg, anc, order):
    if order:
        qc.ccx(anc[0], qreg[0], qreg[1])
    else:
        qc.ccx(anc[0], qreg[1], qreg[0])


def generateU(qc, qreg, params):
    for i in range(params.shape[0]):
        GLayer(qc, qreg, params[i])
        CXLayer(qc, qreg, i % 2)


def generateCU(qc, qreg, anc, params):
    for i in range(params.shape[0]):
        CGLayer(qc, qreg, anc, params[i])
        CCXLayer(qc, qreg, anc, i % 2)


def getPrediction(qc, qreg, creg, backend):
    qc.measure(qreg[0], creg[0])
    job = execute(qc, backend=backend, shots=100000)
    results = job.result().get_counts()
    if '1' in results.keys():
        return results['1'] / 100000
    else:
        return 0


def convertToClass(predictions):
    return (predictions >= 0.5) * 1


def cost(labels, predictions):
    loss = 0
    for label, pred in zip(labels, predictions):
        loss += (pred - label) ** 2

    return loss / 2


def accuracy(labels, predictions):
    acc = 0
    for label, pred in zip(labels, predictions):
        if label == pred:
            acc += 1

    return acc / labels.shape[0]


def forwardPass(params, bias, angles, backend):
    qreg = QuantumRegister(2)
    anc = QuantumRegister(1)
    creg = ClassicalRegister(1)
    qc = QuantumCircuit(qreg, anc, creg)
    encodeData(qc, qreg, angles)
    generateU(qc, qreg, params)
    pred = getPrediction(qc, qreg, creg, backend) + bias
    return pred


def computeRealExpectation(params1, params2, angles, backend):
    qreg = QuantumRegister(2)
    anc = QuantumRegister(1)
    creg = ClassicalRegister(1)
    qc = QuantumCircuit(qreg, anc, creg)
    encodeData(qc, qreg, angles)
    qc.h(anc[0])
    generateCU(qc, qreg, anc, params1)
    qc.cz(anc[0], qreg[0])
    qc.x(anc[0])
    generateCU(qc, qreg, anc, params2)
    qc.x(anc[0])
    qc.h(anc[0])
    prob = getPrediction(qc, anc, creg, backend)
    return 2 * (prob - 0.5)


def computeGradient(params, angles, label, bias, backend):
    prob = forwardPass(params, bias, angles, backend)
    gradients = np.zeros_like(params)
    for i in range(params.shape[0]):
        for j in range(params.shape[1]):
            newParams = np.copy(params)
            newParams[i, j, 0] += np.pi / 2
            gradients[i, j, 0] = computeRealExpectation(
                params, newParams, angles, backend
            )
            newParams[i, j, 0] -= np.pi / 2
            newParams[i, j, 2] = 0
            newParams[i, j, 1] += np.pi / 2
            prob1 = computeRealExpectation(
                params, newParams, angles, backend
            )
            newParams[i, j, 2] = np.pi
            prob2 = computeRealExpectation(
                params, newParams, angles, backend
            )
            gradients[i, j, 1] = 0.5 * (prob1 + prob2)
            newParams[i, j, 2] = params[i, j, 2] + np.pi / 2
            newParams[i, j, 1] = 0
            prob1 = computeRealExpectation(
                params, newParams, angles, backend
            )
            newParams[i, j, 1] = np.pi
            prob2 = computeRealExpectation(
                params, newParams, angles, backend
            )
            gradients[i, j, 2] = 0.5 * (prob1 + prob2)
    biasGrad = (prob + bias - label)
    return gradients * biasGrad, biasGrad


def updateParams(params, prevParams, grads, learningRate, momentum):
    delta = params - prevParams
    paramsNew = np.copy(params)
    paramsNew = params - grads * learningRate + momentum * delta
    return paramsNew, params


def trainNetwork(data, labels, backend):
    np.random.seed(0)
    numSamples = labels.shape[0]
    numTrain = int(numSamples * 0.75)
    ordering = np.random.permutation(range(numSamples))
    trainingData = data[ordering[:numTrain]]
    validationData = data[ordering[numTrain:]]
    trainingLabels = labels[ordering[:numTrain]]
    validationLabels = labels[ordering[numTrain:]]
    params = np.sqrt(np.random.sample((5, 2, 3)))

    bias = 0.01
    prevParams = np.copy(params)
    prevBias = bias
    batchSize = 5
    momentum = 0.9
    learningRate = 0.02
    for iteration in range(15):
        samplePos = iteration * batchSize
        batchTrainingData = trainingData[samplePos:samplePos + 5]
        batchLabels = trainingLabels[samplePos:samplePos + 5]
        batchGrads = np.zeros_like(params)
        batchBiasGrad = 0
        for i in range(batchSize):
            # probPass=forwardPass(params, bias, batchTrainingData[i], backend)
            grads, biasGrad = computeGradient(
                params, batchTrainingData[i], batchLabels[i], bias, backend
            )
            batchGrads += grads / batchSize
            batchBiasGrad += biasGrad / batchSize

        params, prevParams = updateParams(
            params, prevParams, batchGrads, learningRate, momentum
        )

        temp = bias
        bias += -learningRate * batchBiasGrad + momentum * (bias - prevBias)
        prevBias = temp

        trainingPreds = np.array([forwardPass(
            params, bias, angles, backend
        )for angles in trainingData])
        print('Iteration {} | Loss: {}'.format(
            iteration + 1, cost(trainingLabels, trainingPreds)
        ))

    validationProbs = np.array(
        [forwardPass(
            params, bias, angles, backend
        ) for angles in validationData]
    )
    validationClasses = convertToClass(validationProbs)
    validationAcc = accuracy(validationLabels, validationClasses)
    print('After {} iterations:'.format(iteration + 1))
    print('Validation accuracy:', validationAcc)
    for x, y, p in zip(validationData, validationLabels, validationClasses):
        print('Data:', x, ' | Class:', y, ' | Prediction:', p)


data = np.genfromtxt("processedIRISData.csv", delimiter=",")
X = data[:, 0:4]
features = np.array([convertDataToAngles(i) for i in X])
Y = data[:, -1]
backend = Aer.get_backend('qasm_simulator')
trainNetwork(features, Y, backend)