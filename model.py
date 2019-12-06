import tensorflow.keras as K
import tensorflow as tf
import numpy as np
import pickle

np.random.seed(1)
tf.random.set_seed(1)

class Model:
    instance = None
    @staticmethod
    def get_model_instance():
        if Model.instance is None:
            Model.instance = Model.get_model()
        
        return Model.instance

    @staticmethod
    def get_model():
        NUM_ACTIONS = 100
        HAND_SIZE = 510
        DECK_SIZE = 34

        NUM_FEATURES = NUM_ACTIONS + HAND_SIZE + DECK_SIZE # From policy.py
        X = K.layers.Input(shape=(NUM_FEATURES,), name='input')

        # Pull slices out from flattened feature vector
        action = K.layers.Lambda(lambda x: x[:, 0:100], output_shape=(100,), name='action')(X)
        
        hand = K.layers.Lambda(lambda x: x[:, 100:610], output_shape=(610,), name='hand')(X)
        hand = K.layers.Reshape((510, 1))(hand)
        
        table = K.layers.Lambda(lambda x: x[:, 610:644], output_shape=(34,), name='table')(X)

        # TODO: more layers

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
