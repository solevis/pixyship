# Layout a ship using a GA

import random
import operator
import array

import numpy
import sys
from deap import creator, base, tools, algorithms, gp

import pixstar

# Target layout
ship = pixstar.Ship(pixstar.ship_layout)
POP_SIZE = 2000
GENERATIONS = 100
IND_SIZE = 2 * 25


def eval_sum(ind):
    return sum(ind),


def eval_layout(ind):
    ship.reset()
    for i in range(0, len(ind), 2):
        try:
            ship.place_room_at([3, 2], ind[i], ind[i + 1])
        except IndexError:
            pass
        except pixstar.OutOfRoomException:
            pass

    return ship.area(),


def do_ga():
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)

    toolbox = base.Toolbox()
    toolbox.register("evaluate", eval_layout)
    # toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mate", tools.cxOnePoint)
    # toolbox.register("mate", tools.cxMessyOnePoint)
    # toolbox.register("mate", tools.cxUniform, indpb=.5)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("attr_float", random.random)
    toolbox.register("attr_int", random.randint, 0, max(ship.height, ship.width))
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=IND_SIZE)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.decorate("mate", gp.staticLimit(key=len, max_value=100))

    pop = toolbox.population(n=POP_SIZE)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=GENERATIONS, stats=stats, halloffame=hof,
                                   verbose=True)

    print(log)
    print(hof[0])
    eval_layout(hof[0])
    ship.print()


if __name__ == '__main__':
    seed = random.randrange(sys.maxsize)
    print('Seed:', seed)
    random.seed(seed)

    do_ga()
