"""
This module contains a function that returns the training set for a given problem
"""


class Problem:
    CLASSIFICATION = 0
    REGRESSION = 1

    def __init__(self):
        """This class defines a problem & dataset for a model to solve."""
        self._input_dim = None
        self._output_dim = None
        self._approx_type = None

    def training_set(self):
        return None, None

    @property
    def approx_type(self):
        """Classification or Regression"""
        return self._approx_type

    @property
    def input_dim(self):
        """Dimension of input vector"""
        return self._input_dim

    @property
    def output_dim(self):
        """Dimension of output vector"""
        return self._output_dim
