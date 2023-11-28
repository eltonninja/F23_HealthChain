import tensorflow as tf
from tensorflow.keras import layers, models
import pandas as pd
from tensorflow.keras.metrics import TruePositives, FalsePositives, FalseNegatives
from sklearn.decomposition import SparsePCA

#F1 score implementation
class F1Score(tf.keras.metrics.Metric):
    def __init__(self, num_labels, name='f1_score', **kwargs):
        super(F1Score, self).__init__(name=name, **kwargs)
        self.num_labels = num_labels
        self.true_positives = [TruePositives() for _ in range(num_labels)]
        self.false_positives = [FalsePositives() for _ in range(num_labels)]
        self.false_negatives = [FalseNegatives() for _ in range(num_labels)]

    def update_state(self, y_true, y_pred, sample_weight=None):
        y_pred = tf.round(y_pred)
        for i in range(self.num_labels):
            class_true = tf.gather(y_true, [i], axis=1)
            class_pred = tf.gather(y_pred, [i], axis=1)
            self.true_positives[i].update_state(class_true, class_pred, sample_weight)
            self.false_positives[i].update_state(class_true, class_pred, sample_weight)
            self.false_negatives[i].update_state(class_true, class_pred, sample_weight)

    def result(self):
        f1_scores = []
        for i in range(self.num_labels):
            precision = self.true_positives[i].result() / (self.true_positives[i].result() + self.false_positives[i].result() + tf.keras.backend.epsilon())
            recall = self.true_positives[i].result() / (self.true_positives[i].result() + self.false_negatives[i].result() + tf.keras.backend.epsilon())
            f1_score = 2 * ((precision * recall) / (precision + recall + tf.keras.backend.epsilon()))
            f1_scores.append(f1_score)
        return tf.reduce_mean(f1_scores)

    def reset_state(self):
        for i in range(self.num_labels):
            self.true_positives[i].reset_states()
            self.false_positives[i].reset_states()
            self.false_negatives[i].reset_states()

    def get_config(self):
        config = super().get_config()
        config.update({"num_labels": self.num_labels})
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)        


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
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', F1Score(num_diseases)])

    return model


# transformer architecture
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
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy', F1Score(num_diseases)])

    return model

# transformer parameters and setup
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
    head_size = 64
    num_heads = 8
    ff_dim = 256
    num_transformer_blocks = 1
    ep = 30
    pat = 1
    show = 1

    model = build_transformer(
        input_shape, output_units, head_size, num_heads, ff_dim, num_transformer_blocks
    )

    history = model.fit(train_dataset, validation_data=val_dataset, epochs = ep, 
        callbacks = tf.keras.callbacks.EarlyStopping(monitor = "val_f1_score", 
            patience = pat, restore_best_weights = True), workers = 16, use_multiprocessing=True, verbose = show)

    test_loss, test_accuracy, test_f1 = model.evaluate(test_dataset)
    print(f"Test Loss: {test_loss}, Test Accuracy: {test_accuracy}, Test F1: {test_f1}")
    preds = model.predict(test_dataset)
    counts = [0] * output_units
    for pred in preds:
        for i in range(len(pred)):
            if pred[i] >= 0.5:
                counts[i] += 1
    print(counts)            

    model.save('medical_transformer')

if __name__ == "__main__":

    data_directory = 'C:/Users/schafj2/Desktop/S/Data/data'
    sequence_length = 10

    X_train = pd.read_csv(data_directory + '/X_train_s.csv').drop('Unnamed: 0', axis = 1)
    y_train = pd.read_csv(data_directory + '/y_train_s.csv').drop('Unnamed: 0', axis = 1)
    X_val = pd.read_csv(data_directory + '/X_val_s.csv').drop('Unnamed: 0', axis = 1)
    y_val = pd.read_csv(data_directory + '/y_val_s.csv').drop('Unnamed: 0', axis = 1)
    X_test = pd.read_csv(data_directory + '/X_test_s.csv').drop('Unnamed: 0', axis = 1)
    y_test = pd.read_csv(data_directory + '/y_test_s.csv').drop('Unnamed: 0', axis = 1)

    for feat in list(X_train):
        print(feat, (X_train[feat] != 0).sum(), (X_val[feat] != 0).sum(), (X_test[feat] != 0).sum())

    for feat in list(y_train):
        print(feat, (y_train[feat] != 0).sum(), (y_val[feat] != 0).sum(), (y_test[feat] != 0).sum())

    print("Length:", len(list(X_train)))  

    # Sparse PCA

    """    
    n_components = 0.95 
    alpha = 0.0001  

    sparse_pca = SparsePCA(n_components=n_components, alpha=alpha, random_state=42)

    sparse_pca.fit(X_train)

    X_train_pca = pd.DataFrame(sparse_pca.transform(X_train))
    X_val_pca = pd.DataFrame(sparse_pca.transform(X_val))
    X_test_pca = pd.DataFrame(sparse_pca.transform(X_test)) 

    print(X_train_pca.shape)
    """

    train_data_dfs = [X_train.iloc[i:i + sequence_length] for i in range(0, len(X_train), sequence_length)]
    train_label_df = y_train
    val_data_dfs = [X_val.iloc[i:i + sequence_length] for i in range(0, len(X_val), sequence_length)]
    val_label_df = y_val
    test_data_dfs = [X_test.iloc[i:i + sequence_length] for i in range(0, len(X_test), sequence_length)]
    test_label_df = y_test

    transformer_app(train_data_dfs, train_label_df, val_data_dfs, val_label_df, test_data_dfs, test_label_df)