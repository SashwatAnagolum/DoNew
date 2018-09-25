#!/usr/bin/env python
#Add two numbers using quantum logic gates with the IBM QISkit and the QASM simulator

from qiskit import ClassicalRegister, QuantumRegister
from qiskit import QuantumCircuit
from qiskit import execute
from qiskit import register, available_backends, get_backend

def main():
    count = -1 #Used to trigger exit from loop only when both inputs are valid
    while count == -1:
        first = input("Enter a binary number with less than 8 digits")
        second = input("Enter another binary number with less than 8 digits")
        l = len(first)
        l2 = len(second)
        #Checking if the length of either number is more than 8 digits
        if l > 8 or l2 > 8:
            print("Please enter valid inputs. Try again.")
        else:
            count = 0
    #Finding out which number is larger and assign that length to variable n
    if l > l2:
         n = l
    else:
         n = l2
    #Initialising the registers; two quantum registers with n bits each
    #1 more with n+1 bits, which will also hold the sum of the two numbers
    #The classical register has n+1 bits, which is used to make the sum readable
    a = QuantumRegister(n)
    b = QuantumRegister(n+1)
    c = QuantumRegister(n)
    cl = ClassicalRegister(n+1)
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
    #Implementing a carry gate that is applied on all (c[i], a[i], b[i]) with 
    #output fed to c[i+1]
    for i in range(n-1):
        qc.ccx(a[i], b[i], c[i+1])
        qc.cx(a[i], b[i])
        qc.ccx(c[i], b[i], c[i+1])
    #For the last iteration of the carry gate, instead of feeding the result to
    #c[n], we use b[n], which is why c has only n bits, with c[n-1] being the last carry bit
    qc.ccx(a[n-1], b[n-1], b[n])
    qc.cx(a[n-1], b[n-1])
    qc.ccx(c[n-1], b[n-1], b[n])
    #Reversing the gate operation performed on b[n-1]
    qc.cx(c[n-1], b[n-1])
    #Reversing the gate operations performed during the carry gate implementations
    #This is done to ensure the sum gates are fed with the correct input bit states
    for i in range(n-1):
        qc.ccx(c[(n-2)-i], b[(n-2)-i], c[(n-1)-i])
        qc.cx(a[(n-2)-i], b[(n-2)-i])
        qc.ccx(a[(n-2)-i], b[(n-2)-i], c[(n-1)-i])
        #These two operations act as a sum gate; if a control bit is at the 1> state
        #then the target bit b[(n-2)-i] is flipped
        qc.cx(c[(n-2)-i], b[(n-2)-i])
        qc.cx(a[(n-2)-i], b[(n-2)-i])

    #Measure qubits, which forces them to revert to one of two possible states: |0> or |1>
    #Since no superposition was created, all qubits are already in the |0> or |1> state
    #So this effectively transfers the qubit states to the classical register
    for i in range(n+1):
        qc.measure(b[i], cl[i])

    #Import configuration and set API token and url
    try:
        import sys
        sys.path.append("../")
        import Qconfig 
        qx_config = {
            "APItoken": Qconfig.APItoken,
            "url": Qconfig.config['url']
        }
    except Exception as e:
        print(e)
        qx_config = {
            "APItoken": """be05aaea2eb2249e3dced60ccaa6c4104d11e55a35ac64b66f96578e787ba650294857f41ca2c70f34fba9f78fb5fa7e994c7525a3842eb0b74f9a277ee7a6e4""", #Setting API token manually
            "url": "https://quantumexperience.ng.bluemix.net/api"
        }
    register(qx_config['APItoken'], qx_config['url'])

    #Set chosen backend and execute job
    num_shots = 2 #Setting the number of times to repeat measurement
    selected_backend = "local_qasm_simulator"
    job = execute(qc, selected_backend, shots=num_shots)
    #Get results of program
    job_stats = job.result().get_counts()
    print(type(job_stats))   

main()