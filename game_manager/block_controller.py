#!/usr/bin/python3
# -*- coding: utf-8 -*-
from enum import Enum
import csv
import os
from heapq import heapify, heappush, heappushpop, nlargest
#import logging
from copy import copy

#logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(asctime)s: %(message)s')
#logging.basicConfig(level=logging.WARNING, format='%(levelname)s %(asctime)s: %(message)s')

class Mode(Enum):
    NORMAL = 1
    ATTACK = 2
    DEFENCE = 3

#class Board_Data:
    #def __init__(self, board, height, width):
        #self.board : list[int] = board
        #self.height = height
        #self.width = width
        #self.peaks : list[int]
        #self.maxY : int 
    
    #def get_peaks(self):

class Block_Controller(object):

    def __init__(self):
        # init parameter
        self.ind = self.getIndividual(csv_file = 
            os.path.dirname(os.path.abspath(__file__)) + "/genetic_algorithm/individual.csv")
        #logging.debug('self.ind:{}'.format(self.ind))
        self.beam_width = 10
        self.estimate_num = 5
        self.hold = False
        self.xmin_max_tuple = (
            ((0,0),), #Shape None
            ((0,10),(2,9),), # Shape I
            ((0,9),(1,9),(1,10),(1,9),), # Shape L
            ((1,10),(1,9),(0,9),(1,9),), # Shape J
            ((0,9),(1,9),(1,10),(1,9),), # Shape T
            ((0,9),), # Shape O
            ((1,9),(0,9),), # Shape S
            ((1,9),(0,9),),# Shape Z
        )
        self.shape_coord = (
            (((0, 0), (0, 0), (0, 0), (0, 0),),),
            (((0, -1), (0, 0), (0, 1), (0, 2),), ((-2, 0), (-1, 0), (0, 0), (1, 0),),),
            (((0, -1), (0, 0), (0, 1), (1, 1),),((-1, 0), (0, 0), (1, 0), (-1, 1),),((-1, -1), (0, -1), (0, 0), (0, 1),),((1, -1), (-1, 0), (0, 0), (1, 0),),),
            (((0, -1), (0, 0), (0, 1), (-1, 1),),((-1, -1), (-1, 0), (0, 0), (1, 0),),((0, -1), (1, -1), (0, 0), (0, 1),),((-1, 0), (0, 0), (1, 0), (1, 1),),),
            (((0, -1), (0, 0), (0, 1), (1, 0),),((0, 1), (-1, 0), (0, 0), (1, 0),),((0, -1), (-1, 0), (0, 0), (0, 1),),((0, -1), (-1, 0), (0, 0), (1, 0),),),
            (((0, -1), (1, -1), (0, 0),(1, 0),),),
            (((0, -1), (1, -1), (-1, 0), (0, 0),),((0, -1), (0, 0), (1, 0), (1, 1),),),
            (((-1, -1), (0, -1), (0, 0), (1, 0),),((1, -1), (0, 0), (1, 0), (0, 1),),)
        )
        self.shape_coord_for_drop = (
            (((0, 0), (0, 0), (0, 0), (0, 0),),),
            (((0, 2),), ((-2, 0), (-1, 0), (0, 0), (1, 0),),),
            (((0, 1), (1, 1),),((0, 0), (1, 0), (-1, 1),),((-1, -1), (0, 1),),((-1, 0), (0, 0), (1, 0),),),
            (((0, 1), (-1, 1),),((-1, 0), (0, 0), (1, 0),),((1, -1), (0, 1),),((-1, 0), (0, 0), (1, 1),),),
            (((0, 1), (1, 0),),((0, 1), (-1, 0), (1, 0),),((-1, 0), (0, 1),),((-1, 0), (0, 0), (1, 0),),),
            (((0, 0),(1, 0),),),
            (((1, -1), (-1, 0), (0, 0),),((0, 0), (1, 1),),),
            (((-1, -1), (0, 0), (1, 0),),((1, 0), (0, 1),),)
        )
        self.shape_height = (
            (0,),
            (1,0,),
            (1,0,1,1,),
            (1,1,1,0,),
            (1,0,1,1,),
            (1,),
            (1,1,),
            (1,1,)
        )

        self.board_width = 10
        self.board_height = 22
        self.ShapeNone_index = 0

    # GetNextMove is main function.
    # input
    #    nextMove : nextMove structure which is empty.
    #    GameStatus : block/field/judge/debug information. 
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : nextMove structure which includes next shape position and the other.
    def GetNextMove(self, nextMove, GameStatus):

        #start_time = time()

        ## Get data from GameStatus
        # current shape info
        CurrentShapeClass = GameStatus["block_info"]["currentShape"]["class"]
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        #logging.debug('CurrentShapeClass: {}, DirectionRange:{}'.format(CurrentShapeClass.shape, CurrentShapeDirectionRange))
        # next shape info
        ShapeListDirectionRange = []
        ShapeListClass = []
        for i in range(1,6):
            ElementNo = "element" + str(i)
            ShapeListClass.append(GameStatus["block_info"]["nextShapeList"][ElementNo]["class"])
            ShapeListDirectionRange.append(GameStatus["block_info"]["nextShapeList"][ElementNo]["direction_range"])
            #logging.debug('ShapeListClass {}:{}'.format(ElementNo, GameStatus["block_info"]["nextShapeList"][ElementNo]["class"].shape))
        # hold shape info
        HoldShapeClass = GameStatus["block_info"]["holdShape"]["class"]
        HoldShapeDirectionRange = GameStatus["block_info"]["holdShape"]["direction_range"]
        #logging.debug('HoldShapeClass: {}'.format(HoldShapeClass))

        # current board info
        self.board_backboard = GameStatus["field_info"]["backboard"]

        # Decide mode
        self.mode = self.decideMode(self.board_backboard)

        strategy_candidate = []
        heapify(strategy_candidate)

        #Search current shape
        self.beamSearch(self.board_backboard, CurrentShapeClass, 
                         CurrentShapeDirectionRange, strategy_candidate)
        
        #Search hold shape
        if self.hold:
            self.beamSearch(self.board_backboard, HoldShapeClass, 
                             HoldShapeDirectionRange, strategy_candidate, hold=True)

        #Search next shape
        #for i in range(self.estimate_num):
            #strategy_candidate_tmp = []
            #heapify(strategy_candidate_tmp)
            #for pre_eval,_, pre_strategy, pre_board in strategy_candidate:
                #self.beamSearch(pre_board, ShapeListClass[i], ShapeListDirectionRange[i], strategy_candidate_tmp,
                                #pre_strategy=pre_strategy, pre_EvalValuse=pre_eval)
            #strategy_candidate = pickle_copy(strategy_candidate_tmp)

        max_strategy = nlargest(1, strategy_candidate)
        strategy = max_strategy[0][2]

        #logging.debug('Mode: {}'.format(self.mode))
        #logging.debug('Search time: {}'.format(time() - start_time))
        nextMove["strategy"]["direction"] = strategy[0]
        nextMove["strategy"]["x"] = strategy[1]
        nextMove["strategy"]["y_operation"] = strategy[2]
        nextMove["strategy"]["y_moveblocknum"] = strategy[3]
        if self.hold:
            nextMove["strategy"]["use_hold_function"] = strategy[4]
        else:
            nextMove["strategy"]["use_hold_function"] = "y"
            self.hold = True

        return nextMove

    def beamSearch(self, board, ShapeClass, DirectionRange, strategy_candidate, 
        hold = False, pre_strategy = None, pre_EvalValuse = None):
        id = 0
        shape_xmin_max = self.xmin_max_tuple[ShapeClass.shape]
        for direction in DirectionRange:
            # search with x range
            xMin, xMax = shape_xmin_max[direction]
            for x in range(xMin, xMax):
                # get board data, as if dropdown block
                dropdown_board, dy= self.getDropDownBoard(board, ShapeClass, direction, x)
                # evaluate board
                EvalValue, dropdown_board = self.calcEvaluationValue(dropdown_board, ShapeClass, self.mode)
                if not pre_EvalValuse == None:
                    EvalValue += pre_EvalValuse
                # make strategy
                if not pre_strategy == None:
                    strategy = pre_strategy
                else:
                    if hold:
                        strategy = (direction, x, 1, 1, 'y')
                    else:
                        strategy = (direction, x, 1, 1, 'n')
                # update candidate
                if len(strategy_candidate) < self.beam_width:
                    heappush(strategy_candidate, (EvalValue, id, strategy, dropdown_board))
                else:
                    heappushpop(strategy_candidate, (EvalValue, id, strategy, dropdown_board))
                id += 1

    def getIndividual(self, csv_file = "individual.csv"):
        with open(csv_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            individual = list()
            for row in reader:
                if reader.line_num == 2:
                    individual = [float(col) for col in row]
                    break
            return individual

    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        return [(x + xx, y + yy) for xx, yy in self.shape_coord[Shape_class.shape][direction]]

    def getShapeCoordArray_for_drop(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        return [(x + xx, y + yy) for xx, yy in self.shape_coord_for_drop[Shape_class.shape][direction]]

    def getDropDownBoard(self, board_backboard, Shape_class, direction, x):
        # 
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.
        board = copy(board_backboard)
        board, dy = self.dropDown(board, Shape_class, direction, x)
        return board, dy

    def dropDown(self, board, Shape_class, direction, x):
        # 
        # internal function of getBoard.
        # -- drop down the shape on the board.
        # 
        height = self.board_height
        width = self.board_width
        dy = height - 1
        coordArray = self.getShapeCoordArray_for_drop(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < height and (_yy + _y < 0 or board[(_y + _yy)*width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        board = self.dropDownWithDy(board, Shape_class, direction, x, dy)
        return board, dy

    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, dy)
        for _x, _y in coordArray:
            board[_y*self.board_width + _x] = Shape_class.shape
        return board
    
    def removeFullLines(self, board, height, width, maxY):
        newBoard = [0] * width * height
        newY = height - 1
        fullLines = 0
        for y in range(height - 1, height - maxY -1, -1):
            blockCount = sum([1 if board[y*width + x] > 0 else 0 for x in range(width)])
            if blockCount == width:
                fullLines += 1
            elif blockCount == 0:
                pass
            else:
                #for x in range(width):
                    #newBoard[newY * width + x] = board[y * width + x]
                newBoard[newY * width : (newY + 1) * width] = board[y * width : (y + 1) * width]
                newY -= 1
        return newBoard, fullLines
    
    def decideMode(self, board):
        mode = Mode.DEFENCE
        width = self.board_width
        height = self.board_height

        peaks = self.get_peaks(board, height, width)
        maxY = max(peaks)
        holes = self.get_holes(board, peaks)
        n_holes = sum(holes)
        wells = self.get_wells(width, peaks)
        wells_sorted = sorted(wells)
        second_well = wells_sorted[-2]
        if second_well < 5 and maxY < 15 and n_holes < 4:
            mode = Mode.NORMAL
        #if second_well < 5 and maxY < 12 and n_holes < 4:
            #mode = Mode.ATTACK
        #print("mode:", mode)
        return mode

    def calcEvaluationValue(self, board, ShapeListClass, mode = Mode.ATTACK):
        # calc Evaluation Value

        width = self.board_width
        height = self.board_height
        #before remove full lines
        peaks_before = self.get_peaks(board, height, width)
        maxY_right = peaks_before[-1]
        maxY = max(peaks_before)

        #after remove full lines
        board, fullLines = self.removeFullLines(board, height, width, maxY)
        peaks_tmp = [peak - fullLines for peak in peaks_before]
        #peaks = self.get_peaks(board, height, width, maxY)
        peaks = self.get_peaks_tmp(board, height, width, peaks_tmp)
        nPeaks = sum(peaks)
        maxY = max(peaks)
        holes = self.get_holes(board, peaks)
        nHoles = sum(holes)
        total_col_with_hole = self.get_total_cols_with_hole(width, holes)
        x_transitions = self.get_x_transitions(board, maxY)
        y_transitions = self.get_y_transitions(board, peaks)
        total_dy = self.get_total_dy(width, peaks)
        wells = self.get_wells(width, peaks)
        maxWell = max(wells)
        total_none_cols = self.get_total_none_cols(width, peaks)
        #dy_right = peaks[-2] - peaks[-1]

        #20220810-2
        if fullLines < 3:
            fullLines = 0

        #logging.debug('nPeaks: {}, nHoles: {}, total_col_with_hole: {}, total_dy: {}, x_transitions: {}, y_transitions: {}, total_none_cols: {}, maxWell: {}, fullLines: {} '
                    #.format(nPeaks, nHoles, total_col_with_hole, total_dy,
                    #x_transitions, y_transitions, total_none_cols, maxWell, fullLines))

        eval_list = [nPeaks, nHoles, total_col_with_hole, total_dy, x_transitions, y_transitions, total_none_cols, maxWell, fullLines]
        
        score = sum([x * y for (x,y) in zip(self.ind, eval_list)])

        if mode == Mode.NORMAL and fullLines < 3:
            score -= 1000 * maxY_right
        
        if fullLines == 4:
            score += 10000

        return score, board
    
    def get_peaks(self, board, height, width, maxY=None):
        if not maxY == None:
            start_height = maxY
        else:
            start_height = height - 1
        peaks = [0] * width
        for x in range(width):
            for y in range(start_height, 0, -1):
                if board[(height - y) * width + x] != 0:
                    peaks[x] = y
                    break
        return peaks

    def get_peaks_tmp(self, board, height, width, peaks_before = None):
        peaks = [0] * width
        for x in range(width):
            for y in range(peaks_before[x], 0, -1):
                if board[(height - y) * width + x] != 0:
                    peaks[x] = y
                    break
        return peaks

    def get_holes(self, board, peaks):
        holes= []
        for x in range(self.board_width):
            start_y = peaks[x] - 1
            if start_y <= 0:
                holes.append(0)
            else:
                hole = 0
                for y in range(start_y, 0, -1):
                    if board[(self.board_height - y) * self.board_width + x] == 0:
                        hole += 1
                holes.append(hole)
        return holes
    
    def get_total_cols_with_hole(self, width, holes):
        return sum([1 if holes[x] else 0 for x in range(width)])
    
    def get_x_transitions(self, board, maxY):
        height = self.board_height
        width = self.board_width
        transitions = 0
        for y in range(height - maxY, height):
            for x in range(1, width):
                if board[y * width + x] != board[y * width + x-1]:
                    transitions += 1
        return transitions
    
    def get_y_transitions(self, board, peaks):
        height = self.board_height
        width = self.board_width
        transitions = 0
        for x in range(width):
            for y in range(height - peaks[x], height -1):
                if board[width * y + x] != board[width* (y+1) + x]:
                    transitions += 1
        return transitions
    
    def get_total_dy(self, width, peaks):
        total_dy = 0
        for x in range(width-1):
            total_dy += abs(peaks[x+1] - peaks[x])
        return total_dy
    
    def get_wells(self, width, peaks):
        wells = []
        for x in range(width):
            if x == 0:
                well = peaks[1] - peaks[0]
                well = well if well > 0 else 0
                wells.append(well)
            elif x == len(peaks) - 1:
                well = peaks[-2] - peaks[-1]
                well = well if well > 0 else 0
                wells.append(well)
            else:
                w1 = peaks[x - 1] - peaks[x]
                w2 = peaks[x + 1] - peaks[x]
                w1 = w1 if w1 > 0 else 0
                w2 = w2 if w2 > 0 else 0
                well = w1 if w1 >= w2 else w2
                wells.append(well)
        return wells
    
    def get_total_none_cols(self, width, peaks):
        #return sum([1 if peaks[x] else 0 for x in range(self.board_width)])
        return sum([1 if peaks[x] else 0 for x in range(width)])
    
    def show_board(self, board):
        for y in range(self.board_height):
            tmpstr=''
            for x in range(self.board_width):
                tmpstr = tmpstr + str(board[y*self.board_width+x]) + ' '
            print(format(x,'02d'),tmpstr)
        print('-- 0 1 2 3 4 5 6 7 8 9 --' )

BLOCK_CONTROLLER = Block_Controller()

## Test
if __name__ == '__main__':
    import yaml
    config_file = "test_config/board_data.yaml"

    with open(config_file, "r") as yml:
        config = yaml.safe_load(yml)
        backboard = list()
        for board in config["backboard"]:
            backboard.extend(board)

    from board_manager import Shape   
    shapeclass = Shape(1)

    block_controller = Block_Controller()

    block_controller.show_board(backboard)
    _, backboard = block_controller.calcEvaluationValue(backboard, shapeclass)
    block_controller.show_board(backboard)