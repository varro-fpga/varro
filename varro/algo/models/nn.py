"""
This module contains classes for defining each type of model.
"""

import os
import numpy as np
from datetime import datetime
from keras.callbacks import TensorBoard

from varro.algo.models import Model
from varro.algo.problems import Problem
from varro.misc.variables import ABS_ALGO_TENSORBOARD_PATH


class ModelNN(Model):
    def __init__(self, problem):
        """Neural network architecture wrapper class specific to a problem

        Args:
            problem (str): String specifying the type of problem we're dealing with

        """
        from keras.layers import Dense, BatchNormalization
        from keras.models import Sequential
        # Suppress Tensorflow / Keras warnings
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

        self.model = Sequential()
        if problem.approx_type == Problem.CLASSIFICATION:
            self.model.add(Dense(3, input_dim=problem.input_dim, activation='sigmoid'))
            self.model.add(Dense(2, activation='sigmoid'))

            # LAST LAYER:
            # Problem-specific - if y is [0, 1], use sigmoid
            self.model.add(Dense(problem.output_dim, activation='sigmoid'))

        elif problem.approx_type == Problem.REGRESSION:
            self.model.add(Dense(3, input_dim=problem.input_dim, activation='sigmoid'))
            self.model.add(Dense(3, activation='sigmoid'))
            self.model.add(Dense(2, activation='sigmoid'))

            # LAST LAYER:
            # Problem-specific - if y is [-1, 1], use tanh
            self.model.add(Dense(problem.output_dim, activation='tanh'))
        else:
            raise ValueError('Unknown approximation type ' + str(problem.approx_type))

        # Set up tensorboard to logs
        self.tensorboard = TensorBoard(log_dir="{}/{}".format(ABS_ALGO_TENSORBOARD_PATH,
                                                              datetime.now().strftime("%b-%d-%Y-%H:%M:%S")))

        # Set the number of parameters we can change in the architecture
        self.num_parameters_alterable = np.sum([np.prod(layer.shape) for layer in self.model.get_weights()])

    def load_parameters(self, parameters):
        """Loads an array of parameters into this model.

        Args:
            parameters (np.ndarray of floats): The new values for the parameters
                - e.g. [0.93, 0.85, 0.24, ..., 0.19]

        """
        # Pull out the numbers from the individual and
        # load them as the shape from the model's parameters
        ind_idx = 0
        new_parameters = []
        for idx, layer in enumerate(self.model.get_weights()):
            # Number of parameters we'll take from the individual for this layer
            num_parameters_taken = np.prod(layer.shape)
            new_parameters.append(parameters[ind_idx:ind_idx+num_parameters_taken].reshape(layer.shape))
            ind_idx += num_parameters_taken

        # Set Weights using individual
        self.model.set_weights(new_parameters)

    def predict(self, X, problem=None):
        """Evaluates the model on given data."""
        return self.model.predict(X, callbacks=[self.tensorboard])

    @property
    def parameters_shape(self):
        return self.num_parameters_alterable
