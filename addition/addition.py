# -*- coding: utf-8 -*-

"""
addition.py: Addition on a quantum computer based on the
             ripple-carry method.
"""
from qiskit import ClassicalRegister, QuantumRegister
from qiskit import QuantumCircuit
from qiskit import execute
from qiskit import register, Aer

def main():
    count = -1 #Used to trigger exit from loop only when both inputs are valid
    while count == -1:
        first = input("Enter a binary number")
        second = input("Enter another binary number")
        l = len(first)
        l2 = len(second)
        #Checking if the length of either number is more than 8 digits
        if l > 8 or l2 > 8:
            print("Please enter valid inputs. Try again.")
        else:
            count = 0
    #Finding out which number is larger and assigning
    #that length to the variable n
    if l > l2:
         n = l
    else:
         n = l2
    #Initialising the registers; two quantum registers with n bits each
    #1 more with n+1 bits, which will also hold the sum of the two numbers
    #The classical register has n+1 bits, which is used to output the  
    #final sum
    a = QuantumRegister(n) #First number
    b = QuantumRegister(n+1) #Second number and sum
    c = QuantumRegister(n) #Carry bits
    cl = ClassicalRegister(n+1) #Final output
    #Combining all of them into one quantum circuit
    qc = QuantumCircuit(a, b, c, cl)
    #Setting up the registers a and b to hold the values inputted 
    counter = 0
    for i in first:
        if i == "1":
            qc.x(a[l - (counter+1)])
        counter += 1
    counter = 0
    for i in second:
        if i == "1":
            qc.x(b[l2 - (counter+1)])
        counter += 1
    #Implementing a carry gate that is applied on all (c[i], a[i], b[i]) 
    #with output fed to c[i+1]
    for i in range(n-1):
        qc.ccx(a[i], b[i], c[i+1])
        qc.cx(a[i], b[i])
        qc.ccx(c[i], b[i], c[i+1])
    #For the last iteration of the carry gate, instead of feeding the
    #result to c[n], we use b[n], which is why c has only n bits,
    #with c[n-1] being the last carry bit
    qc.ccx(a[n-1], b[n-1], b[n])
    qc.cx(a[n-1], b[n-1])
    qc.ccx(c[n-1], b[n-1], b[n])
    #Reversing the gate operation performed on b[n-1]
    qc.cx(c[n-1], b[n-1])
    #Reversing the gate operations performed during the carry gate
    #implementations, which is done to reset all carry bits to 
    #the |0> state
    for i in range(n-1):
        qc.ccx(c[(n-2)-i], b[(n-2)-i], c[(n-1)-i])
        qc.cx(a[(n-2)-i], b[(n-2)-i])
        qc.ccx(a[(n-2)-i], b[(n-2)-i], c[(n-1)-i])
        #These two operations act as a sum gate; if a control bit is 
        #in the |1> state then the target bit b[(n-2)-i] is flipped
        qc.cx(c[(n-2)-i], b[(n-2)-i])
        qc.cx(a[(n-2)-i], b[(n-2)-i])

    #Measure qubits
    for i in range(n+1):
        qc.measure(b[i], cl[i])

    #Set chosen backend and execute job
    num_shots = 2 #Setting the number of times to repeat measurement
    job = execute(qc, backend=Aer.get_backend('qasm_simulator'), shots=num_shots)
    #Get results of program
    job_stats = job.result().get_counts()
    print(job_stats)   

main()
