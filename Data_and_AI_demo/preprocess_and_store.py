import pandas as pd
from pathlib import Path
import os
import numpy as np
import pickle
from sklearn.decomposition import SparsePCA
from feature_engineering import FeatureEngineering

class DataPreprocessor:

    def __init__(self, target_diseases):
        self.means = {}
        self.stds = {}
        self.target_diseases = target_diseases
    
    def fit(self, df_master, sequence_length):                

        self.sequence_length = sequence_length
        self.master_feature_list = list(df_master)         
        for feat in self.master_feature_list:
            featList = df_master[feat]            
            if feat[-2:] == '_o':                
                self.means[feat] = featList.mean(skipna=True)
                self.stds[feat] = featList.std(skipna=True)

        self.ignoreX = set(self.target_diseases) 

    # normalization parameters are taken across
    # patient averages        
    def fit_by_item(self, dfs, master_feature_list, sequence_length):                

        self.sequence_length = sequence_length
        self.master_feature_list = master_feature_list
        self.items = {feat:[] for feat in master_feature_list}
        for df in dfs:
            for feat in list(df):                            
                if feat[-2:] == '_o':  
                    featList = df[feat] 
                    self.items[feat].append(featList.mean(skipna=True))

        for feat in self.master_feature_list:
            if feat[-2:] == '_o': 
                featList = pd.Series(self.items[feat]) 
                self.means[feat] = featList.mean(skipna=True)
                self.stds[feat] = featList.std(skipna=True)

        self.ignoreX = set(self.target_diseases)     
       
    
    def transform(self, Xs):

        i = 0
        Xs_transformed = []
        for df in Xs:
            transformed = {}
            for feat in list(df):
                featList = df[feat]
                suffix = feat[-2:]
                if suffix == '_o':
                    mean, sd = self.means[feat], self.stds[feat] 
                    if not pd.isna(mean) and not pd.isna(sd) and sd != 0:
                        transformed[feat] = (featList.fillna(mean) - mean) / sd
                elif suffix == '_c':                
                    transformed[feat] = featList.ffill().fillna(0)
                else:
                    transformed[feat] = featList.ffill()

            i += 1
            if i % 1000 == 0:              
                print(i, '/', len(Xs))         

            Xs_transformed.append(pd.DataFrame(transformed))

        return Xs_transformed    

def sequence(patient_data, target_diseases, sequence_length):

    hourMinimum = 24 * 365
    step = max((sequence_length // 2) + 5, 1)    

    patient_data_sequences = []
    for patient_df in patient_data:
        feats = list(patient_df)
        # computer limit on storage was reached
        included = [feat for feat in target_diseases if feat in feats and feat in ['Lupus erythematosus_c']]
        leng = len(included)
        targ_vals = patient_df[included].sum(axis=1)
        patient_df_sequences = []
        t = 1
        for i in range(sequence_length, len(patient_df)):
            if t and leng and targ_vals.iloc[i - 1] > 0:
                sequence = patient_df.iloc[i-sequence_length:i]
                patient_df_sequences.append(sequence)
                t = 0
            elif i % step == 0:    
                sequence = patient_df.iloc[i-sequence_length:i]    
                if sequence['time_between_visits_o'].sum() > hourMinimum:
                    patient_df_sequences.append(sequence)
                else:
                    t = 1        
            else:
                t = 1            
        patient_data_sequences.extend(patient_df_sequences)      

    return patient_data_sequences      

def assemble_data(patient_app_directory, stop = None):
  
    data = []
    unique_features = []
    condition_numbers = {}
    i = 0
    for file_path in Path(patient_app_directory).glob('*.csv'):
        i += 1
        if stop != None and i > stop:
            break
        patient_data = pd.read_csv(file_path)
        if len(patient_data) < sequence_length:
            print(file_path, "Rejected for short length")
            continue
        feats = list(patient_data)                
        #sequences = sequence(patient_data, sequence_length)
        for feat in feats:
            if feat[-2:] == '_c':
                patient_data[feat] = patient_data[feat].ffill()          
        data.append(patient_data)
        print(file_path)
        for feat in list(patient_data):
            if feat == "Unnamed: 0":
                continue
            Sum = patient_data[feat].sum(skipna = True)   
            if feat not in unique_features:                
                unique_features.append(feat)
                if feat[-2] != "_" or Sum > 0:
                    condition_numbers[feat] = 1
                else:
                    condition_numbers[feat] = 0   
            elif feat[-2] != "_" or Sum > 0:
                 condition_numbers[feat] += 1

    print(condition_numbers)            
    return data, unique_features


def concatenate_dataframes(dfs, master_feature_list, ignore = set(), preprocessed = True):
  
    i = 0     
    concatenated_data = {feat: [] for feat in master_feature_list if feat not in ignore}
    for patient_data in dfs:
        sequence_length = len(patient_data)
        patient_features = set(patient_data.columns)
        for feat in concatenated_data.keys():
            if feat in patient_features:
                concatenated_data[feat].extend(patient_data[feat])
            else:
                if preprocessed:
                    concatenated_data[feat].extend([0] * sequence_length)
                else:    
                    concatenated_data[feat].extend([np.nan] * sequence_length)
        i += 1
        if i % 1000 == 0:              
            print(i, '/', len(dfs))        

    return pd.DataFrame(concatenated_data) 


def choose_targets(target_diseases, sequenced_data):
    
    Xs, ys = [], []
    indexes = np.arange(len(sequenced_data))
    np.random.shuffle(indexes)
    for i in range(len(sequenced_data)):
        data_point = sequenced_data[i]
        featList = list(data_point)
        y = {target_disease: [] for target_disease in target_diseases}
        for target_disease in target_diseases:
            if target_disease in featList:
                y[target_disease].append(data_point[target_disease].iloc[-1])
                data_point.drop(target_disease, axis = 1, inplace = True)
            else:
                y[target_disease].append(0)                    

        Xs.append(data_point)
        ys.append(pd.DataFrame(y))

    return Xs, ys    


def split_data(data, train, val):    

    trainPartition = int(len(data) * train)   

    data_train, data_test = data[:trainPartition], data[trainPartition:]

    valPartition = int(len(data_train) * val)

    data_val, data_train = data_train[:valPartition], data_train[valPartition:]

    return data_train, data_val, data_test


def assemble_master_feature_list(dfs):
    master_feature_list = []
    for df in dfs:
        for feat in list(df):
            if feat not in master_feature_list:
                master_feature_list.append(feat)

    return master_feature_list            


def store_sequential_data(data_directory, target_diseases, sequence_length, train, val):
    
    print("Assembling data")
    data, master_feature_list = assemble_data(data_directory)
    print("Assembling data completed:", len(data))

    print("Concatenating")
    combined_data = concatenate_dataframes(data, master_feature_list, preprocessed = False)
    print("Concatenating completed")

    print("Feature engineering")
    FEO = FeatureEngineering(data, combined_data, master_feature_list)
    data_FE = [FEO.apply(df) for df in data]
    master_feature_list = assemble_master_feature_list(data_FE)
    with open('FE_data_obj_demo.pkl', 'wb') as file:
        pickle.dump(FEO, file)
    print("Feature engineering completed")

    print("Sequencing")
    data_FE_sequenced = sequence(data_FE, set(target_diseases), sequence_length)
    print("Sequencing completed")

    data_train, data_val, data_test = split_data(data_FE_sequenced, train, val)

    preprocess_data_obj = DataPreprocessor(target_diseases)

    print("Fitting train data for preprocessing")
    preprocess_data_obj.fit_by_item(data_FE[:int(train*len(data_FE))], master_feature_list, sequence_length)
    with open('preprocess_data_obj_demo.pkl', 'wb') as file:
        pickle.dump(preprocess_data_obj, file)
    print("Fitting train data for preprocessing completed")

    print("Transforming train data for preprocessing")
    data_train_preprocessed = preprocess_data_obj.transform(data_train)
    X_train_preprocessed, y_train = choose_targets(target_diseases, data_train_preprocessed)
    print("Transforming train data for preprocessing completed")

    print("Transforming val data for preprocessing")
    data_val_preprocessed = preprocess_data_obj.transform(data_val)
    X_val_preprocessed, y_val = choose_targets(target_diseases, data_val_preprocessed)
    print("Transforming val data for preprocessing completed")

    print("Transforming test data for preprocessing")
    data_test_preprocessed = preprocess_data_obj.transform(data_test)
    X_test_preprocessed, y_test = choose_targets(target_diseases, data_test_preprocessed)
    print("Transforming test data for preprocessing completed")

    print("Sending to csv")
    ignoreX = preprocess_data_obj.ignoreX
    train_master_feature_list = preprocess_data_obj.master_feature_list
    print("Ignored:", ignoreX)    
    concatenate_dataframes(X_train_preprocessed, train_master_feature_list, ignoreX).to_csv(data_directory + '/data/X_train_s2.csv')
    concatenate_dataframes(y_train, target_diseases).to_csv(data_directory + '/data/y_train_s2.csv')
    concatenate_dataframes(X_val_preprocessed, train_master_feature_list, ignoreX).to_csv(data_directory + '/data/X_val_s2.csv')
    concatenate_dataframes(y_val, target_diseases).to_csv(data_directory + '/data/y_val_s2.csv')
    concatenate_dataframes(X_test_preprocessed, train_master_feature_list, ignoreX).to_csv(data_directory + '/data/X_test_s2.csv')
    concatenate_dataframes(y_test, target_diseases).to_csv(data_directory + '/data/y_test_s2.csv')
    print("Sending to csv completed")

if __name__ == "__main__":

    data_directory = 'C:/Users/schafj2/Desktop/S/Data'  
    target_diseases_easy = ['Prediabetes_c']  
    target_diseases_medium = ['Chronic kidney disease stage 1 (disorder)_c', 'Chronic kidney disease stage 2 (disorder)_c']
    target_diseases_hard = ['Osteoporosis (disorder)_c', 'Localized, primary osteoarthritis of the hand_c']  
    target_diseases = target_diseases_easy + target_diseases_medium + target_diseases_hard + ['Lupus erythematosus_c']
    sequence_length, train, val = 10, 0.8, 0.2   

    store_sequential_data(data_directory, target_diseases, sequence_length, train, val)