import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime

def load_fhir_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_age(birth_date_str, visit_dates):

    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")

    ages = []
    for visit_date_str in visit_dates:
        visit_date_Y, visit_date_M, visit_date_D = visit_date_str.split('T')[0].split('-')   
        age = int(visit_date_Y) - birth_date.year - ((int(visit_date_M), int(visit_date_D)) < (birth_date.month, birth_date.day))
        ages.append(age)
    
    return ages

def get_patient_static_data(patient_resource):

    patient_id = patient_resource['id']
    gender = patient_resource['gender']
    birth_date = patient_resource['birthDate']

    if gender == 'male':
        return patient_id, {'male': 1, 'female': 0, 'birth_date': birth_date}
    elif gender == 'female':
        return patient_id, {'male': 0, 'female': 1, 'birth_date': birth_date}
    else:
        return patient_id, {'male': 0, 'female': 0, 'birth_date': birth_date}       

def extract_visit_data(entries, patient_to_visits_map):
    for entry in entries:
        resource = entry['resource']
        resource_type = resource['resourceType']
        
        if resource_type == 'Encounter':
            patient_id = resource['subject']['reference'].split(':')[-1]
            visit_id = resource['id']
            visit_date = resource['period']['start']
            
            if patient_id not in patient_to_visits_map:
                patient_to_visits_map[patient_id] = {}
            
            patient_to_visits_map[patient_id][visit_id] = {'visit_date': visit_date}
            
        elif resource_type in ['Condition', 'Observation']:
            patient_id = resource['subject']['reference'].split(':')[-1]          
            visit_id = resource['encounter']['reference'].split(':')[-1]
            visit_data = patient_to_visits_map[patient_id][visit_id]            
                
            if resource_type == 'Condition':
                condition_code = resource['code']['coding'][0]['code']
                condition_status = resource['clinicalStatus']['coding'][0]['code']
                condition_name = resource['code']['coding'][0]['display']
                visit_data[condition_name + '_c'] = 1 if condition_status == 'active' else 0
            
            elif resource_type == 'Observation':
                observation_code = resource['code']['coding'][0]['code']
                observation_value = resource.get('valueQuantity', {}).get('value', None)
                obs_name = resource['code']['coding'][0]['display']
                visit_data[obs_name + '_o'] = observation_value
            
            patient_to_visits_map[patient_id][visit_id] = visit_data


def process_patient_data(patient_id, visits, patient_static_data):

    visit_data_list = list(visits.values())
    patient_df = pd.DataFrame(visit_data_list)

    patient_df['age_o'] = calculate_age(patient_static_data[patient_id]['birth_date'], patient_df['visit_date'])
    patient_df['male'] = patient_static_data[patient_id]['male']
    patient_df['female'] = patient_static_data[patient_id]['female']
    
    col_order = ['visit_date', 'male', 'female', 'age_o'] + [col for col in patient_df if col not in ['visit_date', 'male', 'female', 'age_o']]
    patient_df = patient_df[col_order]
    
    patient_df.sort_values(by='visit_date', inplace=True)  

    return patient_df  


def save_patient_data_to_csv(patient_to_visits_map, patient_static_data, output_dir):

    for patient_id, visits in patient_to_visits_map.items():
        patient_df = process_patient_data(patient_id, visits, patient_static_data)              
        patient_df.to_csv(os.path.join(output_dir, f'patient_{patient_id}.csv'), index=False)


def assign_patient_data(entries, patient_static_data):

    for entry in entries:
        resource = entry['resource']
        resource_type = resource['resourceType']
        
        if resource_type == 'Patient':
            patient_id, static_data = get_patient_static_data(resource)
            patient_static_data[patient_id] = static_data
            break

def process_fhir_data(fhir_json):

    patient_to_visits_map, patient_static_data = {}, {}
    entries = fhir_json.get('entry', [])
    extract_visit_data(fhir_json.get('entry', []), patient_to_visits_map, patient_static_data)
    
    assign_patient_data(entries, patient_static_data)
    extract_visit_data(entries, patient_to_visits_map)        
    
    patient_df = process_patient_data(patient_to_visits_map, patient_static_data)

    return patient_df 


def process_fhir_directory(input_dir, output_dir):

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    patient_to_visits_map = {}
    patient_static_data = {}

    for file_name in os.listdir(input_dir):
        if len(file_name.split('_')) <= 2:
            continue
        file_path = os.path.join(input_dir, file_name)
        print(file_name)
        fhir_data = load_fhir_json(file_path)
        entries = fhir_data.get('entry', [])
        
        assign_patient_data(entries, patient_static_data)        
        extract_visit_data(entries, patient_to_visits_map)
    
    save_patient_data_to_csv(patient_to_visits_map, patient_static_data, output_dir)

input_directory = 'C:/Users/schafj2/synthea/output/fhir'
output_directory = 'C:/Users/schafj2/Desktop/S/Data'

process_fhir_directory(input_directory, output_directory)