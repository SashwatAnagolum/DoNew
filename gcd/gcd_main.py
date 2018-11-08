# -*- coding: utf-8 -*-

"""
gcd_main.py: Finds the greatest common divisor of two given numbers.
"""

import math
from qiskit import ClassicalRegister, QuantumRegister, QuantumCircuit
from qiskit import execute
from qiskit import CompositeGate
from qiskit import available_backends, get_backend
import subtract

def isEven(qc, reg, reg2, anc, anc_cl):
    """
    Applies a bit flip on the first qubit of QuantumRegister anc conditioned
    on the qubits of QuantumRegister reg. The value of anc is then stored in 
    the ClassicalRegister anc_cl, and then anc is reset to the |00> state.
    Parameters:
    qc: QuantumCircuit
    reg, reg2, anc: QuantumRegisters
    anc_cl: ClassicalRegister
    Returns:
    None
    """
    qc.cx(reg[0], anc[0])
    qc.cx(reg2[0], anc[1])
    qc.measure(anc, anc_cl)
    #Reset reg to its intial state for later use
    qc.cx(reg[0], anc[0])
    qc.cx(reg2[0], anc[1])

def divideBy2(cgate, n, circ, reg, anc_cl, num, anc, a_cl): 
    """
    Adds instructions that shift the qubits of QuantumRegister reg 
    rightwards to CompositeGate cgate controlled by the value stored in
    ClassicalRegister anc_cl, and then sets the leftmost bit of reg to
    the |0> state by swapping qubits with the first qubit of QuantumRegister
    anc. Finally, the first qubit of anc is set to |0> again.
    Parameters:
    cgate: CompositeGate
    circ: QuantumCircuit
    reg, anc: QuantumRegister
    anc_cl, a_cl: ClassicalRegister
    n, num: integers   
    Returns:
    cgate: CompositeGate   
    """   
    #Perform a rightwards swap
    for i in range(n-1):
        cgate._attach(circ.swap(reg[i], reg[i + 1]).
            c_if(anc_cl, num))
    #Ensure the rightmost qubit is in the |0> state
    cgate._attach(circ.swap(reg[n-1], anc[0]).c_if(anc_cl, num))
    cgate._attach(circ.measure(anc[0], a_cl[0]).c_if(anc_cl, num))
    cgate._attach(circ.cx(anc[0],anc[1]).c_if(anc_cl, num))
    cgate._attach(circ.x(anc).c_if(a_cl, 1))
    cgate._attach(circ.measure(anc[0], a_cl[0]).c_if(anc_cl, num))
    return cgate

def multiplyBy2(cgate, n, circ, reg, anc_cl, num):
    """
    Adds instructions that shift the qubits of QuantumRegister reg leftwards
    to CompositeGate cgate controlled by the value stored in ClassicalRegister
    anc_cl.
    Parameters:
    cgate: CompositeGate
    circ: QuantumCircuit
    reg: QuantumRegister
    anc_cl: ClassicalRegister
    n, num: integers
    Returns:
    cgate: CompositeGate     
    """
    #Perform a leftwards swap    
    for i in range(n-1):
        cgate._attach(circ.swap(reg[n-(i+2)], reg[n-(i + 1)]).
            c_if(anc_cl, num))
    return cgate     

def createCG(circ, args, anc_cl, n, num, anc, a_cl, \
    reg, reg2 = None, reg3 = None):   
    """
    Creates a CompositeGate cgate with a series of instructions controlled
    by ClassicalRegister anc_cl holding the value num. 
    Parameters:
    circ: QuantumCircuit
    args: List containing (Register, index) pairs that the CompositeGate
          will affect.
    reg, reg2, reg3, anc: QuantumRegisters
    anc_cl, a_cl: ClassicalRegisters
    n, num: integers
    pie: float representing pi (3.14..)
    Returns:
    cgate: CompositeGate     
    """
    cgate = CompositeGate("cl_" + str(num), [], args, circuit = circ)
    cgate = divideBy2(cgate, n, circ, reg, anc_cl, num, anc, a_cl)
    if num == 0:
        cgate = divideBy2(cgate, n, circ, reg2, anc_cl, num, anc, a_cl)    
        cgate = multiplyBy2(cgate, n, circ, reg3, anc_cl, num)
    return cgate

def createCG3(circ, args, anc_cl, n, reg, reg2, pie, anc, a_cl):
    """
    Creates a CompositeGate cgate with a series of instructions controlled
    by ClassicalRegister anc_cl holding the value 3. 
    Parameters:
    circ: QuantumCircuit
    args: List containing (Register, index) pairs that the CompositeGate
          will affect.
    reg, reg2, anc: QuantumRegisters
    anc_cl, a_cl: ClassicalRegisters
    n: integer
    pie: float representing pi (3.14..)
    Returns:
    cgate: CompositeGate     
    """    
    cgate = CompositeGate("cl_" + str(3), [pie], args,
     circuit = circ)
    #Compute (reg - reg2)/2
    cgate = subtract.subtract(circ, n, pie, reg, reg2
        , cgate, -1, anc_cl, 3)
    cgate = divideBy2(cgate, n, circ, reg, anc_cl, 3, anc, a_cl)
    return cgate

def gcd(qc, a, b, res, anc, zero, zero_cl, anc_cl, cl, n, a_cl, b_cl):
    """
    Computes the GCD of two numbers stored in QuantumRegisters a and b.
    Parameters:
    qc: QuantumCircuit
    a: QuantumRegister holding the first number
    b: QuantumRegister holding the second number
    res: QuantumRegister holding the multiplication factor for the GCD
    anc: QuantumRegister used as an ancillary register
    zero: QuantumRegister used as an ancillary register      
    zero_cl, anc_cl, cl, a_cl, b_cl: ClassicalRegisters
    n: integer
    Returns:
    counts: List
    """ 
    ab = [a[x] for x in range(n)] + [b[x] for x in range(n)]

    isEven(qc, a, b, anc, anc_cl)
    #Create a CompositeGate for each possible value of anc_cl
    #(0, 1, 2, 3)
    cl0 = createCG(qc, ab, anc_cl, n, 0, anc, a_cl, a, b, res)
    cl1 = createCG(qc, ab, anc_cl, n, 1, anc, a_cl, b)
    cl2 = createCG(qc, ab, anc_cl, n, 2, anc, a_cl, a)
    cl3 = createCG3(qc, ab, anc_cl, n, a, b, math.pi, anc, a_cl)
    #Measure qubits
    qc.measure(zero, anc_cl) 
    qc.measure(res, cl)
    qc.measure(a, a_cl)
    qc.measure(b, b_cl)
    #Select backedn and run job
    result = execute(qc, backend='ibmq_qasm_simulator', 
                      shots=256).result()

    counts = result.get_counts("qc")
    counts = [i.split() for i in counts.keys()]
    return counts[0][0], counts[0][1], counts[0][2], \
     counts[0][3], counts[0][4]