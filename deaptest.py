import random

import numpy
from deap import creator, base, tools, algorithms


# def ver1():
#     creator.create("FitnessMax", base.Fitness, weights=(1.0, 1.0))
#     creator.create("Individual", list, fitness=creator.FitnessMax)
#
#     toolbox = base.Toolbox()
#
#     INT_MIN, INT_MAX = 5, 10
#     FLT_MIN, FLT_MAX = -0.2, 0.8
#     N_CYCLES = 4
#
#     toolbox.register("attr_int", random.randint, INT_MIN, INT_MAX)
#     toolbox.register("attr_flt", random.uniform, FLT_MIN, FLT_MAX)
#     toolbox.register("individual", tools.initCycle, creator.Individual,
#                      (toolbox.attr_int, toolbox.attr_flt), n=N_CYCLES)
#
#     print(toolbox.individual())
#
#
# def ver2():
#     creator.create("FitnessMax", base.Fitness, weights=(1.0,))
#     creator.create("Individual", list, fitness=creator.FitnessMax)
#
#     IND_SIZE=10
#
#     toolbox = base.Toolbox()
#     toolbox.register("attr_float", random.random)
#     toolbox.register("individual", tools.initRepeat, creator.Individual,
#                      toolbox.attr_float, n=IND_SIZE)
#
#     print(toolbox.individual())


def eval_one_max(individual):
    return sum(individual),


IND_SIZE = 4


def main():
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("evaluate", eval_one_max)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("attribute", random.random)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, n=IND_SIZE)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    pop = toolbox.population(n=1000)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=100, stats=stats, halloffame=hof, verbose=True)

    print(pop)
    print(log)
    # print(toolbox.individual())


main()
