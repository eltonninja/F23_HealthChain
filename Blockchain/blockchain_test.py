def test():
  blockChain = BlockchainClass()
  
  patient_address = "0x0000000000000000000000000000000000000000"
  doctor_address =  "0x0000000000000000000000000000000000000001"
  
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
  print("Patient Data Query results: ", blockChain.patientHashPointer(patient_address))
  
  #get medical records as doctor
  blockChain.doctorHashPointer(patient_address, doctor_address)
  print("Doctor Data Query results: ", blockChain.patientHashPointer(patient_address))

  
  #remove authorized doctor
  blockChain.removeAuthorizedDoctor(patient_address, doctor_address)
  print("Removed doctor")
  
  #test upload record while not having permissions
  hash_ = "testHash2"
  pointer = "testPointer2"

  results = blockChain.uploadRecord(patient_address, doctor_address, hash_, pointer)
  print("Second upload: ", results)

  #get medical records as patient
  print("Patient Data Query results: ", blockChain.patientHashPointer(patient_address))

if __name__ == "__main__":
  test()
