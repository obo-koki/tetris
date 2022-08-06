import random
import subprocess
import sys
import csv
import json
from unicodedata import name
from deap import base, creator, tools, algorithms
from ga_config import NIND, NGEN, POP, CXPB, MUTPB, GAME_LEVEL, GAME_TIME, DROP_INTERVAL

def make_csv(individual, file_name = 'individual.csv'):
    with open(file_name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(individual)

def execute_tetris_game():
    cmd = 'python3' + ' ' + 'start.py' \
        + ' ' + '--game_level' + ' ' + str(GAME_LEVEL) \
        + ' ' + '--game_time' + ' ' + str(GAME_TIME) \
        + ' ' + '--drop_interval' + ' ' + str(DROP_INTERVAL)

    ret = subprocess.run(cmd, shell=True)
    if ret.returncode != 0:
        print('error: subprocess failed.', file=sys.stderr)
        sys.exit(1)

def get_result():
    result_json_file = open('result.json', 'r')
    result = json.load(result_json_file)
    return result['judge_info']['score']
    
def start():
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    def obfunc(individual):
        make_csv(individual)
        execute_tetris_game()
        return get_result(),

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
    toolbox.register("evaluate", obfunc)

    random.seed(64)

    pop = toolbox.population(n=POP)
    for individual in pop:
        individual.fitness.values = toolbox.evaluate(individual)
    hof = tools.ParetoFront()

    algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, halloffame=hof)

    best_ind = tools.selBest(pop, 1)[0]
    print("The best individual is %s and then, the fitness value is %s" % (best_ind, best_ind.fitness.values))
    make_csv(best_ind)
    execute_tetris_game()
    print(get_result())

if __name__ == '__main__':
    start()