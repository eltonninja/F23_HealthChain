#Helper Functions

#function to query the database at a given pointer  
def queryDatabase(pointer):
  #TODO: request database using pointer
  #TODO: return the medical record given
  pass

#function to check that the hash matches the medical record
#the key for encoding/decoding the medical record is a hash of the medical record with a set key
def checkHash(hash, MR):
  setKey = "exampleKey"
  #TODO: encode MR using the setKey to get the key
  #TODO: using that key encode the medical record and make sure it matches with the hash
  #return True if success and False otherwise
  pass

#----------------------------------------------------------------------------------------------------

#Database Query Functions

#function for patient to get his medical record from the database
#gets called when the patient clicks a button on the UI interface
#returns medical record or error
def patientDatabaseQuery():
   
  pointer, hash = #TODO: request the pointer to the database and the hash from the contract
  
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
def doctorDatabaseQuery(patientAddress):

  pointer, hash = #TODO: request the pointer to the database and the hash from the contract
  #if that returns successfully
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

#Patient queries the AI

#I'm not sure how the AI query is going to work so this function is subject to change
#The patient should press a button to query the AI 
def queryAI(MR):

  #query the database for the medical record
  MR = patientDatabaseQuery()

  #check that the medical record returned successfully and if it doesn't return -1 for the error 
  if MR == -1:
    return -1

  #TODO: Query the AI and return the results
  #if there needs to be some preprocessing of the medical record before querying take care of that too

  pass

#----------------------------------------------------------------------------------------------------

#Patient adds/remove doctor to his list of allowed doctors

#Patient adds doctor to his list of allowed doctors
#happens when the patient does something on the UI (not sure how that looks)
def addDoctor(address):
  #address is the doctor's blockchain address
  #TODO: Add the doctor using the smart contract
  pass


#Patient removes doctor to his list of allowed doctors
#happens when the patient does something on the UI (not sure how that looks)
def removeDoctor(address):
  #address is the doctor's blockchain address
  #TODO: Remove the doctor using the smart contract
  pass

#----------------------------------------------------------------------------------------------------

#Doctor upload/edit medical record

#uploads the patient medical record to the database
#doctor uploads a FHIR or CSV file (tbd) through the UI
def uploadRecord(record):

  #TODO: Check permission using the smart contract
    #return an error if no permission
  
  #TODO: Maybe some preprocessing idk

  #TODO: add the medical record to the database 
  #TODO: hash the record 
  #TODO: update the patients pointer and has on the smart contract
  
  return 1


#might not need to be different depends on whether we want to remove the old record from the database or not 
def editRecord(newRecord):

  #TODO: Check permission using the smart contract
    #return an error if no permission
  
  #TODO: Remove the record from the database

  #upload newRecord
  return uploadRecord(newRecord)
