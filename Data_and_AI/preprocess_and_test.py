import pandas as pd
from pathlib import Path
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

class DataPreprocessor:

    def __init__(self):
        self.means = {}
        self.stds = {}
        self.sequence_length = 0
    
    def fit(self, X_train, sequence_length):
        
        self.sequence_length = sequence_length
        df_master = pd.concat(X_train, ignore_index=True)
        for feat in list(df_master):
            featList = df_master[feat]
            if feat[-2:] == '_o':                
                self.means[feat] = featList.mean(skipna=True)
                self.stds[feat] = featList.std(skipna=True)
    
    def transform(self, Xs):

        Xs_transformed = []
        for df in Xs:
            transformed = {}
            for feat in list(df):
                if feat == 'visit_date':
                    continue
                featList = df[feat]
                suffix = feat[-2:]
                if suffix == '_o':
                    mean, sd = self.means[feat], self.stds[feat] 
                    if not pd.isna(mean) and not pd.isna(sd): 
                        transformed[feat] = (df[feat].fillna(mean) - mean) / sd
                elif suffix == '_c':                
                    group_ids = np.arange(len(featList)) // self.sequence_length
                    transformed[feat] = featList.groupby(group_ids).ffill().fillna(0)
                else:
                    transformed[feat] = df[feat]        

            Xs_transformed.append(pd.DataFrame(transformed).astype(np.float32))

        return Xs_transformed    

def create_master_feature_template(data_directory):

    unique_features = []

    for file_path in Path(data_directory).glob('*.csv'):
        patient_data = pd.read_csv(file_path)
        patient_cols = patient_data.columns
        for col in patient_cols:
            if col not in unique_features:
                unique_features.append(col)

    master_feature_template = pd.DataFrame(columns=unique_features)

    return master_feature_template

def sequence(patient_data, sequence_length):

    if len(patient_data) < sequence_length:
        padding = pd.DataFrame([{}], index=range(sequence_length - len(patient_data)))
        patient_data = pd.concat([padding, patient_data], ignore_index=True)
    elif len(patient_data) > sequence_length:
        # Switch to multiple?
        patient_data = patient_data.tail(sequence_length)  

    return patient_data      

def assemble_data(data_directory, patient_app_directory, sequence_length):
  
    master_feature_template = create_master_feature_template(data_directory)

    sequenced_data = []
    for file_path in Path(patient_app_directory).glob('*.csv'):
        patient_data = pd.read_csv(file_path)        
        patient_features = master_feature_template.copy()
        for col in patient_data.columns:
            if col in patient_features.columns:
                patient_features[col] = patient_data[col]        
        
        sequenced_data.append(sequence(patient_features, sequence_length))    

    return sequenced_data

def choose_targets(target_diseases, sequenced_data):
    
    Xs, ys = [], []
    for data_point in sequenced_data:
        X, y = data_point.drop(columns=target_diseases), data_point[target_diseases].ffill().fillna(0).iloc[-1].values
        Xs.append(X)
        ys.append(y)

    return Xs, ys    


def split_data(Xs, ys, train, val):

    leng = len(Xs)

    trainPartition = int(leng * train)   

    X_train, y_train, X_test, y_test = Xs[:trainPartition], ys[:trainPartition], Xs[trainPartition:], ys[trainPartition:]

    valPartition = int(len(X_train) * val)

    X_val, y_val = X_train[:valPartition], y_train[:valPartition]
    X_train, y_train = X_train[valPartition:], y_train[valPartition:]

    return X_train, y_train, X_val, y_val, X_test, y_test


def build_transformer(input_shape, num_diseases, head_size, num_heads, ff_dim, num_transformer_blocks):
    inputs = layers.Input(shape=input_shape)

    # Embedding for categorical data, if necessary
    # x = Embedding_layer(x)
    
    # Initial LayerNormalization
    x = layers.LayerNormalization(epsilon=1e-6)(inputs)

    # Transformer blocks
    for _ in range(num_transformer_blocks):

        x1 = layers.LayerNormalization(epsilon=1e-6)(x)
        
        attn_output = layers.MultiHeadAttention(
            key_dim=head_size, num_heads=num_heads, dropout=0.1
        )(x1, x1)
        
        x2 = layers.Add()([x, attn_output])
        
        x2 = layers.LayerNormalization(epsilon=1e-6)(x2)
        
        ffn_output = layers.Conv1D(filters=x2.shape[-1], kernel_size=1, activation='relu')(x2)
        ffn_output = layers.Dropout(0.1)(ffn_output)
        
        x = layers.Add()([x2, ffn_output])

    x = layers.LayerNormalization(epsilon=1e-6)(x)
    x = layers.GlobalAveragePooling1D()(x)

    outputs = layers.Dense(num_diseases, activation='sigmoid')(x)

    model = models.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])


    return model


def model_app(train_sequences, train_labels, val_sequences, val_labels, test_sequences, test_labels):    

    train_data = tf.constant([df.values for df in train_sequences])
    val_data = tf.constant([df.values for df in val_sequences])
    test_data = tf.constant([df.values for df in test_sequences])

    train_dataset = tf.data.Dataset.from_tensor_slices((train_data, train_labels))
    val_dataset = tf.data.Dataset.from_tensor_slices((val_data, val_labels))
    test_dataset = tf.data.Dataset.from_tensor_slices((test_data, test_labels))

    batch_size = 5
    train_dataset = train_dataset.batch(batch_size)
    val_dataset = val_dataset.batch(batch_size)
    test_dataset = test_dataset.batch(batch_size)

    train_dataset = train_dataset.prefetch(tf.data.experimental.AUTOTUNE)
    val_dataset = val_dataset.prefetch(tf.data.experimental.AUTOTUNE)
    test_dataset = test_dataset.prefetch(tf.data.experimental.AUTOTUNE)

    input_shape = train_data.shape[1:]

    output_units = len(train_labels[0])
    head_size = 64
    num_heads = 1
    ff_dim = 256
    num_transformer_blocks = 4
    ep = 30
    pat = 10
    show = 1

    model = build_transformer(
        input_shape, output_units, head_size, num_heads, ff_dim, num_transformer_blocks
    )

    history = model.fit(train_dataset, validation_data=val_dataset, epochs = ep, 
        callbacks = tf.keras.callbacks.EarlyStopping(monitor = "val_loss", 
            patience = pat, restore_best_weights = True), workers = 16, use_multiprocessing=True, verbose = show)

    test_loss, test_accuracy = model.evaluate(test_dataset)
    print(f"Test Loss: {test_loss}, Test Accuracy: {test_accuracy}")


data_directory = 'C:/Users/schafj2/Desktop/S/Data'
patient_app_directory = 'C:/Users/schafj2/Desktop/S/Data'
sequence_length = 10

target_diseases = ['Infectious mediastinitis (disorder)_c', 'Acute bronchitis (disorder)_c']
sequenced_data = assemble_data(data_directory, patient_app_directory, sequence_length)

combined_sequenced_data = pd.concat(sequenced_data, ignore_index=True)

combined_sequenced_data.to_csv(patient_app_directory + '/assemble_samples/sample.csv')

Xs, ys = choose_targets(target_diseases, sequenced_data)

train, val = 0.8, 0.2

X_train, y_train, X_val, y_val, X_test, y_test = split_data(Xs, ys, train, val)

preprocess_data_obj = DataPreprocessor()
preprocess_data_obj.fit(X_train, sequence_length)

X_train_preprocessed = preprocess_data_obj.transform(X_train)
X_val_preprocessed = preprocess_data_obj.transform(X_val)
X_test_preprocessed = preprocess_data_obj.transform(X_test)

pd.concat(X_train_preprocessed, ignore_index=True).to_csv(patient_app_directory + '/sample_data/X_train.csv')
pd.concat(X_val_preprocessed, ignore_index=True).to_csv(patient_app_directory + '/sample_data/X_val.csv')
pd.concat(X_test_preprocessed, ignore_index=True).to_csv(patient_app_directory + '/sample_data/X_test.csv')

model_app(X_train_preprocessed, y_train, X_val_preprocessed, y_val, X_test_preprocessed, y_test)
