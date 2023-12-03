import json
from web3 import Web3, Account
from Blockchain_functions import *

#web3 setup

#load json file
contract_abi = json.load(open("Blockchain/abi.json"))

#infura key
infura_url = "https://sepolia.infura.io/v3/7be17999d53e49ba8a3f5e2776d1dff0"
w3 = Web3(Web3.HTTPProvider(infura_url))

if not w3.is_connected():
    raise ValueError("Failed to connect to Ethereum node")

#probably should make this an environmental variable and access it that way
private_key = '82fdebc4ee42ffd17391232d1cabc7092d50b85226549bd1d48cdb52d6f3e31f'
account=Account.from_key(private_key) 
print(account.address)

#same here environmental variable
contract_address = "0xc9a62f6D80E64C913E20D08d14bBD9facE211128"
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

#----------------------------------------------------------------------------------------------------

#Testing Block


#Patient Creation
createPatient(contract, account.address, private_key, account.address, "John Smith", 1998)
print("Created Patient")

#Doctor Creation
createDoctor(contract, account.address, private_key, account.address, "Bob Bobby", "Nose Doctor", 4)
print("Created Doctor")

#add authorized doctor
addAuthorizedDoctor(contract, account.address, private_key, account.address, account.address)
print("added authorized doctor")

#test remove later first test things that rely on doctor having permissions

#upload record
results = uploadRecord(contract, account.address, private_key, account.address, account.address, "record")
print("First upload: ", results)

#get medical records as patient
patientDatabaseQuery(contract, account.address)
print("Patient queried database succesfully")

#get medical records as doctor
doctorDatabaseQuery(contract, account.address, account.address)
print("Doctor queried database succesfully")

#remove authorized doctor
removeAuthorizedDoctor(contract, account.address, private_key, account.address, account.address)
print("Removed doctor")

#test upload record while not having permissions
results = uploadRecord(contract, account.address, private_key, account.address, account.address, "record")
print("Second upload: ", results)
