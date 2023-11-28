import pandas as pd
import numpy as np


# Feature engineering class for adding and removal of features
class FeatureEngineering:

    # designates master features and features for removal    
    def __init__(self, dfs, df_master, master_feature_list):
        self.master_feature_dict = {feat:0 for feat in master_feature_list}
        self.features_to_remove = set([
        "visit_date",
        "Cause of Death [US Standard Certificate of Death]_o",
        "Housing unsatisfactory (finding)_c",
        "Received higher education (finding)_c",
        "Full-time employment (finding)_c",
        "Social isolation (finding)_c",
        "Limited social contact (finding)_c",
        "Part-time employment (finding)_c",
        #"Stress (finding)_c",
        #"Protocol for Responding to and Assessing Patients' Assets, Risks, and Experiences [PRAPARE]_o",
        "Fall risk total [Morse Fall Scale]_o",
        "Fall risk level [Morse Fall Scale]_o",
        "Total score [DAST-10]_o",
        #"Patient Health Questionnaire 2 item (PHQ-2) total score [Reported]_o",
        #"Patient Health Questionnaire 9 item (PHQ-9) total score [Reported]_o",
        "Patient transfer to skilled nursing facility (procedure)_c",
        #"Tobacco smoking status_o",
        "Unemployed (finding)_c",
        "Not in labor force (finding)_c",
        "Refugee (person)_c",
        "Lack of access to transportation (finding)_c",
        "Transport problem (finding)_c",
        "Has a criminal record (finding)_c",
        "Served in armed forces (finding)_c",
        "Unhealthy alcohol drinking behavior (finding)_c",
        "Reports of violence in the environment (finding)_c",
        "Homeless (finding)_c",
        #"Sexual orientation_o",
        "HIV status_o",
        "Abuse Status [OMAHA]_o",
        "Housing status_o",
        "Are you covered by health insurance or some other kind of health care plan [PhenX]_o",
        "History of Hospitalizations+Outpatient visits Narrative_o",
        "Died in hospice (finding)_c",
        "Only received primary school education (finding)_c",
        "Smokes tobacco daily_c",
        "Social migrant (finding)_c",
        "Medication management note_o",
        "Veterans Rand health survey - 36 item (VR-36)_o",
        "Veterans Rand health survey - 12 item (VR-12)_o",
        "Functional capacity NYHA_o",
        "Objective assessment of cardiovascular disease NYHA_o",
        "PROMIS short form - global - version 1.1_o",
        "Mental health Outpatient Note_o",
        "Mental health Telehealth Note_o"
        ])

        for feat in master_feature_list:
            featList = df_master[feat]
            if len(featList) - featList.isna().sum() < 20:
                self.features_to_remove.add(feat) 

        occurences = {feat:0 for feat in master_feature_list}            
        for df in dfs:
            for feat in list(df):
                occurences[feat] += 1

        for feat in master_feature_list:
            if occurences[feat] < 5:
                 self.features_to_remove.add(feat)               


    # applies all usable engineered features and drops 
    # designated features               
    def apply(self, record):

        feats = list(record)
        present_feature_dict = self.master_feature_dict.copy()
        for feat in feats:
            present_feature_dict[feat] = 1
        self.engineered_features = {} 
        self.helpers = {} 

        if present_feature_dict['visit_date']:
            self.helpers['visit_time'] = pd.to_datetime(record['visit_date'], utc=True)
            self.add_time_between_visits(record)
            self.add_seasonality_features(record)
            self.add_visit_frequency(record)
        
        self.add_visit_count_in_windows(record)

        for feat in self.features_to_remove:
            if feat in feats:
                record.drop(feat, axis = 1, inplace = True)    

        return record.join(pd.DataFrame(self.engineered_features))


    def add_time_between_visits(self, record):
        self.engineered_features['time_between_visits_o'] = self.helpers['visit_time'].diff().dt.total_seconds().div(3600)

    def add_seasonality_features(self, record):
        self.helpers['month'] = self.helpers['visit_time'].dt.month
        self.engineered_features['visit_in_summer_c'] = np.where((self.helpers['month'] >= 6) & (self.helpers['month'] <= 8), 1, 0)
        self.engineered_features['visit_in_winter_c'] = np.where((self.helpers['month'] >= 12) | (self.helpers['month'] <= 2), 1, 0)
        self.engineered_features['visit_in_fall_c'] = np.where((self.helpers['month'] >= 9) & (self.helpers['month'] <= 11), 1, 0)
        self.engineered_features['visit_in_spring_c'] = np.where((self.helpers['month'] >= 3) & (self.helpers['month'] <= 5), 1, 0)

    def add_visit_frequency(self, record):
        # Assuming monthly intervals for simplicity
        self.engineered_features['time_between_visits_5_o'] = self.helpers['visit_time'].diff(5).dt.total_seconds().div(3600)

    def add_visit_count_in_windows(self, record):
        # Example: Count visits per month
        self.engineered_features['visit_count_per_month_o'] = record.index
    
