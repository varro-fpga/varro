"""
This module contains the class for Multi-objective Genetic Algorithm
-> Individuals that perform well on multiple objectives are benefitted
"""

import os
import pickle
import numpy as np
import random
from deap import base, creator, tools
from collections import namedtuple

from varro.algo.strategies.strategy import Strategy
from varro.algo.strategies.sga import StrategySGA
from varro.algo.strategies.ns_es import StrategyNSES


OBJECTIVES = ['rmse', 'mae', 'wasserstein']

class StrategyMOGA(StrategySGA):
    def __init__(self, **kwargs):
        super().__init__(self, name='moga', **kwargs)

        # Set Objectives (Fitness scores) to optimize over
        self.objectives = OBJECTIVES

    @staticmethod
    def init_fitness_and_inds(objectives=OBJECTIVES):
        """Initializes the fitness and definition of individuals"""

        class Fitness(base.Fitness):
            def __init__(self):
                super().__init__()
                self.__fitness_scores = None

            @property
            def fitness_scores(self):
                return self.values

            @fitness_scores.setter
            def fitness_scores(self, fitness_scores):
                self.__fitness_scores = fitness_scores
                if fitness_scores:
                    # WARNING:
                    # Setting values breaks alot of things:
                    # self.__fitness_scores is reset to None
                    # after setting values, so you should only
                    # set values after all the scores you require are set
                    self.values = fitness_scores

            @fitness_scores.deleter
            def fitness_scores(self):
                if hasattr(self, '__fitness_scores'):
                    del self.__fitness_scores

            def delValues(self):
                super().delValues()
                if hasattr(self, '__fitness_scores'):
                    del self.__fitness_scores

        creator.create("FitnessMulti", Fitness, weights=tuple(-1.0 for _ in objectives)) # Weights for each objective
        creator.create("Individual", np.ndarray, fitness=creator.FitnessMulti)


    def load_es_vars(self):
        """Loads the evolutionary strategy variables from checkpoint given after
        creating the fitness and individual templates for DEAP evolution or initializes them
        """
        super().load_es_vars()

        # If we have a multiobjective strategy,
        # we also need to keep the Pareto Fronts
        self.paretofront = cp["paretofront"] if self.ckpt else tools.ParetoFront(similar=np.array_equal)


    def compute_fitness(self, pop):
        """Calculates the fitness scores for the entire Population

        Args:
            pop (list): An iterable of Individual(np.ndarrays) that represent the individuals

        Returns:
            Number of individuals with invalid fitness scores we updated
        """
        # Evaluate the individuals with an invalid fitness or if we are at the start
        # of the evolutionary algo, AKA curr_gen == 0
        # (These are the individuals that have not been evaluated before -
        # individuals at the start of the evolutionary algorithm - or those
        # that have been mutated / the offspring after crossover with fitness deleted)
        invalid_inds = [ind for ind in pop if not ind.fitness.valid or self.curr_gen == 0]

        # Get fitness score for each individual with
        # invalid fitness score in population
        for ind in invalid_inds:

            # Load Weights into model using individual
            self.model.load_parameters(ind)

            # Calculate the Fitness score of the individual
            ind.fitness.fitness_scores = tuple(self.fitness_score(reg_metric=objective) for objective in self.objectives)

        return len(invalid_inds)


    def evaluate(self, pop):
        """Evaluates an entire population on a dataset on the neural net / fpga
        architecture specified by the model, and calculates the fitness scores for
        each individual, sorting the entire population by fitness scores in-place

        Args:
            pop (list): An iterable of np.ndarrays that represent the individuals

        Returns:
            Average fitness score of population

        """
        # Re-generates the training set for the problem (if possible) to prevent overfitting
        self.problem.reset_train_set()

        # Compute all fitness for population
        num_invalid_inds = self.compute_fitness(pop)

        # The population is entirely replaced by the
        # evaluated offspring
        self.pop[:] = pop

        # Update population statistics
        self.halloffame.update(self.pop)
        self.paretofront.update(self.pop)
        # record = self.stats.compile(self.pop)
        # self.logbook.record(gen=self.curr_gen, evals=num_invalid_inds, **record)

        return np.mean([ind.fitness.fitness_scores[0] for ind in pop])
