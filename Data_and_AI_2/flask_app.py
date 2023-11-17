from flask import Flask, request, jsonify
import tensorflow as tf
import pandas as pd
import json
from FHIR_to_csv import process_fhir_data
from preprocess_and_store import concatenate_dataframes
from tensorflow.keras.models import load_model
import pickle

app = Flask(__name__)

# Load the object from the file
with open('preprocess_data_obj.pkl', 'rb') as file:
    preprocess_data_obj = pickle.load(file)

model = load_model('path')

@app.route('/fhir_predict', methods=['POST'])
def fhir_predict():
    try:
        # Receive FHIR JSON data
        fhir_json = request.json

        # Process FHIR JSON to DataFrame
        patient_df = process_fhir_data(fhir_json)
        patient_df_preprocessed = preprocess_data_obj.transform([patient_df])
        master_feature_list, sequence_length, ignoreX = preprocess_data_obj.master_feature_list, preprocess_data_obj.sequence_length, preprocess_data_obj.ignoreX
        patient_df_preprocessed = concatenate_dataframes(patient_df_preprocessed, master_feature_list, sequence_length, ignoreX)  

        # Make prediction
        predictions = model.predict(patient_df_preprocessed)

        # Format and send back the predictions
        return jsonify(predictions.tolist())
    except Exception as e:
        return jsonify({"error": str(e)}), 500