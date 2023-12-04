import requests
import json
import os
from pathlib import Path
from flask import Flask, request, jsonify
import tensorflow as tf
import pandas as pd
import json
from FHIR_to_csv import process_fhir_data
from preprocess_and_store import concatenate_dataframes
from tensorflow.keras.models import load_model
from preprocess_and_store import DataPreprocessor
from transformer import F1Score
import pickle
import numpy as np

specialists = {'Chronic sinusitis (disorder)': 'Otolaryngologist', 'Prediabetes' : 'Endocrinologist', 
    'Chronic kidney disease stage 1 (disorder)': 'Nephrologist', 'Chronic kidney disease stage 2 (disorder)': 'Nephrologist',
    'Osteoporosis (disorder)': 'Endocrinologist', 'Localized, primary osteoarthritis of the hand': 'Rheumatologist', 
    'Lupus erythematosus': 'Rheumatologist'}

with open('preprocess_data_obj.pkl', 'rb') as file:
    preprocess_data_obj = pickle.load(file)

with open('FE_data_obj.pkl', 'rb') as file:
    FE_data_obj = pickle.load(file)  

model = load_model('medical_transformer', custom_objects={'F1Score': F1Score})

def load_fhir_json(file_path):
    with open(file_path, 'r', encoding = 'utf-8') as f:
        return json.load(f)

def fhir_predict(fhir_json):

    # Process FHIR JSON to DataFrame
    patient_df = process_fhir_data(fhir_json)
    if len(patient_df) <  10:
    	return "none"	
    patient_df_FE = FE_data_obj.apply(patient_df)
    patient_df_preprocessed = preprocess_data_obj.transform([patient_df_FE])
    master_feature_list, sequence_length, ignoreX = preprocess_data_obj.master_feature_list, preprocess_data_obj.sequence_length, preprocess_data_obj.ignoreX     
    patient_df_preprocessed = concatenate_dataframes(patient_df_preprocessed, master_feature_list, ignoreX)     
    #patient_df_pca = pd.DataFrame(sparse_pca.transform(patient_df_preprocessed))
    current_sequence = tf.constant([patient_df_preprocessed.iloc[-sequence_length:].values])

    # Make prediction

    predictions = model.predict(current_sequence).tolist()[0]
    disease_pred_dict = {}
    recommendation = "none"
    suspected_disease = "none"
    for disease, pred in zip(preprocess_data_obj.target_diseases, predictions):
        disease_pred_dict[disease[:-2]] = pred
    predMax = np.max(predictions)
    if predMax > 0.7:
        suspected_disease = preprocess_data_obj.target_diseases[np.argmax(predictions)][:-2]
        recommendation = specialists[suspected_disease]         

    # Format and send back the predictions
    return recommendation    

def process_dir(input_dir):

    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        #print(os.path.getsize(file_path))
        if len(file_name.split('_')) <= 2 or file_name[-41] != 'f' or os.path.getsize(file_path) > 25000000:
            continue
        print(file_path)
        fhir_data = load_fhir_json(file_path)
        rec = fhir_predict(fhir_data)
        print(rec)
        if rec == "Rheumatologist":
        	print(rec)
        	break        

if __name__ == "__main__":    

	#input_dir = 'C:/Users/schafj2/synthea/output/fhir'
	#process_dir(input_dir)

	fhir_data = load_fhir_json('Clint766_Hyatt152_f98eb589-baf2-b1cb-9bf6-7c68016d0018.json')
	rec = fhir_predict(fhir_data)
	print(rec)

	fhir_data = load_fhir_json('Collin529_Weimann465_f63c6119-c079-20c4-3230-0bb3d63c0e78.json')
	rec = fhir_predict(fhir_data)
	print(rec)

	fhir_data = load_fhir_json('Corey514_O\'Keefe54_f10438de-565e-f23e-324d-aeda087f602c.json')
	rec = fhir_predict(fhir_data)
	print(rec)

	fhir_data = load_fhir_json('Clark193_Quigley282_f6d03243-2451-2a27-5d80-8f40b6d74d6d.json')
	rec = fhir_predict(fhir_data)
	print(rec)
