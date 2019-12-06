import tensorflow.keras as K
import tensorflow as tf
import numpy as np
import pickle

np.random.seed(1)
tf.random.set_seed(1)

def get_model():
    NUM_FEATURES = 100 + 340 + 34 # From policy.py
    NUM_ACTIONS = 100
    X = K.layers.Input(shape=(NUM_FEATURES,), name='input')

    # Pull slices out from flattened feature vector
    action = K.layers.Lambda(lambda x: x[:, 0:100], output_shape=(100), name='action')(X)
    hand = K.layers.Lambda(lambda x: x[:, 100:440], output_shape=(340, 1), name='hand')(X)
    hand = K.layers.Reshape((340, 1))(hand)
    table = K.layers.Lambda(lambda x: x[:, 440:440+34], output_shape=(34), name='table')(X)

    action = K.layers.Dense(16, activation='relu')(action)
    hand = K.layers.Conv1D(16, kernel_size=(34,), strides=34, activation='relu')(hand)
    hand = K.layers.Flatten()(hand)
    hand = K.layers.Dense(16, activation='relu')(hand)
    table = K.layers.Dense(16, activation='relu')(table)

    added = K.layers.Concatenate()([action, hand, table])
    fc = K.layers.Dense(50, activation='relu')(added)
    fc = K.layers.Dense(50, activation='sigmoid')(fc) # Estimate Q value of taking S in A
    fc = K.layers.Dense(10, activation='sigmoid')(fc)
    fc = K.layers.Dense(1)(fc)

    out = fc

    model = K.models.Model(inputs=X, outputs=out)
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=[])
    # model.summary() # DEBUG
    return model
