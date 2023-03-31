#!/usr/bin/python3
# -*- coding: utf-8 -*-
from enum import Enum
import csv
import os
from heapq import heapify, heappush, heappushpop, nlargest
from copy import copy
from time import time

class Mode(Enum):
    ATTACK_RIGHT = 1
    ATTACK_LEFT = 2
    NORMAL_RIGHT = 3
    NORMAL_LEFT = 4
    DEFENCE = 5
    
class Block_Controller(object):

    def __init__(self):
        #init param
        self.ind_normal = self.getIndividual(csv_file = 
            os.path.dirname(os.path.abspath(__file__)) + "/genetic_algorithm/individual_normal.csv")
        self.ind = self.ind_defence = self.getIndividual(csv_file = 
            os.path.dirname(os.path.abspath(__file__)) + "/genetic_algorithm/individual_defence.csv")
        self.board_width = 10
        self.board_height = 22
        self.ShapeNone_index = 0

        #board data
        self.board_initialized = False
        self.peaks_initialized = False
        self.board_backboard = [0] * self.board_width * (self.board_height + 3)
        self.board_sl = slice(0,self.board_width * self.board_height)
        self.peaks_sl = slice(self.board_width * self.board_height, self.board_width * (self.board_height + 1))
        self.holes_sl = slice(self.board_width * (self.board_height + 1), self.board_width * (self.board_height + 2))
        self.wells_sl = slice(self.board_width * (self.board_height + 2), self.board_width * (self.board_height + 3))

        #beam search param
        self.beam_width = 80
        self.estimate_num = 3

        #for hold function
        self.hold = False

        #look-up table for speed up
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
        self.shape_coord_for_peak = (
            (((0, 0), (0, 0), (0, 0), (0, 0),),), # Shape None
            (((0, -1),), ((-2, 0), (-1, 0), (0, 0), (1, 0),),), # Shape I
            (((0, -1), (1, 1),),((-1, 0), (0, 0), (1, 0),),((-1, -1), (0, -1),),((1, -1), (-1, 0), (0, 0),),), # Shape L
            (((0, -1), (-1, 1),),((-1, -1), (0, 0), (1, 0),),((0, -1), (1, -1),),((-1, 0), (0, 0), (1, 0),),), # Shape J
            (((0, -1), (1, 0),),((-1, 0), (0, 0), (1, 0),),((0, -1), (-1, 0),),((0, -1), (-1, 0), (1, 0),),), # Shape T
            (((0, -1), (1, -1),),), # Shape O
            (((0, -1), (1, -1), (-1, 0),),((0, -1), (1, 0),),), # Shape S
            (((-1, -1), (0, -1), (1, 0),),((1, -1), (0, 0),),) # Shape Z
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
        self.shape_height_abs = (
            (0,),
            (4,1,),
            (3,2,3,2,),
            (3,2,3,2,),
            (3,2,3,2,),
            (2,),
            (2,3,),
            (2,3,)
        )
        self.xMinMax_allow_ind_ATTACK_RIGHT = set([0]) # (shape -1) * 4 + range
        self.xMinMax_allow_ind_ATTACK_LEFT = set([0]) # (shape -1) * 4 + range
        self.xMinMax_allow_ind_NORMAL_RIGHT = set([0, 4, 10, 12]) # (shape -1) * 4 + range
        self.xMinMax_allow_ind_NORMAL_LEFT = set([0, 6, 8, 14]) # (shape -1) * 4 + range

    # GetNextMove is main function.
    def GetNextMove(self, nextMove, GameStatus):
        ## Get data from GameStatus
        # current shape info
        CurrentShapeClass = GameStatus["block_info"]["currentShape"]["class"]
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        # next shape info
        nextShapeList = GameStatus["block_info"]["nextShapeList"]
        ShapeListDirectionRange = [
            nextShapeList["element1"]["direction_range"],
            nextShapeList["element2"]["direction_range"],
            nextShapeList["element3"]["direction_range"],
            nextShapeList["element4"]["direction_range"],
            nextShapeList["element5"]["direction_range"]
        ]
        ShapeListClass = [
            nextShapeList["element1"]["class"],
            nextShapeList["element2"]["class"],
            nextShapeList["element3"]["class"],
            nextShapeList["element4"]["class"],
            nextShapeList["element5"]["class"]
        ]
        ## hold shape info
        HoldShapeClass = GameStatus["block_info"]["holdShape"]["class"]
        HoldShapeDirectionRange = GameStatus["block_info"]["holdShape"]["direction_range"]

        ## board backboard
        self.board_backboard[self.board_sl] = GameStatus["field_info"]["backboard"]

        # Decide mode
        self.mode = self.decideMode(self.board_backboard)

        strategy_candidate = [] # [evalvalue, id, strategy, board]
        heapify(strategy_candidate)

        #Search current shape
        self.beamSearch(self.board_backboard, CurrentShapeClass.shape, 
                         CurrentShapeDirectionRange, strategy_candidate)
        
        #Search hold shape
        if self.hold:
            self.beamSearch(self.board_backboard, HoldShapeClass.shape, 
                             HoldShapeDirectionRange, strategy_candidate, hold=True)

        #Search next shape
        for i in range(self.estimate_num):
            strategy_candidate_tmp = []
            heapify(strategy_candidate_tmp)
            for pre_eval,_, pre_strategy, pre_board in strategy_candidate:
                self.beamSearch(pre_board, ShapeListClass[i].shape, ShapeListDirectionRange[i], strategy_candidate_tmp,
                                pre_strategy=pre_strategy, pre_EvalValuse=pre_eval)
            strategy_candidate = copy(strategy_candidate_tmp)

        max_strategy = nlargest(1, strategy_candidate)
        strategy = max_strategy[0][2]

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

    def decideMode(self, board):
        mode = Mode.DEFENCE
        self.ind = self.ind_defence
        width = self.board_width
        height = self.board_height

        board[self.peaks_sl] = \
            self.get_peaks(board[self.board_sl], height, width)
        board[self.holes_sl], holes_height = \
            self.get_holes(board[self.board_sl], width, board[self.peaks_sl])
        board[self.wells_sl] = \
            self.get_wells(width, board[self.peaks_sl])

        peaks = board[self.peaks_sl]
        maxY = max(peaks)
        wells = board[self.wells_sl]
        wells_sorted = sorted(wells)
        second_well = wells_sorted[-2]
        if second_well < 5 and maxY < 15 and holes_height < 7:
            self.ind = self.ind_normal
            if peaks[0] < peaks[-1]:
                mode = Mode.ATTACK_LEFT
                if wells[1] > 2:
                    mode = Mode.NORMAL_LEFT
            else:
                mode = Mode.ATTACK_RIGHT
                if wells[-2] > 2:
                    mode = Mode.NORMAL_RIGHT
        return mode

    def beamSearch(self, board, Shape, DirectionRange, strategy_candidate, 
        hold = False, pre_strategy = None, pre_EvalValuse = None):
        id = 0
        shape_xmin_max = self.xmin_max_tuple[Shape]
        for direction in DirectionRange:
            # search with x range
            xMin, xMax = shape_xmin_max[direction]
            ind = (Shape - 1) * 4 + direction
            if self.mode == Mode.NORMAL_RIGHT or self.mode == Mode.ATTACK_RIGHT:
                xMax_allow_ind = self.xMinMax_allow_ind_ATTACK_RIGHT
                if self.mode == Mode.NORMAL_RIGHT:
                    xMax_allow_ind = self.xMinMax_allow_ind_NORMAL_RIGHT
                if not ind in xMax_allow_ind:
                    xMax -= 1
                elif ind == 0:
                    peaks = board[self.peaks_sl]
                    right_end_Y = peaks[-1]
                    left_min_Y = min(peaks[:-1])
                    if left_min_Y - right_end_Y < 4:
                        xMax -= 1

            elif self.mode == Mode.NORMAL_LEFT or self.mode == Mode.ATTACK_LEFT:
                xMin_allow_ind = self.xMinMax_allow_ind_ATTACK_LEFT
                if self.mode == Mode.NORMAL_LEFT:
                    xMin_allow_ind = self.xMinMax_allow_ind_NORMAL_LEFT
                if not ind in xMin_allow_ind:
                    xMin += 1
                elif ind == 0:
                    peaks = board[self.peaks_sl]
                    left_end_Y = peaks[0]
                    right_min_Y = min(peaks[1:])
                    if right_min_Y - left_end_Y < 4:
                        xMin += 1

            for x in range(xMin, xMax):
                # get board data, as if dropdown block
                dropdown_board, dy= self.getDropDownBoard(board, Shape, direction, x)
                # evaluate board
                EvalValue, dropdown_board = self.calcEvaluationValue(dropdown_board, Shape, direction)
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

    def getShapeCoordArray(self, Shape, direction, x, y):
        return [(x + xx, y + yy) for xx, yy in self.shape_coord[Shape][direction]]

    def getShapeCoordArray_for_drop(self, Shape, direction, x, y):
        return [(x + xx, y + yy) for xx, yy in self.shape_coord_for_drop[Shape][direction]]

    def getShapeCoordArray_for_peak(self, Shape, direction, x, y):
        return [(x + xx, y + yy) for xx, yy in self.shape_coord_for_peak[Shape][direction]]

    def getDropDownBoard(self, board_backboard, Shape, direction, x):
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.
        board = copy(board_backboard)
        board, dy = self.dropDown(board, Shape, direction, x)
        return board, dy

    def dropDown(self, board, Shape, direction, x):
        # internal function of getBoard.
        # -- drop down the shape on the board.
        height = self.board_height
        width = self.board_width
        maxY = max(board[self.peaks_sl])
        dy = height - 1
        coordArray = self.getShapeCoordArray_for_drop(Shape, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = height - (maxY + 2)
            while _yy + _y < height and (_yy + _y < 0 or board[(_y + _yy)*width + _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        board = self.dropDownWithDy(board, Shape, direction, x, dy)
        return board, dy

    def dropDownWithDy(self, board, Shape, direction, x, dy):
        # internal function of dropDown.
        coordArray = self.getShapeCoordArray(Shape, direction, x, dy)
        for _x, _y in coordArray:
            if not _y < 0:
                board[_y*self.board_width + _x] = Shape
        coordArray_for_peak = self.getShapeCoordArray_for_peak(Shape, direction, x, dy)
        for _x, _y in coordArray_for_peak:
            if _y < 0:
                board[self.board_width * self.board_height + _x] = self.board_height
            else:
                board[self.board_width * self.board_height + _x] = self.board_height - _y
        return board
    
    def calcEvaluationValue(self, board, Shape, direction):
        # calc Evaluation Value
        width = self.board_width
        height = self.board_height

        maxPeak = max(board[self.peaks_sl])
        minPeak = min(board[self.peaks_sl])
        shape_height = self.shape_height_abs[Shape][direction]

        board[self.board_sl], fullLines = self.removeFullLines(
            board[self.board_sl], height, width, maxPeak, minPeak, shape_height)
        peaks_tmp = [peak - fullLines for peak in board[self.peaks_sl]]
        board[self.peaks_sl] = self.get_peaks_from_before(board[self.board_sl], height, width, peaks_tmp)
        board[self.holes_sl], _ = self.get_holes(board[self.board_sl], width, board[self.peaks_sl])
        board[self.wells_sl] = self.get_wells(width, board[self.peaks_sl])

        nPeaks = sum(board[self.peaks_sl])
        maxY = max(board[self.peaks_sl])
        total_dy = self.get_total_dy(width, board[self.peaks_sl])
        nHoles = sum(board[self.holes_sl])
        x_transitions = self.get_x_transitions(board, maxY)
        y_transitions = self.get_y_transitions(board, board[self.peaks_sl])
        maxWell = max(board[self.wells_sl])
        total_col_with_hole = self.get_total_cols_with_hole(width, board[self.holes_sl])
        total_none_cols = self.get_total_none_cols(width, board[self.peaks_sl])

        if fullLines < 3:
            fullLines = 0

        eval_list = [nPeaks, nHoles, total_col_with_hole, total_dy, x_transitions, y_transitions, total_none_cols, maxWell, fullLines]
        score = sum([x * y for (x,y) in zip(self.ind, eval_list)])
        
        if fullLines == 4:
            score += 10000

        return score, board
    
    def removeFullLines(self, board, height, width, maxPeak, minPeak, shape_height):
        newBoard = [0] * width * height
        count_height = minPeak - shape_height
        newY = height - 1
        if count_height > 0:
            sl = slice((height-count_height)*width,height*width)
            newBoard[sl] = board[sl]
            newY -= count_height
        else:
            count_height = 0
        fullLines = 0
        for y in range(height - count_height - 1, height - minPeak -1 , -1):
            blockCount = sum([1 if board[y*width + x] > 0 else 0 for x in range(width)])
            if blockCount == width:
                fullLines += 1
            else:
                newBoard[newY * width : (newY + 1) * width] = board[y * width : (y + 1) * width]
                newY -= 1
        if maxPeak - minPeak > 0:
            newBoard[(newY - (maxPeak - minPeak)+1)*width : (newY+1) * width] = \
                board[(height-maxPeak)*width : (height-minPeak) * width]
        return newBoard, fullLines
    
    def get_peaks(self, board, height, width):
        start_height = height - 1
        peaks = [0] * width
        for x in range(width):
            for y in range(start_height, 0, -1):
                if board[(height - y) * width + x] != 0:
                    peaks[x] = y
                    break
        return peaks

    def get_peaks_from_before(self, board, height, width, peaks_before = None):
        peaks = [0] * width
        for x in range(width):
            for y in range(peaks_before[x], 0, -1):
                if board[(height - y) * width + x] != 0:
                    peaks[x] = y
                    break
        return peaks

    def get_holes(self, board, width, peaks):
        holes= [0] * width
        holes_max = 0
        for x in range(width):
            start_y = peaks[x] - 1
            if start_y <= 0:
                pass
            else:
                hole_flag = False
                hole = 0
                for y in range(start_y, 0, -1):
                    if board[(self.board_height - y) * self.board_width + x] == 0:
                        if not hole_flag:
                            if y > holes_max:
                                holes_max = y
                                hole_flag = True
                        hole += 1
                holes[x] = hole
        return holes, holes_max

    def get_wells(self, width, peaks):
        wells = [0] * width
        for x in range(width):
            if x == 0:
                well = peaks[1] - peaks[0]
                well = well if well > 0 else 0
                wells[x] = well
            elif x == len(peaks) - 1:
                well = peaks[-2] - peaks[-1]
                well = well if well > 0 else 0
                wells[x] = well
            else:
                w1 = peaks[x - 1] - peaks[x]
                w2 = peaks[x + 1] - peaks[x]
                w1 = w1 if w1 > 0 else 0
                w2 = w2 if w2 > 0 else 0
                well = w1 if w1 >= w2 else w2
                wells[x] = well
        return wells
    
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
        return sum([abs(peaks[x+1]-peaks[x]) for x in range(width-1)])
    
    def get_total_cols_with_hole(self, width, holes):
        return sum([1 if holes[x] else 0 for x in range(width)])
    
    def get_total_none_cols(self, width, peaks):
        return sum([1 if peaks[x] else 0 for x in range(width)])
    
    def show_board(self, board):
        for y in range(self.board_height):
            tmpstr=''
            for x in range(self.board_width):
                tmpstr = tmpstr + str(board[y*self.board_width+x]) + ' '
            print(format(x,'02d'),tmpstr)
        print('-- 0 1 2 3 4 5 6 7 8 9 --' )

BLOCK_CONTROLLER = Block_Controller()