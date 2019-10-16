"""
This module contains code for testing the evolutionary algorithm on a neural network.
"""

import numpy as np
from sklearn.metrics import mean_squared_error
import keras 
from keras.layers import Dense, Activation
from keras.models import Sequential


def evaluate_nn_function_approx(individual, function=np.sin):
    """Loads an individual (list) as the weights of neural net and computes the
    Mean Squared Error of the neural net with the given weights and provided
    approximating function
    
    Args:
        individual: An individual (represented by list of floats) 
            - e.g. [0.93, 0.85, 0.24, ..., 0.19], ...}
        function: Function to be approximated by neural net
    
    Returns:
        An np.ndarray of the fitness score(s) of the individual

    """
    # Basic Neural net model
    model = Sequential() 
    model.add(Dense(1, input_dim=1, activation='relu'))
    model.add(Dense(3, activation='relu'))
    model.add(Dense(2, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    
    # Training set of examples for the neural net to test on 
    # 500 random integers from -1000 to 1000
    training_set = np.random.randint(-1000, 1000, 500) 
    y_true = np.array(list(map(function, training_set)))
    
    def load_weights(individual, model):
        """Reshapes individual as weights of the neural net architecture
        prespecified

        Args:
            individual: An individual (represented by an np.ndarray of floats) 
                - e.g. [0.93, 0.85, 0.24, ..., 0.19], ...}

            function: Reshapes individuals to weights of a neural net

        Returns:
            An np.ndarray of the fitness score(s) of the individual
                - e.g. [Mean Squared Error]
        """

        # Pull out the numbers from the individual and
        # load them as the shape from the model's weights
        ind_idx = 0
        new_weights = []
        for idx, x in enumerate(model.get_weights()):
            if idx % 2:
                new_weights.append(x)
            else: 
                num_weights_taken = x.shape[0]*x.shape[1]
                new_weights.append(individual[ind_idx:ind_idx+num_weights_taken].reshape(x.shape))
                ind_idx += num_weights_taken
        
        # Set Weights using individual
        model.set_weights(new_weights)
        y_pred = np.array(model.predict(training_set))

        # Get the mean squared error of the 
        # individual
        mse = np.square(y_true - y_pred).mean()
               
        return np.array([mse])

    return load_weights(individual, model)
