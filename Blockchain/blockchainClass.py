import json
from web3 import Web3, Account

#----------------------------------------------------------------------------------------------------

#Create Doctor/Patient


class BlockchainClass():

  def __init__(self):

    #contract_abi = json.load(open("Blockchain/abi.json"))
    contract_abi = json.load(open("abi.json"))

    #infura key
    infura_url = "https://sepolia.infura.io/v3/7be17999d53e49ba8a3f5e2776d1dff0"

    self.web3 = Web3(Web3.HTTPProvider(infura_url))

    if not self.web3.is_connected():
        raise ValueError("Failed to connect to Ethereum node")

    #probably should make this an environmental variable and access it that way
    self.private_key = '82fdebc4ee42ffd17391232d1cabc7092d50b85226549bd1d48cdb52d6f3e31f'
    account=Account.from_key(self.private_key) 
    self.address = account.address

    #same here environmental variable
    contract_address = "0x53b982Ee7ba21D357307CA4154Edb9C3d745886f"
    
    self.contract = self.web3.eth.contract(address=contract_address, abi=contract_abi)
    



  def createPatient(self, patientAddress, patientName, patientBirthYear):

    Chain_id = self.web3.eth.chain_id

    nonce = self.web3.eth.get_transaction_count(self.address)

    # Build the transaction to call the function
    transaction = self.contract.functions.addPatient(patientAddress, patientName, patientBirthYear).build_transaction({
        'from': self.address,
        'chainId': Chain_id,
        'nonce': nonce,  
    })

    # Sign the transaction
    signed_transaction = self.web3.eth.account.sign_transaction(transaction, self.private_key)  

    # Send the transaction
    tx_hash = self.web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    # Wait for the transaction to be mined
    tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)


  def createDoctor(self, doctorAddress, doctorName, doctorSpecialty, doctorRating):

    Chain_id = self.web3.eth.chain_id

    nonce = self.web3.eth.get_transaction_count(self.address)

    # Build the transaction to call the function
    transaction = self.contract.functions.addDoctor(doctorAddress, doctorName, doctorSpecialty, doctorRating).build_transaction({
        'from': self.address,
        'chainId': Chain_id,
        'nonce': nonce,  
    })

    # Sign the transaction
    signed_transaction = self.web3.eth.account.sign_transaction(transaction, self.private_key)  

    # Send the transaction
    tx_hash = self.web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    # Wait for the transaction to be mined
    tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)


  #----------------------------------------------------------------------------------------------------

  #Patient adds/remove doctor to his list of allowed doctors

  #Patient adds doctor to his list of allowed doctors
  #happens when the patient does something on the UI (not sure how that looks)
  def addAuthorizedDoctor(self, patientAddress, doctorAddress):

    Chain_id = self.web3.eth.chain_id

    nonce = self.web3.eth.get_transaction_count(self.address)

    # Build the transaction to call the function
    transaction = self.contract.functions.authorizeDoctor(patientAddress, doctorAddress).build_transaction({
        'from': self.address,
        'chainId': Chain_id,
        'nonce': nonce,  
    })

    # Sign the transaction
    signed_transaction = self.web3.eth.account.sign_transaction(transaction, self.private_key)  

    # Send the transaction
    tx_hash = self.web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    # Wait for the transaction to be mined
    tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)


  #Patient removes doctor to his list of allowed doctors
  #happens when the patient does something on the UI (not sure how that looks)
  def removeAuthorizedDoctor(self, patientAddress, doctorAddress):
    
    Chain_id = self.web3.eth.chain_id

    nonce = self.web3.eth.get_transaction_count(self.address)

    # Build the transaction to call the function
    transaction = self.contract.functions.revokeDoctor(patientAddress, doctorAddress).build_transaction({
        'from': self.address,
        'chainId': Chain_id,
        'nonce': nonce,  
    })

    # Sign the transaction
    signed_transaction = self.web3.eth.account.sign_transaction(transaction, self.private_key)  

    # Send the transaction
    tx_hash = self.web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    # Wait for the transaction to be mined
    tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

    

  #----------------------------------------------------------------------------------------------------

  #Doctor upload/edit medical record

  #uploads the patient medical record to the database
  #doctor uploads a FHIR or CSV file (tbd) through the UI
  def uploadRecord(self, patientAddress, doctorAddress, hash_, record):

    if(self.contract.functions.doctorCheckPermissions(patientAddress, doctorAddress).call()):
      
      Chain_id = self.web3.eth.chain_id

      nonce = self.web3.eth.get_transaction_count(self.address)

      # Build the transaction to call the function
      transaction = self.contract.functions.setPatientHashPointer(patientAddress, hash_, pointer).build_transaction({
          'from': self.address,
          'chainId': Chain_id,
          'nonce': nonce,  
      })

      # Sign the transaction
      signed_transaction = self.web3.eth.account.sign_transaction(transaction, self.private_key)  

      # Send the transaction
      tx_hash = self.web3.eth.send_raw_transaction(signed_transaction.rawTransaction)

      # Wait for the transaction to be mined
      tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)

    else:
      return -1
    
    return 1

  #----------------------------------------------------------------------------------------------------

  #Database Query Functions

  #function for patient to get the pointer to the database and the hash of the MR
  #returns medical record or error
  def patientHashPointer(self, patientAddress):
    
    #get hash and pointer from smart contract
    pointer = self.contract.functions.returnPointer(patientAddress).call()
    hash_ = self.contract.functions.returnHash(patientAddress).call()

    #else return -1, somehandling client side will be needed to show an error message if this -1 is returned
    return -1 


  #funtion for doctor to get the hash of the medical record and the pointer to the medical record
  #returns the patient's medical record or an error
  #returns -1 for pointer error
  #returns -2 for permission error
  def doctorHashPointer(self, patientAddress, doctorAddress):

    if(self.contract.functions.doctorCheckPermissions(patientAddress, doctorAddress).call()):

      pointer = self.contract.functions.returnPointer(patientAddress).call()
      hash_ = self.contract.functions.returnHash(patientAddress).call()

      print("pointer", pointer)
      print("hash", hash_)

      if pointer != None:
        return pointer, hash_

      return -1
    
    #else return no permission error or -2
    return -2

  #----------------------------------------------------------------------------------------------------
