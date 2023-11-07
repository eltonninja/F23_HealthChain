import tensorflow as tf
from tensorflow.keras import layers, models

def build_transformer(input_shape, num_diseases, head_size, num_heads, ff_dim, num_transformer_blocks):
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


def transformer_app(train_sequences, train_labels, val_sequences, val_labels, test_sequences, test_labels):    

    train_data = tf.constant([df.values for df in train_sequences])
    val_data = tf.constant([df.values for df in val_sequences])
    test_data = tf.constant([df.values for df in test_sequences])

    train_dataset = tf.data.Dataset.from_tensor_slices((train_data, train_labels))
    val_dataset = tf.data.Dataset.from_tensor_slices((val_data, val_labels))
    test_dataset = tf.data.Dataset.from_tensor_slices((test_data, test_labels))

    batch_size = 32
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