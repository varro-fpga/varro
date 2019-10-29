"""
This module contains a function that returns training set for functions to approximate
"""

import random
import numpy as np

from varro.algo.problems import Problem


def rastrigin(x):
    """Rastrigin function

    Args:
        x (list): Input list

    Returns:
        Outputs of the rastrigin function given the inputs
    """
    x = np.asarray_chkfinite(x)
    n = len(x)
    return 10*n + np.sum(x**2 - 10 * np.cos( 2 * np.pi * x))

def rosenbrock(x):
    """Rosenbrock function

    Args:
        x (list): Input list

    Returns:
        Outputs of the rosenbrock function given the inputs
    """
    x = np.asarray_chkfinite(x)
    x0 = x[:-1]
    x1 = x[1:]
    return (np.sum( (1 - x0) **2 ) + 100 * np.sum( (x1 - x0**2) **2 ))

class ProblemFuncApprox(Problem):
    def __init__(self, func):
        # Set seed
        random.seed(100)

        # Choose classification or regression
        self._approx_type = Problem.REGRESSION
        self._name = func
        self._input_dim = 1
        self._output_dim = 1

        def sample_float(start, end, step):
            self.minimum = start
            self.maximum = end
            return random.sample(list(np.arange(start, end, step)), k=500)

        def sample_int(start, end):
            self.minimum = start
            self.maximum = end
            return np.random.randint(start, end + 1, size=500)

        # Get the function to approximate
        if func == 'sinx':
            self.X_train = sample_float(-2*np.pi, 2*np.pi, 0.001)
            self.y_train = np.sin(self.X_train)
        elif func == 'cosx':
            self.X_train = sample_float(-2*np.pi, 2*np.pi, 0.001)
            self.y_train = np.cos(self.X_train)
        elif func == 'tanx':
            self.X_train = sample_float(-2*np.pi, 2*np.pi, 0.001)
            self.y_train = np.tan(self.X_train)
        elif func == 'x':
            self.X_train = sample_float(-10, 10, 0.001)
            self.y_train = self.X_train
        elif func == 'ras':
            self.X_train = sample_float(-5.12, 5.12, 0.01)
            self.y_train = rastrigin(self.X_train)
        elif func == 'rosen':
            self.X_train = sample_float(-10, 10, 0.001)
            self.y_train = rosenbrock(self.X_train)
        elif func == 'step':
            self.X_train = sample_float(-10, 10, 0.001)
            self.y_train = (np.array(self.X_train) > 0).astype(float)
            self._approx_type = Problem.CLASSIFICATION
        elif func == 'simple_step':
            self.X_train = sample_int(0, 1)
            self.y_train = self.X_train
            self._approx_type = Problem.CLASSIFICATION
        else:
            raise ValueError('Problem \'' + str(func) + '\' not recognised')
