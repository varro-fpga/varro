"""
This module contains the evolutionary algorithm logic
"""

from dowel import logger
import numpy as np
from deap import base, creator, tools
from datetime import datetime

from varro.algo.problems import Problem


def evolve(strategy,
           grid_search=False,
           ckpt_freq=10):
    """Evolves parameters to train a model on a dataset.

    Args:
        strategy (Strategy): The strategy to be used for evolving, Simple Genetic Algorithm (sga) / Novelty Search (ns) / Covariance-Matrix Adaptation (cma-es)
        grid_search (bool): Whether grid search will be in effect

    Returns:
        pop: Population of the fittest individuals so far
        avg_fitness_scores: A list of the average fitness scores for each generation
        fittest_ind_score: The Best Individual's fitness score

    """
    ########################################################
    # 1. SET UP LOGGER, FOLDERS, AND FILES TO SAVE DATA TO #
    ########################################################

    def process_record(record):
        now = datetime.utcnow()
        try:
            delta = now - process_record.now
        except AttributeError:
            delta = 0
        process_record.now = now
        return {'time_since_last': delta}

    logger.log('Starting Evolution ...')
    logger.log('strategy: {}'.format(strategy.name))
    logger.log('problem_type: {}'.format(strategy.problem.name))
    logger.log('cxpb: {}'.format(strategy.cxpb))
    logger.log('mutpb: {}'.format(strategy.mutpb))
    logger.log('popsize: {}'.format(strategy.popsize))
    logger.log('elitesize: {}'.format(strategy.elitesize))
    logger.log('ngen: {}'.format(strategy.ngen))
    logger.log('imutpb: {}'.format(strategy.imutpb))
    logger.log('imutmu: {}'.format(strategy.imutmu))
    logger.log('imutsigma: {}'.format(strategy.imutsigma))
    logger.log('halloffamesize: {}'.format(strategy.halloffamesize))
    logger.log('earlystop: {}'.format(strategy.earlystop))

    # Set additional logging information about experiment
    # if not simple genetic algorithm strategy
    if strategy.name == 'ns-es' or strategy.name == 'nsr-es':
        logger.log('novelty_metric: {}'.format(strategy.novelty_metric))

    ###############################
    # 2. CURRENT POPULATION STATS #
    ###############################
    # Track the Average fitness scores
    avg_fitness_scores = []

    # Evaluate the entire population
    logger.start_timer()
    avg_fitness_score = strategy.toolbox.evaluate(pop=strategy.pop)
    avg_fitness_scores.append(avg_fitness_score)
    logger.stop_timer('EVOLVE.PY strategy.toolbox.evaluate complete')

    #################################
    # 4. EVOLVE THROUGH GENERATIONS #
    #################################
    # Iterate for generations
    start_gen = strategy.curr_gen
    for g in range(start_gen, strategy.ngen):

        logger.start_timer()

        # Select the next generation individuals
        non_alterable, alterable = strategy.generate_offspring()

        logger.stop_timer('EVOLVE.PY Selecting the next generation of individuals')
        
        logger.start_timer()

        # Mate offspring
        strategy.mate(alterable)

        logger.stop_timer('EVOLVE.PY Mating offspring')
        logger.start_timer()

        # Mutate offspring
        strategy.mutate(alterable) 
        logger.stop_timer('EVOLVE.PY Mutating offspring')

        # Recombine Non-alterable offspring with the
        # ones that have been mutated / cross-overed
        offspring = non_alterable + alterable

        # Evaluate the entire population
        strategy.curr_gen = g # Set the current generation
        avg_fitness_score = strategy.toolbox.evaluate(pop=offspring)
        avg_fitness_scores.append(avg_fitness_score)


        # Save snapshot of population (offspring)
        if g % ckpt_freq == 0 or g == strategy.ngen-1:
            # Save the checkpoint
            strategy.save_ckpt()

        # Best individual's fitness / novelty score,
        # whichever is the first element of the fitness
        # values tuple because:
        # The hall of fame contains the best individual
        # that ever lived in the population during the
        # evolution. It is lexicographically sorted at all
        # time so that the first element of the hall of fame
        # is the individual that has the best first fitness value
        # ever seen, according to the weights provided to the fitness at creation time.
        if strategy.name == 'sga' or strategy.name == 'nsr-es':
            fittest_ind_score = strategy.halloffame[0].fitness.fitness_score
        elif strategy.name == 'ns-es':
            fittest_ind_score = strategy.halloffame[0].fitness.novelty_score
        elif strategy.name == 'moga':
            fittest_ind_score = strategy.halloffame[0].fitness.fitness_scores[0] # Gets the first objective
        else:
            raise NotImplementedError

        # Log Average score of population
        logger.log(('Generation {:0' + str(len(str(strategy.ngen-1))) + '} | Avg. Fitness Score: {:.5f} | Fittest Individual Score: {:.5f}')\
                        .format(g, avg_fitness_score, fittest_ind_score)) 

        # Early Stopping if average fitness
        # score is close to the minimum possible,
        # or if stuck at local optima (average fitness score
        # hasnt changed for past 10 rounds)
        if strategy.earlystop and (strategy.name == 'sga' or strategy.name == 'nsr-es'):
            if strategy.problem.approx_type == Problem.CLASSIFICATION:
                if round(-fittest_ind_score, 4) > 0.95:
                    logger.log('Early Stopping activated because Accuracy > 95%.')
                    break;
                if len(avg_fitness_scores) > 10 and len(set(avg_fitness_scores[-10:])) == 1:
                    logger.log('Early Stopping activated because fitness scores have converged.')
                    break;
            else:
                if round(fittest_ind_score, 4) < 0.01:
                    logger.log('Early Stopping activated because MSE < 0.01.')
                    break;
                if len(avg_fitness_scores) > 10 and len(set(avg_fitness_scores[-10:])) == 1:
                    logger.log('Early Stopping activated because fitness scores have converged.')
                    break;
    return strategy.pop, avg_fitness_scores, fittest_ind_score
