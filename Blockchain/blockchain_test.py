import json
from web3 import Web3, Account
from Blockchain_functions import *

#Testing Block

blockChain = BlockchainClass()

patient_address = "0x0000000000000000000000000000000000000000"
doctor_address =  "0x0000000000000000000000000000000000000001"

#Patient Creation
blockChain.createPatient(patient_address, "John Smith", 1998)
print("Created Patient")

#Doctor Creation
blockChain.createDoctor(doctor_address, "Bob Bobby", "Nose Doctor", 4)
print("Created Doctor")

#add authorized doctor
blockChain.addAuthorizedDoctor(patient_address, doctor_address)
print("added authorized doctor")

#test remove later first test things that rely on doctor having permissions

hash_ = "testHash"
pointer = "testPointer"
#upload record
results = blockChain.uploadRecord(patient_address, doctor_address, hash_, pointer)
print("First upload: ", results)

#get medical records as patient
blockChain.patientHashPointer(patient_address)
print("Patient queried database succesfully")

#get medical records as doctor
blockChain.doctorHashPointer(patient_address, doctor_address)
print("Doctor queried database succesfully")

#remove authorized doctor
blockChain.removeAuthorizedDoctor(patient_address, doctor_address)
print("Removed doctor")

#test upload record while not having permissions
hash_ = "testHash2"
pointer = "testPointer2"

results = blockChain.uploadRecord(patient_address, doctor_address, hash_, pointer)
print("Second upload: ", results)
