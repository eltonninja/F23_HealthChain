import requests
import json

# Replace 'your_fhir_data.json' with the path to your FHIR JSON file
with open('Sharyl439_Farrell962_31979ebb-074d-be12-13e0-9eb1bff7fad9.json', 'r') as file:
    fhir_data = json.load(file)

response = requests.post('http://localhost:5000/fhir_predict', json=fhir_data)

if response.status_code == 200:
    print("Prediction:", response.json())
else:
    print("Error:", response.json())