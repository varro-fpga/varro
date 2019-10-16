"""
This module implements an evolutionary strategies algorithm.
"""

from algo.util import get_args, mkdir
from algo.nn_mnist import evaluate_nn_mnist

import os
import logging
from pathlib import Path
import numpy as np
import random
import functools
from tqdm import tqdm
from deap import base, creator, tools
from functools import partial
# from array import array # Use this if speed is an issue


#################
# MAIN FUNCTION #
#################
def main():

    # Initialize logger
    logger = logging.getLogger(__name__)

    # Get the Arguments parsed from file execution
    args = get_args()

    toolbox = init(args.isize)

    logger.info('Start Evolution ...')
    evolve(toolbox=toolbox,
           crossover_prob=args.cxpb,
           mutation_prob=args.mutpb,
           num_generations=args.ngen)


##################
# INITIALIZATION #
##################
def init(individual_size):
    """Initializes the algorithm.

    Args:
        individual_size (int): Size of an individual in the population (array length)

    Returns:
        toolbox (deap.base.Toolbox): Initialized DEAP Toolbox for the algorithm.

    """
    # Set seed
    random.seed(100)

    # Define a Class called FitnessMin to
    # define the fitness objective 
    # for the Selection of individuals
    # to become offspring
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

    # Define a Class called Individual to inherit from
    # array and has a fitness attribute
    # = creator.FitnessMin
    creator.create("Individual", np.ndarray, fitness=creator.FitnessMin)

    # Initialzie Toolbox
    toolbox = base.Toolbox()

    # Define an attribute variable
    toolbox.register("attribute", random.random)

    # Define an individual that has 
    toolbox.register("individual", 
                     tools.initRepeat, 
                     creator.Individual,
                     toolbox.attribute, 
                     n=individual_size)

    # Define a population of individuals
    toolbox.register("population", 
                     tools.initRepeat, 
                     list, 
                     toolbox.individual)

    # Defines a mating function that takes in 
    # 2 tuples (2 individuals) and performs 2 point cross over
    toolbox.register("mate", 
                     tools.cxTwoPoint)

    # Defines a mutation function that takes in
    # a single tuple (an individual) and for each
    # entry in the tuple, we have a different probability
    # of mutation given by indpb, and parameters for
    # how much to mutate each entry by, using a gaussian
    # distribution
    toolbox.register("mutate", 
                     tools.mutGaussian, 
                     mu=0, 
                     sigma=1, 
                     indpb=0.1)
                     
    # Defines the selection method for the mating
    # pool / offspring 
    toolbox.register("select", 
                     tools.selTournament, 
                     tournsize=3)
                     
    # Defines the evaluation function
    # we will use for calculating the fitness of
    # an individual
    toolbox.register("evaluate", 
                     evaluate_nn_mnist)

    return toolbox


def evolve(toolbox, crossover_prob, mutation_prob, num_generations):
    """Evolves weights of neural network to train classifier for MNIST
    
    Args:
        crossover_prob (float): Crossover probability from 0-1
        mutation_prob (float): Mutation probability from 0-1
        num_generations (int): Number of generations to run algorithm
    
    Returns:
        pop: Population of the fittest individuals so far
        avg_fitness_scores: A list of the average fitness scores for each generation

    """

    # Create Logs folder if not created
    mkdir('./algo/logs/')

    # Set Logging configuration
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='./algo/logs/evolve_mnist.log',
                        level=logging.INFO,
                        format=log_fmt)

    # Get logger
    logger = logging.getLogger(__name__)

    # Initialize random population
    pop = toolbox.population(n=100)
    
    # Track the Average fitness scores
    avg_fitness_scores = []

    # Evaluate the entire population
    fitnesses = map(toolbox.evaluate, pop)
    avg_fitness_scores.append(np.mean([fitness_score for fitness in fitnesses for fitness_score in fitness]))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    # Iterate for generations
    for g in tqdm(range(num_generations)):
        
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover on the offspring by
        # choosing alternate offsprings
        # e.g. if pop = [ind1, ind2, ind3, ind4],
        # we are doing 2-point crossover between
        # ind1, ind3 and ind2, ind4
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < crossover_prob:
                
                # Crossover
                toolbox.mate(child1, child2)
                
                # Delete fitness values after crossover
                # because the individuals are changed
                # and will have different fitness values
                del child1.fitness.values
                del child2.fitness.values

        # Apply mutation on the offspring
        for mutant in offspring:
            if random.random() < mutation_prob:
                
                # Mutate
                toolbox.mutate(mutant)
                
                # Delete fitness values after crossover
                # because the individuals are changed
                # and will have different fitness values
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        # (These are the individuals that have been mutated
        # or the offspring after crossover with fitness deleted)
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        # Compute Average fitness score of generation
        valid_ind = [ind for ind in offspring if ind.fitness.valid]
        avg_fitness_score = np.mean([fitness_score \
                                        for fitness in list(fitnesses) + list(map(toolbox.evaluate, valid_ind)) \
                                        for fitness_score in fitness])
        avg_fitness_scores.append(avg_fitness_score)
        logger.info('Generation {} Avg. Fitness Score: {}'.format(g, avg_fitness_score))
        
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        
        
    return pop, avg_fitness_scores

if __name__ == "__main__":

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    main()
