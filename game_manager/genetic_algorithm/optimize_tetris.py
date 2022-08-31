import random
import subprocess
import os, sys
import csv, json
import time
import datetime
import numpy as np
from deap import base, creator, tools, algorithms
from ga_config import NIND, NGEN, POP, CXPB, MUTPB, GAME_LEVEL, GAME_TIME, DROP_INTERVAL
import matplotlib.pyplot as plt

GAME_CNT = 0
GEN = 0
SEED = 0

row_name = ["nPeaks", "nHoles", "total_col_with_hole", "total_dy",
            "x_transitions", "y_transitions", "total_none_cols", "maxWell", "fullLines"]
param_name = ["NIND", "NGEN", "POP", "CXPB", "MUTPB", "GAME_LEVEL"]
param_list = [NIND, NGEN, POP, CXPB, MUTPB, GAME_LEVEL]

def make_graph(list1, list2):
    x1 = [i for i in range(len(list1))]
    x2 = [i for i in range(len(list2))]

    fig = plt.figure()
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.plot(x1, list1, marker="o", color="red", linestyle="--")
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.plot(x2, list2, marker="o", color="blue", linestyle="--")
    plt.show()

def make_ind_csv(individual, file_name = 'individual.csv'):
    global row_name, param_name, param_list
    with open(file_name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(row_name)
        writer.writerow(individual)
        writer.writerow(param_name)
        writer.writerow(param_list)

def make_pop_csv(pop, file_name = 'last_population.csv'):
    global row_name
    with open(file_name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(row_name)
        for ind in pop:
            writer.writerow(ind)

def make_process_csv(means, stds, file_name = 'process.csv'):
    with open(file_name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["mean", "std"])
        for mean, std in zip(means, stds):
            writer.writerow([mean, std])

def execute_tetris_game(random_seed):
    cmd = 'python3' + ' ' + 'start_gen.py' \
        + ' ' + '--game_level' + ' ' + str(GAME_LEVEL) \
        + ' ' + '--game_time' + ' ' + str(GAME_TIME) \
        + ' ' + '--drop_interval' + ' ' + str(DROP_INTERVAL)\
        + ' ' + '--random_seed' + ' ' + str(random_seed)\
        + ' ' + '--BlockNumMax' + ' ' + '180'
    ret = subprocess.run(cmd, shell=True)
    if ret.returncode != 0:
        print('error: subprocess failed.', file=sys.stderr)
        sys.exit(1)

def get_result():
    result_json_file = open('result.json', 'r')
    result = json.load(result_json_file)
    return result['judge_info']['score']
    
def eval_ind(individual):
    global GAME_CNT, GEN, SEED
    make_ind_csv(individual)
    execute_tetris_game(SEED)
    GAME_CNT += 1
    return get_result(),

def start():
    #Seed update
    random.seed(int(time.time() * 100000000))

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("attribute", random.uniform, -1,1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, NIND)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", eval_ind)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("mate", tools.cxBlend,alpha=0.2)
    mu_list = []
    for i in range(NIND):
        mu_list.append(0.0)
    sigma_list = []
    for i in range(NIND):
        sigma_list.append(20.0)
    toolbox.register("mutate", tools.mutGaussian, mu=mu_list, sigma=sigma_list, indpb=0.2)

    pop = toolbox.population(n=POP)
    print("Start of evolution")
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    print("  Evaluated %i individuals" % len(pop))
    fits = [ind.fitness.values[0] for ind in pop]
    means = []
    stds = []
    hof = tools.ParetoFront()

    length = len(pop)
    mean = sum(fits) / length
    sum2 = sum(x*x for x in fits)
    std = abs(sum2 / length - mean**2)**0.5
    means.append(mean)
    stds.append(std)

    generation = 0
    while generation < NGEN:
        generation += 1

        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        #Cross
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        #Mutation
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        #Evaluate
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        print("  Evaluated %i individuals" % len(invalid_ind))

        pop[:] = offspring
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5
        means.append(mean)
        stds.append(std)

        print("  Min %s" % min(fits))
        print("  Max %s" % max(fits))
        print("  Avg %s" % mean)
        print("  Std %s" % std)


    print("-- End of (successful) evolution --")

    #get best individual from last generations
    best_ind = tools.selBest(pop, 1)[0]
    best_value = best_ind.fitness.values
    #search best individual from all generations
    for ind in hof:
        if ind.fitness.values > best_value:
            best_ind = ind

    print("The best individual is %s and then, the fitness value is %s" % (best_ind, best_ind.fitness.values))

    now = datetime.datetime.now()
    make_ind_csv(best_ind)

    date = now.strftime('%Y%m%d%H%M%S')
    ind_file_name = "individual/individual_" + str(date) + ".csv"
    pop_file_name = "individual/last_population_" + str(date) + ".csv"
    process_file_name = "individual/process_" + str(date) + ".csv"
    make_ind_csv(best_ind, file_name=ind_file_name)
    make_pop_csv(pop, file_name=pop_file_name)
    make_process_csv(means, stds, file_name=process_file_name)
    make_graph(means, stds)

if __name__ == '__main__':
    start()