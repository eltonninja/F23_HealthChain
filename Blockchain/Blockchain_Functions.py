import json
from web3 import Web3, Account

#----------------------------------------------------------------------------------------------------

#Create Doctor/Patient

def createPatient(contract, ownerAddress, private_key, patientAddress, patientName, patientBirthYear):

  Chain_id = w3.eth.chain_id
  nonce = w3.eth.get_transaction_count(ownerAddress)

  # Build the transaction to call the function
  transaction = contract.functions.addPatient(patientAddress, patientName, patientBirthYear).build_transaction({
      'from': ownerAddress,
      'chainId': Chain_id,
      'nonce': nonce,  
  })

  # Sign the transaction
  signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)  

  # Send the transaction
  tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

  # Wait for the transaction to be mined
  tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

  #run the function
  #contract.functions.addPatient(patientAddress, patientName, patientBirthYear).call({'from': ownerAddress})


def createDoctor(contract, ownerAddress, private_key, doctorAddress, doctorName, doctorSpecialty, doctorRating):

  Chain_id = w3.eth.chain_id
  nonce = w3.eth.get_transaction_count(ownerAddress)

  # Build the transaction to call the function
  transaction = contract.functions.addDoctor(doctorAddress, doctorName, doctorSpecialty, doctorRating).build_transaction({
      'from': ownerAddress,
      'chainId': Chain_id,
      'nonce': nonce,  
  })

  # Sign the transaction
  signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)  

  # Send the transaction
  tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

  # Wait for the transaction to be mined
  tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

  #run the function
  #contract.functions.addDoctor(doctorAddress, doctorName, doctorSpecialty, doctorRating).call({'from': ownerAddress})


#----------------------------------------------------------------------------------------------------

#Patient adds/remove doctor to his list of allowed doctors

#Patient adds doctor to his list of allowed doctors
#happens when the patient does something on the UI (not sure how that looks)
def addAuthorizedDoctor(contract, ownerAddress, private_key, patientAddress, doctorAddress):
  #address is the doctor's blockchain address
  
  Chain_id = w3.eth.chain_id
  nonce = w3.eth.get_transaction_count(ownerAddress)

  # Build the transaction to call the function
  transaction = contract.functions.authorizeDoctor(patientAddress, doctorAddress).build_transaction({
      'from': ownerAddress,
      'chainId': Chain_id,
      'nonce': nonce,  
  })

  # Sign the transaction
  signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)  

  # Send the transaction
  tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

  # Wait for the transaction to be mined
  tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

  #run the function
  #contract.functions.authorizeDoctor(patientAddress, doctorAddress).call({'from': ownerAddress})


#Patient removes doctor to his list of allowed doctors
#happens when the patient does something on the UI (not sure how that looks)
def removeAuthorizedDoctor(contract, ownerAddress, private_key, patientAddress, doctorAddress):
  #address is the doctor's blockchain address
  
  Chain_id = w3.eth.chain_id
  nonce = w3.eth.get_transaction_count(ownerAddress)

  # Build the transaction to call the function
  transaction = contract.functions.revokeDoctor(patientAddress, doctorAddress).build_transaction({
      'from': ownerAddress,
      'chainId': Chain_id,
      'nonce': nonce,  
  })

  # Sign the transaction
  signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)  

  # Send the transaction
  tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

  # Wait for the transaction to be mined
  tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

  #run the function
  #contract.functions.revokeDoctor(patientAddress, doctorAddress).call({'from': ownerAddress})
  

#----------------------------------------------------------------------------------------------------

#Doctor upload/edit medical record

#uploads the patient medical record to the database
#doctor uploads a FHIR or CSV file (tbd) through the UI
def uploadRecord(contract, ownerAddress, private_key, patientAddress, doctorAddress, record):

  if(contract.functions.doctorCheckPermissions(patientAddress, doctorAddress).call()):
    #TODO: Maybe some preprocessing idk

    #TODO: add the medical record to the database 
    #TODO: hash the record 

    #hard coded values for testing replace this with appropriate values
    hash = "IhaveNoInspiration"
    pointer = "part2"

    Chain_id = w3.eth.chain_id
    nonce = w3.eth.get_transaction_count(ownerAddress)

    # Build the transaction to call the function
    transaction = contract.functions.setPatientHashPointer(patientAddress, hash, pointer).build_transaction({
        'from': ownerAddress,
        'chainId': Chain_id,
        'nonce': nonce,  
    })

    # Sign the transaction
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)  

    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    # Wait for the transaction to be mined
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    #run the function
    #contract.functions.setPatientHashPointer(patientAddress, hash, pointer).call({'from': ownerAddress})

  else:
    return -1
  
  return 1

#----------------------------------------------------------------------------------------------------

#Database Query Functions

#function for patient to get his medical record from the database
#gets called when the patient clicks a button on the UI interface
#returns medical record or error
def patientDatabaseQuery(contract, patientAddress):
  
  #get hash and pointer from smart contract
  pointer = contract.functions.returnPointer(patientAddress).call()
  hash = contract.functions.returnHash(patientAddress).call()
  
  print("pointer", pointer)
  print("hash", hash)

  #return is there to end function early for testing the rest has to do with the database
  return

  #Use the pointer to return the medical record
  MR = queryDatabase(pointer)

  #Encode the medical record and check it matches the hash
  
  #if it does return the medical record, will need to print this client side
  if checkHash(hash, MR):
    return MR 

  #else return -1, somehandling client side will be needed to show an error message if this -1 is returned
  return -1 


#funtion for doctor to get the medical record of a patient from the database
#gets called when the doctor clicks on a button in the UI interface
#returns the patient's medical record or an error
#returns -1 for hash mismatch error
#returns -2 for permission error
def doctorDatabaseQuery(contract, patientAddress, doctorAddress):


  if(contract.functions.doctorCheckPermissions(patientAddress, doctorAddress).call()):

    pointer = contract.functions.returnPointer(patientAddress).call()
    hash = contract.functions.returnHash(patientAddress).call()

    print("pointer", pointer)
    print("hash", hash)


    #return is there to end function early for testing the rest has to do with the database
    return
    if pointer != None:
      #Use the pointer to return the medical record
      MR = queryDatabase(pointer)

      #Encode the medical record and check it matches the hash
      #if it does return the medical record, will need to print this client side
      if checkHash(hash, MR):
        return MR 

      #else return -1, somehandling client side will be needed to show an error message if this -1 is returned
      return -1 
  
  #else return no permission error or -2
  return -2

#----------------------------------------------------------------------------------------------------
