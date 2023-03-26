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
import multiprocessing
import pickle

GAME_CNT = 0
GEN = 0
SEED = 0
gen = 0

ROW_NAME = ["nPeaks", "nHoles", "total_col_with_hole", "total_dy",
            "x_transitions", "y_transitions", "total_none_cols", "maxWell", "fullLines"]
PARAM_NAME = ["NIND", "NGEN", "POP", "CXPB", "MUTPB", "GAME_LEVEL"]
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
    with open(file_name, 'w', newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(ROW_NAME)
        writer.writerow(individual)
        writer.writerow(PARAM_NAME)
        writer.writerow(param_list)

def execute_tetris_game(random_seed):
    cmd = 'python' + ' ' + 'start_for_gen.py' \
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
    global GAME_CNT, GEN, SEED, gen
    make_ind_csv(individual)
    execute_tetris_game(gen)
    result = get_result()
    execute_tetris_game(1000000-gen)
    result += get_result()
    GAME_CNT += 1
    #print("GAME_CNT: ",GAME_CNT)
    return result,

if __name__ == '__main__':
    args = sys.argv
    checkpoint_file = None
    if len(args) >= 2:
        checkpoint_file = args[1]

    #Seed update
    random.seed(int(time.time() * 100000000))

    #Define problem
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    #Multiprocessing module
    pool = multiprocessing.Pool()
    toolbox.register("map", pool.map)

    #Add operation to make individual
    toolbox.register("attribute", random.uniform, -1,1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attribute, NIND)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", eval_ind)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("mate", tools.cxBlend,alpha=0.2)
    mu_list = [0.0 for i in range(NIND)]
    sigma_list = [20.0 for i in range(NIND)]
    for i in range(NIND):
        sigma_list.append(20.0)
    toolbox.register("mutate", tools.mutGaussian, mu=mu_list, sigma=sigma_list, indpb=0.2)

    if checkpoint_file:
        #Copy past evolution data
        with open(checkpoint_file, "rb") as cp_file:
            try:
                cp = pickle.load(cp_file)
                print(cp)
            except Exception as e:
                print("pickle.load Error: ",e)
                sys.exit()
        pop = cp["population"]
        gen = cp["generation"]
        hof = cp["halloffame"]
        log = cp["logbook"]
        random.setstate(cp["rndstate"])
    else:
        #Start new evolution
        pop = toolbox.population(n=POP)
        gen = 0
        hof = tools.ParetoFront()
        log = tools.Logbook()

    print("Start of evolution")
    #Initial evaluation
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("max", np.max)
    stats.register("min", np.min)
    stats.register("avg", np.mean)
    stats.register("std", np.std)

    #Start genetic algorithm
    while gen < NGEN:
        gen += 1

        #Selection
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

        #Record log
        hof.update(pop)
        record = stats.compile(pop)
        log.record(gen=gen, evals=len(invalid_ind), **record)

        print("Gen:", gen, end=' ')
        print (record)

        pop[:] = offspring

    print("-- End of (successful) evolution --")

    #Get best individual from last generations
    best_ind = tools.selBest(pop, 1)[0]
    best_value = best_ind.fitness.values

    #Search best individual from all generations
    for ind in hof:
        if ind.fitness.values > best_value:
            best_ind = ind
    print("The best individual is %s and then, the fitness value is %s" % (best_ind, best_ind.fitness.values))

    #Get time string
    now = datetime.datetime.now()
    date = now.strftime('%Y%m%d%H%M%S')

    #Save individual
    ind_file_name = "individual/individual_" + str(date) + ".csv"
    make_ind_csv(best_ind)
    make_ind_csv(best_ind, file_name=ind_file_name)

    #Save optimize log
    checkpoint_file_name = "individual/check_point_" + str(date) + ".csv"
    with open("checkpoint_name.pkl", "wb") as cp_file:
        cp = dict(population=pop, generation=gen, halloffame=hof,
                    logbook=log, rndstate=random.getstate())
        pickle.dump(cp, cp_file)