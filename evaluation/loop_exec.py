#!/usr/bin/python3
# -*- coding: utf-8 -*-
#pip install pandas
#pip install pyQt5
#pip install openpyxl

import sys
import os
import subprocess
from argparse import ArgumentParser
# from pygit2 import Repository
import pandas as pd

def get_option(game_level, game_time, mode, random_seed, drop_interval, resultlogjson, train_yaml, predict_weight, user_name, ShapeListMax, BlockNumMax, art_config_filepath):
    argparser = ArgumentParser()
    argparser.add_argument('-l', '--game_level', type=int,
                            default=game_level,
                            help='Specify game level')
    argparser.add_argument('-t', '--game_time', type=int,
                            default=game_time,
                            help='Specify game time(s), if specify -1, do endless loop')
    argparser.add_argument('-m', '--mode', type=str,
                            default=mode,
                            help='Specify mode (keyboard/gamepad/sample/art/train/predict/train_sample/predict_sample/train_sample2/predict_sample2) if necessary')
    argparser.add_argument('-r', '--random_seed', type=int,
                            default=random_seed,
                            help='Specify random seed if necessary') 
    argparser.add_argument('-d', '--drop_interval', type=int,
                            default=drop_interval,
                            help='Specify drop interval (msec) if necessary') 
    argparser.add_argument('-f', '--resultlogjson', type=str,
                            default=resultlogjson,
                            help='Specigy result log file path if necessary')
    argparser.add_argument('--train_yaml', type=str,
                            default=train_yaml,
                            help='yaml file for machine learning')
    argparser.add_argument('--predict_weight', type=str,
                            default=predict_weight,
                            help='weight file for machine learning')
    argparser.add_argument('-u', '--user_name', type=str,
                            default=user_name,
                            help='Specigy user name if necessary')
    argparser.add_argument('--ShapeListMax', type=int,
                            default=ShapeListMax,
                            help='Specigy ShapeListMax if necessary')
    argparser.add_argument('--BlockNumMax', type=int,
                            default=BlockNumMax,
                            help='Specigy BlockNumMax if necessary')
    argparser.add_argument('--art_config_filepath', type=str,
                           default=art_config_filepath,
                           help='art_config file path')
    return argparser.parse_args()

def get_python_cmd():
    ret = subprocess.run("python --version", shell=True, \
                         stderr=subprocess.PIPE, encoding="utf-8")
    print(ret)
    if "not found" in ret.stderr:
        return "python3"
    if "Python 2" in ret.stderr:
        return "python3"
    return "python"

def read_option_from_excel():
    # os.chdir('C:/Users/yuich/Source/tetris/evaluation')
    excel_file_name = './evaluation/loop_exec_option.xlsx'
    excel_sheet_name = 'list'
    df = pd.read_excel(excel_file_name, sheet_name=excel_sheet_name)
    return(df)

def exec_cmd(cmd):
    print('cmd : '+cmd)
    try:
        subprocess.run(cmd, shell=True)
    except:
        print('ERROR:'+cmd)
    # if ret.returncode != 0:
    #     print('error: subprocess failed.', file=sys.stderr)
    #     sys.exit(1)

def start():
    ## define
    EXEC_LOG_ON = 1    
    ## default value
    GAME_LEVEL = 1
    GAME_TIME = 180
    IS_MODE = "default"
    IS_SAMPLE_CONTROLL = "n"
    INPUT_RANDOM_SEED = -1
    INPUT_DROP_INTERVAL = -1
    DROP_INTERVAL = 1000          # drop interval
    RESULT_LOG_JSON = "result.json"
    USER_NAME = "window_sample"
    SHAPE_LIST_MAX = 6
    BLOCK_NUM_MAX = -1
    TRAIN_YAML = "config/default.yaml"
    PREDICT_WEIGHT = "outputs/latest/best_weight.pt"
    ART_CONFIG = "default.json"
    # branch_list=['master','master_seigot','ish05h3']

    # set current directory .git
    # repo = Repository('.git')
    df = read_option_from_excel()
    # for branch_name in branch_list:
    for num in range(len(df)):
        branch_name = df.at[num,'branch_name']
        GAME_LEVEL = df.at[num,'GAME_LEVEL']
        GAME_TIME = df.at[num,'GAME_TIME']
        IS_MODE = df.at[num,'IS_MODE']
        INPUT_RANDOM_SEED = df.at[num,'INPUT_RANDOM_SEED']
        DROP_INTERVAL = df.at[num,'DROP_INTERVAL']
        # RESULT_LOG_JSON = df.at[num,'RESULT_LOG_JSON']
        USER_NAME = df.at[num,'USER_NAME']
        SHAPE_LIST_MAX = df.at[num,'SHAPE_LIST_MAX']
        BLOCK_NUM_MAX = df.at[num,'BLOCK_NUM_MAX']
        TRAIN_YAML = df.at[num,'TRAIN_YAML']
        PREDICT_WEIGHT = df.at[num,'PREDICT_WEIGHT']
        REPOSITORY = df.at[num,'REPOSITORY']
        # branch = repo.lookup_branch(branch_name)
        # ref = repo.lookup_reference(branch.name)
        # repo.checkout(ref)
        # print('branch=',Repository('.').head.shorthand)

        cmd = 'git remote remove eva'
        exec_cmd(cmd)
        cmd = 'git remote add eva ' + REPOSITORY
        exec_cmd(cmd)
        cmd = 'git fetch eva'
        exec_cmd(cmd)
        # cmd = 'git checkout eva/'+branch_name+' ./game_manager/block_controller.py'
        # exec_cmd(cmd)
        # cmd = 'git checkout eva/'+branch_name+' ./game_manager/lib_tetris_isshy.py'
        # exec_cmd(cmd)
        # cmd = 'git checkout eva/'+branch_name+' ./game_manager/machine_learning'
        # exec_cmd(cmd)
        cmd = 'git checkout eva/'+branch_name+' ./game_manager'
        exec_cmd(cmd)

        ## set field parameter for level 1
        # RANDOM_SEED = 0            # random seed for field
        # OBSTACLE_HEIGHT = 0        # obstacle height (blocks)
        # OBSTACLE_PROBABILITY = 0   # obstacle probability (percent)

        # for GAME_LEVEL in [1,2,3]:
        # if GAME_LEVEL==1:
        #     RANDOM_SEED = 0
        #     BLOCK_NUM_MAX = 180
        #     # seed_max = 1
        #     # DROP_INTERVAL = 1        # drop interval
        # elif GAME_LEVEL==2:
        #     RANDOM_SEED = -1
        #     BLOCK_NUM_MAX = 180
        #     # seed_max = 1
        #     # DROP_INTERVAL = 1        # drop interval
        # elif GAME_LEVEL==3:
        #     # GAME_TIME = 30
        #     BLOCK_NUM_MAX = -1
        #     # seed_max = 1
        #     DROP_INTERVAL = 1         # drop interval
        # for num in range(1,seed_max+1,1):
        result_name = USER_NAME+'_'\
                    +branch_name.replace('/','-').replace('_','-')\
                    +"_"+IS_MODE.replace('_','')\
                    +"_"+f'{GAME_LEVEL:1}'\
                    +"_"+f'{GAME_TIME:03}'\
                    +"_"+f'{BLOCK_NUM_MAX:04}'\
                    +"_"+f'{DROP_INTERVAL:03}'\
                    +"_"+f'{INPUT_RANDOM_SEED:+05}'\
                    +"_"+f'{num+1:03}'
        ## update value if args are given
        args = get_option(GAME_LEVEL,
                        GAME_TIME,
                        IS_MODE,
                        INPUT_RANDOM_SEED,
                        INPUT_DROP_INTERVAL,
                        '', # RESULT_LOG_JSON
                        TRAIN_YAML,
                        PREDICT_WEIGHT,
                        USER_NAME,
                        SHAPE_LIST_MAX,
                        BLOCK_NUM_MAX,
                        ART_CONFIG)
        if args.game_level >= 0:
            GAME_LEVEL = args.game_level
        if args.game_time >= 0 or args.game_time == -1:
            GAME_TIME = args.game_time
        if args.mode in ("keyboard", "gamepad", "sample", "art", "train", "predict", "train_sample", "predict_sample", "train_sample2", "predict_sample2"):
            IS_MODE = args.mode
        if args.random_seed >= 0:
            INPUT_RANDOM_SEED = args.random_seed
        if args.drop_interval > 0:
            INPUT_DROP_INTERVAL = args.drop_interval
        if len(args.resultlogjson) != 0:
            RESULT_LOG_JSON = args.resultlogjson
        else:
            # RESULT_LOG_JSON = "result/"+Repository('.').head.shorthand\
            RESULT_LOG_JSON = 'result/'+result_name+'.json'
        if len(args.user_name) != 0:
            USER_NAME = args.user_name
        if args.ShapeListMax > 1:
            SHAPE_LIST_MAX = args.ShapeListMax
        if args.BlockNumMax > 1:
            BLOCK_NUM_MAX = args.BlockNumMax
        if len(args.train_yaml) != 0:
            TRAIN_YAML = args.train_yaml
        if args.predict_weight != None:
            PREDICT_WEIGHT = args.predict_weight
        if len(args.art_config_filepath) != 0:
            ART_CONFIG = args.art_config_filepath

        ## set field parameter for level 1
        RANDOM_SEED = 0            # random seed for field
        OBSTACLE_HEIGHT = 0        # obstacle height (blocks)
        OBSTACLE_PROBABILITY = 0   # obstacle probability (percent)

        ## update field parameter level
        if GAME_LEVEL == 0:   # level0
            GAME_TIME = -1
        elif GAME_LEVEL == 1: # level1
            RANDOM_SEED = 0
            BLOCK_NUM_MAX = 180
        elif GAME_LEVEL == 2: # level2
            RANDOM_SEED = -1
            BLOCK_NUM_MAX = 180
        elif GAME_LEVEL == 3 or GAME_LEVEL == 4: # level3 or level4
            RANDOM_SEED = -1
            BLOCK_NUM_MAX = 180
            OBSTACLE_HEIGHT = 10
            OBSTACLE_PROBABILITY = 40
            if GAME_LEVEL == 4:
                BLOCK_NUM_MAX = -1
                DROP_INTERVAL = 1
        else:
            print('invalid level: ' + str(GAME_LEVEL), file=sys.stderr)
            sys.exit(1)

        ## update random seed
        if GAME_LEVEL != 1:
            if INPUT_RANDOM_SEED >= 0:
                RANDOM_SEED = INPUT_RANDOM_SEED
        ## update drop interval
        if INPUT_DROP_INTERVAL > 0:
            DROP_INTERVAL = INPUT_DROP_INTERVAL

        ## print
        print('branch:' + branch_name)
        print('game_level: ' + str(GAME_LEVEL))
        print('game_time: ' + str(GAME_TIME))
        print('DROP_INTERVAL: ' + str(DROP_INTERVAL))
        print('RANDOM_SEED: ' + str(RANDOM_SEED))
        print('IS_MODE :' + str(IS_MODE))
        print('OBSTACLE_HEIGHT: ' + str(OBSTACLE_HEIGHT))
        print('OBSTACLE_PROBABILITY: ' + str(OBSTACLE_PROBABILITY))
        print('USER_NAME: ' + str(USER_NAME))
        print('SHAPE_LIST_MAX: ' + str(SHAPE_LIST_MAX))
        print('BLOCK_NUM_MAX: ' + str(BLOCK_NUM_MAX))
        print('RESULT_LOG_JSON: ' + str(RESULT_LOG_JSON))
        print('TRAIN_YAML: ' + str(TRAIN_YAML))
        print('PREDICT_WEIGHT: ' + str(PREDICT_WEIGHT))
        print('ART_CONFIG: ' + str(ART_CONFIG))

        os.makedirs('result', exist_ok=True)
        ## start game
        PYTHON_CMD = get_python_cmd()
        cmd = PYTHON_CMD + ' ' + 'game_manager/game_manager.py' \
            + ' ' + '--game_time' + ' ' + str(GAME_TIME) \
            + ' ' + '--seed' + ' ' + str(RANDOM_SEED) \
            + ' ' + '--obstacle_height' + ' ' + str(OBSTACLE_HEIGHT) \
            + ' ' + '--obstacle_probability' + ' ' + str(OBSTACLE_PROBABILITY) \
            + ' ' + '--drop_interval' + ' ' + str(DROP_INTERVAL) \
            + ' ' + '--mode' + ' ' + str(IS_MODE) \
            + ' ' + '--user_name' + ' ' + str(USER_NAME) \
            + ' ' + '--resultlogjson' + ' ' + str(RESULT_LOG_JSON) \
            + ' ' + '--train_yaml' + ' ' + str(TRAIN_YAML) \
            + ' ' + '--predict_weight' + ' ' + str(PREDICT_WEIGHT) \
            + ' ' + '--ShapeListMax' + ' ' + str(SHAPE_LIST_MAX) \
            + ' ' + '--BlockNumMax' + ' ' + str(BLOCK_NUM_MAX) \
            + ' ' + '--art_config_filepath' + ' ' + str(ART_CONFIG)

        if EXEC_LOG_ON==1:
            # EXEC_LOG = "result/"+Repository('.').head.shorthand\
            EXEC_LOG = "result/"+result_name+".log"
            cmd = cmd + ' ' + '>'+EXEC_LOG

        os.makedirs('./result', exist_ok=True)
        # print(cmd)
        exec_cmd(cmd)


        #p = subprocess.Popen(cmd, shell=True)
        #try:
        #    p.wait()
        #except KeyboardInterrupt:
        #    print("KeyboardInterrupt, call p.terminate()")
        #    p.terminate()

    cmd = 'git checkout HEAD ./game_manager'
    exec_cmd(cmd)

    cmd = 'git remote remove eva'
    exec_cmd(cmd)

    cmd = PYTHON_CMD + ' ' + 'evaluation/read_result.py'
    exec_cmd(cmd)

if __name__ == '__main__':
    start()