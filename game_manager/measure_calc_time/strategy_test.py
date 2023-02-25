import yaml
import time
import sys
from os.path import dirname, abspath

parent_dir = dirname(dirname(abspath(__file__)))
sys.path.append(parent_dir)
print(parent_dir)

from board_manager import BOARD_DATA, Shape
from game_manager import Game_Manager

from block_controller import BLOCK_CONTROLLER as BLOCK_CONTROLLER_BASE
#from block_controller_sample import BLOCK_CONTROLLER_SAMPLE as BLOCK_CONTROLLER_BASE

from argparse import ArgumentParser


def get_option(
    mode,
    random_seed,
    drop_interval,
    resultlogjson,
    train_yaml,
    predict_weight,
    user_name,
    ShapeListMax,
    BlockNumMax,
    art_config_filepath,
    backboard,
):
    argparser = ArgumentParser()

    argparser.add_argument(
        "-b",
        "--backboard",
        type=str,
        default=backboard,
        help="Specify mode () if necessary",
    )

    argparser.add_argument(
        "-m",
        "--mode",
        type=str,
        default=mode,
        help="Specify mode (keyboard/gamepad/sample/art/train/predict/train_sample/predict_sample/train_sample2/predict_sample2) if necessary",
    )
    argparser.add_argument(
        "-r",
        "--random_seed",
        type=int,
        default=random_seed,
        help="Specify random seed if necessary",
    )
    argparser.add_argument(
        "-d",
        "--drop_interval",
        type=int,
        default=drop_interval,
        help="Specify drop interval (msec) if necessary",
    )
    argparser.add_argument(
        "-f",
        "--resultlogjson",
        type=str,
        default=resultlogjson,
        help="Specigy result log file path if necessary",
    )
    argparser.add_argument(
        "--train_yaml",
        type=str,
        default=train_yaml,
        help="yaml file for machine learning",
    )
    argparser.add_argument(
        "--predict_weight",
        type=str,
        default=predict_weight,
        help="weight file for machine learning",
    )
    argparser.add_argument(
        "-u",
        "--user_name",
        type=str,
        default=user_name,
        help="Specigy user name if necessary",
    )
    argparser.add_argument(
        "--ShapeListMax",
        type=int,
        default=ShapeListMax,
        help="Specigy ShapeListMax if necessary",
    )
    argparser.add_argument(
        "--BlockNumMax",
        type=int,
        default=BlockNumMax,
        help="Specigy BlockNumMax if necessary",
    )
    argparser.add_argument(
        "--art_config_filepath",
        type=str,
        default=art_config_filepath,
        help="art_config file path",
    )
    return argparser.parse_args()


def get_arg():
    BACKBOAD_DATA = "backboard_data.yaml"
    ## default value
    IS_MODE = "default"
    IS_SAMPLE_CONTROLL = "n"
    INPUT_RANDOM_SEED = -1
    INPUT_DROP_INTERVAL = -1
    DROP_INTERVAL = 1000  # drop interval
    RESULT_LOG_JSON = "result.json"
    USER_NAME = "window_sample"
    SHAPE_LIST_MAX = 6
    BLOCK_NUM_MAX = -1
    TRAIN_YAML = "config/default.yaml"
    PREDICT_WEIGHT = "outputs/latest/best_weight.pt"
    ART_CONFIG = "default.json"

    ## update value if args are given
    return get_option(
        IS_MODE,
        INPUT_RANDOM_SEED,
        INPUT_DROP_INTERVAL,
        RESULT_LOG_JSON,
        TRAIN_YAML,
        PREDICT_WEIGHT,
        USER_NAME,
        SHAPE_LIST_MAX,
        BLOCK_NUM_MAX,
        ART_CONFIG,
        BACKBOAD_DATA,
    )


###############################################
# ゲーム情報の取得
###############################################
def getGameStatus(board_info, block_info):
    # return current Board status.
    # define status data.
    status = {
        "field_info": {
            "width": "none",
            "height": "none",
            "backboard": "none",
            "withblock": "none",  # back board with current block
        },
        "block_info": {
            "currentX": "none",
            "currentY": "none",
            "currentDirection": "none",
            "currentShape": {
                "class": "none",
                "index": "none",
                "direction_range": "none",
            },
            "nextShape": {
                "class": "none",
                "index": "none",
                "direction_range": "none",
            },
            "nextShapeList": {},
            "holdShape": {
                "class": "none",
                "index": "none",
                "direction_range": "none",
            },
        },
        "judge_info": {
            "elapsed_time": "none",
            "game_time": "none",
            "gameover_count": "none",
            "score": "none",
            "line": "none",
            "block_index": "none",
            "block_num_max": "none",
            "mode": "none",
        },
        "debug_info": {
            "dropdownscore": "none",
            "linescore": "none",
            "line_score": {
                "line1": "none",
                "line2": "none",
                "line3": "none",
                "line4": "none",
                "gameover": "none",
            },
            "shape_info": {
                "shapeNone": {
                    "index": "none",
                    "color": "none",
                },
                "shapeI": {
                    "index": "none",
                    "color": "none",
                },
                "shapeL": {
                    "index": "none",
                    "color": "none",
                },
                "shapeJ": {
                    "index": "none",
                    "color": "none",
                },
                "shapeT": {
                    "index": "none",
                    "color": "none",
                },
                "shapeO": {
                    "index": "none",
                    "color": "none",
                },
                "shapeS": {
                    "index": "none",
                    "color": "none",
                },
                "shapeZ": {
                    "index": "none",
                    "color": "none",
                },
            },
            "line_score_stat": "none",
            "shape_info_stat": "none",
            "random_seed": "none",
            "obstacle_height": "none",
            "obstacle_probability": "none",
        },
    }
    # update status
    ## board
    status["field_info"]["width"] = BOARD_DATA.width
    status["field_info"]["height"] = BOARD_DATA.height
    status["field_info"]["backboard"] = board_info
    status["field_info"]["withblock"] = board_info
    ## shape
    status["block_info"]["currentX"] = -1
    status["block_info"]["currentY"] = -1
    status["block_info"]["currentDirection"] = 0
    ### current shape
    currentShapeClass, currentShapeIdx, currentShapeRange = BOARD_DATA.getShapeData(
        block_info[0]
    )
    status["block_info"]["currentShape"]["class"] = currentShapeClass
    status["block_info"]["currentShape"]["index"] = currentShapeIdx
    status["block_info"]["currentShape"]["direction_range"] = currentShapeRange
    ### next shape
    nextShapeClass, nextShapeIdx, nextShapeRange = BOARD_DATA.getShapeData(
        block_info[1]
    )
    status["block_info"]["nextShape"]["class"] = nextShapeClass
    status["block_info"]["nextShape"]["index"] = nextShapeIdx
    status["block_info"]["nextShape"]["direction_range"] = nextShapeRange
    ### next shape list
    for i in range(BOARD_DATA.getShapeListLength()):
        ElementNo = "element" + str(i)
        ShapeClass, ShapeIdx, ShapeRange = BOARD_DATA.getShapeData(block_info[i])
        status["block_info"]["nextShapeList"][ElementNo] = {
            "class": ShapeClass,
            "index": ShapeIdx,
            "direction_range": ShapeRange,
        }
    ### hold shape
    holdShapeClass, holdShapeIdx, holdShapeRange = BOARD_DATA.getholdShapeData()
    status["block_info"]["holdShape"]["class"] = holdShapeClass
    status["block_info"]["holdShape"]["index"] = holdShapeIdx
    status["block_info"]["holdShape"]["direction_range"] = holdShapeRange
    ### next shape
    ## judge_info
    status["judge_info"]["elapsed_time"] = 0
    status["judge_info"]["game_time"] = 0
    status["judge_info"]["gameover_count"] = 0
    status["judge_info"]["score"] = 0
    status["judge_info"]["line"] = 0
    status["judge_info"]["block_index"] = 0
    status["judge_info"]["block_num_max"] = 0
    status["judge_info"]["mode"] = 0
    ## debug_info
    status["debug_info"]["dropdownscore"] = 0
    status["debug_info"]["linescore"] = 0
    status["debug_info"]["line_score_stat"] = 0
    status["debug_info"]["shape_info_stat"] = 0
    status["debug_info"]["line_score"]["line1"] = Game_Manager.LINE_SCORE_1
    status["debug_info"]["line_score"]["line2"] = Game_Manager.LINE_SCORE_2
    status["debug_info"]["line_score"]["line3"] = Game_Manager.LINE_SCORE_3
    status["debug_info"]["line_score"]["line4"] = Game_Manager.LINE_SCORE_4
    status["debug_info"]["line_score"]["gameover"] = Game_Manager.GAMEOVER_SCORE
    status["debug_info"]["shape_info"]["shapeNone"]["index"] = Shape.shapeNone
    status["debug_info"]["shape_info"]["shapeI"]["index"] = Shape.shapeI
    status["debug_info"]["shape_info"]["shapeI"]["color"] = "red"
    status["debug_info"]["shape_info"]["shapeL"]["index"] = Shape.shapeL
    status["debug_info"]["shape_info"]["shapeL"]["color"] = "green"
    status["debug_info"]["shape_info"]["shapeJ"]["index"] = Shape.shapeJ
    status["debug_info"]["shape_info"]["shapeJ"]["color"] = "purple"
    status["debug_info"]["shape_info"]["shapeT"]["index"] = Shape.shapeT
    status["debug_info"]["shape_info"]["shapeT"]["color"] = "gold"
    status["debug_info"]["shape_info"]["shapeO"]["index"] = Shape.shapeO
    status["debug_info"]["shape_info"]["shapeO"]["color"] = "pink"
    status["debug_info"]["shape_info"]["shapeS"]["index"] = Shape.shapeS
    status["debug_info"]["shape_info"]["shapeS"]["color"] = "blue"
    status["debug_info"]["shape_info"]["shapeZ"]["index"] = Shape.shapeZ
    status["debug_info"]["shape_info"]["shapeZ"]["color"] = "yellow"
    status["debug_info"]["random_seed"] = 0
    status["debug_info"]["obstacle_height"] = 0
    status["debug_info"]["obstacle_probability"] = 0
    if currentShapeIdx == Shape.shapeNone:
        print("warning: current shape is none !!!")

    return status


def main():
    args = get_arg()

    print(args)

    with open(args.backboard, "r") as yml:
        config = yaml.safe_load(yml)
        backboard = list()
        for board in config["backboard"]:
            backboard.extend(board)
        block = config["block_shape"]

    ##画面ボードと現テトリミノ情報をクリア
    BOARD_DATA.clear()
    BOARD_DATA.init_shape_parameter(len(block))
    ## 新しい予告テトリミノ配列作成
    BOARD_DATA.createNewPiece()

    nextMove = {
        "strategy": {
            "direction": "none",  # next shape direction ( 0 - 3 )
            "x": "none",  # next x position (range: 0 - (witdh-1) )
            "y_operation": "none",  # movedown or dropdown (0:movedown, 1:dropdown)
            "y_moveblocknum": "none",  # amount of next y movement
            "use_hold_function": "n",  # use hold function (y:yes, n:no)
        },
        "option": {
            "reset_callback_function_addr": None,
            "reset_all_field": None,
            "force_reset_field": None,
        },
    }
    game_status = getGameStatus(backboard, block)

    # 時間計測開始
    time_sta = time.perf_counter()

    BLOCK_CONTROLLER_BASE.GetNextMove(nextMove, game_status)

    # 時間計測終了
    time_end = time.perf_counter()
    # 経過時間（秒）
    calc_time = time_end - time_sta

    print(nextMove)
    print("Calc Time :", calc_time, "[S]")


if __name__ == "__main__":
    main()
