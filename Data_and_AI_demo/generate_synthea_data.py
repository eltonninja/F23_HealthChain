import subprocess
import os

# Set the path to your Synthea directory
synthea_path = "C:/Users/schafj2/synthea"

# Variables
num_patients, seed = 1000, 1234

os.chdir(synthea_path)

# Generate the FHIR data
subprocess.run([synthea_path + "\\run_synthea.bat", "-s", str(seed), "-p", str(num_patients)], shell=True)
