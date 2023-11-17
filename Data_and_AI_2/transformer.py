import tensorflow as tf
from tensorflow.keras import layers, models
import pandas as pd


def build_transformer2(input_shape, num_diseases, head_size, num_heads, ff_dim, num_transformer_blocks):
    
    inputs = layers.Input(shape=input_shape)

    # Embedding for categorical data (is necessary and unimplemented)
    # x = Embedding_layer(x)
    
    # Initial LayerNormalization (mixed with batch normalization on input: not ideal)
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

def build_transformer(input_shape, num_diseases, head_size, num_heads, ff_dim, num_transformer_blocks):
    
    inputs = layers.Input(shape=input_shape)

    # Embedding for categorical data (is necessary and unimplemented)
    # x = Embedding_layer(x)
    
    # Initial LayerNormalization (mixed with batch normalization on input: not ideal)
    x = inputs

    # Transformer blocks
    for _ in range(num_transformer_blocks):

        attn_output = layers.MultiHeadAttention(
            key_dim=head_size, num_heads=num_heads, dropout=0.1
        )(x, x)
        
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


def transformer_app(train_data_dfs, train_label_df, val_data_dfs, val_label_df, test_data_dfs, test_label_df):    

    train_data = tf.constant([df.values for df in train_data_dfs])
    train_labels = tf.constant([train_label_df.iloc[i] for i in range(len(train_label_df))])
    val_data = tf.constant([df.values for df in val_data_dfs])
    val_labels = tf.constant([val_label_df.iloc[i] for i in range(len(val_label_df))])
    test_data = tf.constant([df.values for df in test_data_dfs])
    test_labels = tf.constant([test_label_df.iloc[i] for i in range(len(test_label_df))])

    train_dataset = tf.data.Dataset.from_tensor_slices((train_data, train_labels))
    val_dataset = tf.data.Dataset.from_tensor_slices((val_data, val_labels))
    test_dataset = tf.data.Dataset.from_tensor_slices((test_data, test_labels))

    batch_size = 64
    train_dataset = train_dataset.batch(batch_size)
    val_dataset = val_dataset.batch(batch_size)
    test_dataset = test_dataset.batch(batch_size)

    train_dataset = train_dataset.prefetch(tf.data.experimental.AUTOTUNE)
    val_dataset = val_dataset.prefetch(tf.data.experimental.AUTOTUNE)
    test_dataset = test_dataset.prefetch(tf.data.experimental.AUTOTUNE)

    input_shape = train_data.shape[1:]
    output_units = len(train_labels[0])
    head_size = 20
    num_heads = 10
    ff_dim = 256
    num_transformer_blocks = 1
    ep = 30
    pat = 1
    show = 1

    model = build_transformer(
        input_shape, output_units, head_size, num_heads, ff_dim, num_transformer_blocks
    )

    history = model.fit(train_dataset, validation_data=val_dataset, epochs = ep, 
        callbacks = tf.keras.callbacks.EarlyStopping(monitor = "val_loss", 
            patience = pat, restore_best_weights = True), workers = 16, use_multiprocessing=True, verbose = show)

    test_loss, test_accuracy = model.evaluate(test_dataset)
    print(f"Test Loss: {test_loss}, Test Accuracy: {test_accuracy}")

data_directory = 'C:/Users/schafj2/Desktop/S/Data/data'
sequence_length = 10

X_train = pd.read_csv(data_directory + '/X_train.csv').drop('Unnamed: 0', axis = 1)
y_train = pd.read_csv(data_directory + '/y_train.csv').drop('Unnamed: 0', axis = 1)
X_val = pd.read_csv(data_directory + '/X_val.csv').drop('Unnamed: 0', axis = 1)
y_val = pd.read_csv(data_directory + '/y_val.csv').drop('Unnamed: 0', axis = 1)
X_test = pd.read_csv(data_directory + '/X_test.csv').drop('Unnamed: 0', axis = 1)
y_test = pd.read_csv(data_directory + '/y_test.csv').drop('Unnamed: 0', axis = 1)

for feat in list(y_test):
    print(feat, y_test[feat].sum())

print("Length:", len(list(X_train)))   

train_data_dfs = [X_train.iloc[i:i + sequence_length] for i in range(0, len(X_train), sequence_length)]
train_label_df = y_train
val_data_dfs = [X_val.iloc[i:i + sequence_length] for i in range(0, len(X_val), sequence_length)]
val_label_df = y_val
test_data_dfs = [X_test.iloc[i:i + sequence_length] for i in range(0, len(X_test), sequence_length)]
test_label_df = y_test

transformer_app(train_data_dfs, train_label_df, val_data_dfs, val_label_df, test_data_dfs, test_label_df)