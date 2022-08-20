from audioop import minmax
from faulthandler import disable
import random
import subprocess
import os, sys
import csv, json
import time
import numpy as np
from deap import base, creator, tools, algorithms
from ga_config import NIND, NGEN, POP, CXPB, MUTPB, GAME_LEVEL, GAME_TIME, DROP_INTERVAL

GAME_CNT = 0

def make_csv(individual, file_name = 'individual.csv'):
    with open(file_name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(individual)

def execute_tetris_game():
    #random_seed = int(time.time() * 100000000)
    random_seed = 1
    cmd = 'python3' + ' ' + 'start_gen.py' \
        + ' ' + '--game_level' + ' ' + str(GAME_LEVEL) \
        + ' ' + '--game_time' + ' ' + str(GAME_TIME) \
        + ' ' + '--drop_interval' + ' ' + str(DROP_INTERVAL)\
        + ' ' + '--random_seed' + ' ' + str(random_seed)

    disable_print()
    ret = subprocess.run(cmd, shell=True)
    if ret.returncode != 0:
        print('error: subprocess failed.', file=sys.stderr)
        sys.exit(1)
    enable_print()

def get_result():
    result_json_file = open('result.json', 'r')
    result = json.load(result_json_file)
    return result['judge_info']['score']
    
def eval_ind(individual):
    global GAME_CNT
    make_csv(individual)
    execute_tetris_game()
    GAME_CNT += 1
    #print("###### Genetic Alogithm #####")
    #print("GEN: ", GAME_CNT // NIND, " / ", NGEN, ", IND: ", GAME_CNT % NIND, " / ", NIND)
    return get_result(),

def disable_print():
    sys.stdout = open(os.devnull, 'w')

def enable_print():
    sys.stdout = sys.__stdout__

def start():
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("attribute", random.uniform, -10,10)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, NIND)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("select", tools.selTournament, tournsize=5)
    toolbox.register("mate", tools.cxBlend,alpha=0.2)
    mu_list = []
    for i in range(NIND):
        mu_list.append(0.0)
    sigma_list = []
    for i in range(NIND):
        sigma_list.append(20.0)
    toolbox.register("mutate", tools.mutGaussian, mu=mu_list, sigma=sigma_list, indpb=0.2)
    toolbox.register("evaluate", eval_ind)

    random.seed(int(time.time() * 100000000))

    pop = toolbox.population(n=POP)
    for individual in pop:
        individual.fitness.values = toolbox.evaluate(individual)
    hof = tools.ParetoFront()

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, stats = stats, halloffame=hof)

    #get best individual from last generations
    best_ind = tools.selBest(pop, 1)[0]
    best_value = best_ind.fitness.values
    #search best individual from all generations
    for ind in hof:
        if ind.fitness.values > best_value:
            best_ind = ind

    print("The best individual is %s and then, the fitness value is %s" % (best_ind, best_ind.fitness.values))
    make_csv(best_ind)

if __name__ == '__main__':
    start()