#!/usr/bin/python3
# -*- coding: utf-8 -*-
from time import time
import copy
from enum import Enum
import numpy as np
import csv
import os
from heapq import heapify, heappush, heappop, heappushpop, nlargest
import copy
import logging

logging.basicConfig(level=logging.WARNING, format='%(levelname)s %(asctime)s: %(message)s')

class Mode(Enum):
    NORMAL = 1
    ATTACK = 2
    DEFENCE = 3

class Block_Controller(object):

    def __init__(self):
        # init parameter
        self.individual = self.get_individual(csv_file = 
            os.path.dirname(os.path.abspath(__file__)) + "/genetic_algorithm/individual.csv")
        self.beam_width = 10
        self.estimate_num = 5
        

    # GetNextMove is main function.
    # input
    #    nextMove : nextMove structure which is empty.
    #    GameStatus : block/field/judge/debug information. 
    #                 in detail see the internal GameStatus data.
    # output
    #    nextMove : nextMove structure which includes next shape position and the other.
    def GetNextMove(self, nextMove, GameStatus):

        t1 = time()

        ## Get data from GameStatus
        # current shape info
        CurrentShapeDirectionRange = GameStatus["block_info"]["currentShape"]["direction_range"]
        CurrentShapeClass = GameStatus["block_info"]["currentShape"]["class"]
        logging.debug('CurrentShapeClass: {}'.format(CurrentShapeClass))
        # next shape info
        ShapeListDirectionRange = []
        ShapeListClass = []
        for i in range(1,6):
            ElementNo = "element" + str(i)
            ShapeListDirectionRange.append(GameStatus["block_info"]["nextShapeList"][ElementNo]["direction_range"])
            ShapeListClass.append(GameStatus["block_info"]["nextShapeList"][ElementNo]["class"])
            logging.debug('ShapeListClass {}:{}'.format(ElementNo, GameStatus["block_info"]["nextShapeList"][ElementNo]["class"]))
        # hold shape info
        HoldShapeDirectionRange = GameStatus["block_info"]["holdShape"]["direction_range"]
        HoldShapeClass = GameStatus["block_info"]["holdShape"]["class"]
        logging.debug('HoldShapeClass: {}'.format(HoldShapeClass))

        # current board info
        self.board_backboard = GameStatus["field_info"]["backboard"]
        # default board definition
        self.board_data_width = GameStatus["field_info"]["width"]
        self.board_data_height = GameStatus["field_info"]["height"]
        self.ShapeNone_index = GameStatus["debug_info"]["shape_info"]["shapeNone"]["index"]
        # change board list in numpy list
        self.board_backboard_np = np.array(self.board_backboard).reshape(self.board_data_height, self.board_data_width)

        # search best nextMove -->
        mode = self.decideMode(self.board_backboard_np)
        # search with current block Shape
        # select top {beam width} strategy
        top_strategy = []
        heapify(top_strategy)

        count = 0
        for direction0 in CurrentShapeDirectionRange:
            # search with x range
            x0Min, x0Max = self.getSearchXRange(CurrentShapeClass, direction0)
            for x0 in range(x0Min, x0Max):
                # get board data, as if dropdown block
                board, dy= self.getDropDownBoard(self.board_backboard_np, CurrentShapeClass, direction0, x0)
                # evaluate board
                EvalValue = self.calcEvaluationValue(board, dy, mode)
                # get board removed fulllines
                board, _ = self.removeFullLines(board)
                strategy = (direction0, x0, 1, 1)
                # update best move
                if len(top_strategy) < self.beam_width:
                    heappush(top_strategy, (EvalValue, count, strategy, board))
                else:
                    heappushpop(top_strategy, (EvalValue, count, strategy, board))
                count += 1
        
        for i in range(self.estimate_num):
            next_strategy = []
            heapify(next_strategy)
            for _,_, strategy, board in top_strategy:
                for direction1 in ShapeListDirectionRange[i]:
                    x1Min, x1Max = self.getSearchXRange(ShapeListClass[i], direction1)
                    for x1 in range(x1Min, x1Max):
                        board2, dy = self.getDropDownBoard(board, ShapeListClass[i], direction1, x1)
                        EvalValue = self.calcEvaluationValue(board2, dy, mode)
                        board2, _ = self.removeFullLines(board2)
                        # update best move
                        if len(next_strategy) < self.beam_width:
                            heappush(next_strategy, (EvalValue, count, strategy, board2))
                        else:
                            heappushpop(next_strategy, (EvalValue, count, strategy, board2))
                        count +=1
            top_strategy = copy.deepcopy(next_strategy)
        
        max_strategy = nlargest(1, top_strategy)
        strategy = max_strategy[0][2]
        # search best nextMove <--

        logging.debug('Mode: {}'.format(mode))
        #print("Search time = ", time() - t1)
        nextMove["strategy"]["direction"] = strategy[0]
        nextMove["strategy"]["x"] = strategy[1]
        nextMove["strategy"]["y_operation"] = strategy[2]
        nextMove["strategy"]["y_moveblocknum"] = strategy[3]
        #print(nextMove)

        #use HOLD function
        nextMove["strategy"]["use_hold_function"] = "n"
        return nextMove

    def get_individual(self, csv_file = "individual.csv"):
        with open(csv_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            ind_list = []
            for row in reader:
                if reader.line_num == 2:
                    for col in row:
                        ind_list.append(float(col))
                    break
            return np.array(ind_list)

    def getSearchXRange(self, Shape_class, direction):
        #
        # get x range from shape direction.
        #
        minX, maxX, _, _ = Shape_class.getBoundingOffsets(direction) # get shape x offsets[minX,maxX] as relative value.
        xMin = -1 * minX
        xMax = self.board_data_width - maxX
        return xMin, xMax

    def getShapeCoordArray(self, Shape_class, direction, x, y):
        #
        # get coordinate array by given shape.
        #
        coordArray = Shape_class.getCoords(direction, x, y) # get array from shape direction, x, y.
        return coordArray

    def getDropDownBoard(self, board_backboard, Shape_class, direction, x):
        # 
        # get new board.
        #
        # copy backboard data to make new board.
        # if not, original backboard data will be updated later.
        board = copy.deepcopy(board_backboard)
        _board, dy = self.dropDown(board, Shape_class, direction, x)
        return _board, dy
    
    def removeFullLines(self, board):
        height = board.shape[0]
        width = board.shape[1]
        newBoard = np.zeros((height, width))
        newY = height - 1
        fullLines = 0
        for y in range(height - 1, -1, -1):
            blockCount = sum([1 if board[y, x] > 0 else 0 for x in range(width)])
            if blockCount < width and blockCount > 0:
                for x in range(width):
                    newBoard[newY, x] = board[y, x]
                newY -= 1
            elif blockCount == width:
                fullLines += 1
        return newBoard, fullLines

    def dropDown(self, board, Shape_class, direction, x):
        # 
        # internal function of getBoard.
        # -- drop down the shape on the board.
        # 
        height = board.shape[0]
        dy = height - 1
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        # update dy
        for _x, _y in coordArray:
            _yy = 0
            while _yy + _y < height and (_yy + _y < 0 or board[_y + _yy, _x] == self.ShapeNone_index):
                _yy += 1
            _yy -= 1
            if _yy < dy:
                dy = _yy
        # get new board
        _board = self.dropDownWithDy(board, Shape_class, direction, x, dy)
        return _board, dy

    def dropDownWithDy(self, board, Shape_class, direction, x, dy):
        #
        # internal function of dropDown.
        #
        _board = board
        coordArray = self.getShapeCoordArray(Shape_class, direction, x, 0)
        for _x, _y in coordArray:
            _board[_y + dy, _x] = Shape_class.shape
        return _board
    
    def decideMode(self, board):
        mode = Mode.DEFENCE
        peaks = self.get_peaks(board)
        maxY = np.max(peaks)
        holes = self.get_holes(board, peaks)
        n_holes = np.sum(holes)
        wells = self.get_wells(board, peaks)
        second_well = np.sort(wells)[-2]
        if second_well < 5 and maxY < 15 and n_holes < 4:
            mode = Mode.NORMAL
        #if second_well < 5 and maxY < 12 and n_holes < 4:
            #mode = Mode.ATTACK
        #print("mode:", mode)
        return mode

    def calcEvaluationValue(self, board, dy, mode = Mode.ATTACK):
        # calc Evaluation Value

        #before remove full lines
        peaks_before = self.get_peaks(board)
        maxY_right = peaks_before[-1]

        #after remove full lines
        board, fullLines = self.removeFullLines(board)
        peaks = self.get_peaks(board)
        nPeaks = peaks.sum()
        maxY = np.max(peaks)
        holes = self.get_holes(board, peaks)
        nHoles = np.sum(holes)
        total_col_with_hole = self.get_total_cols_with_hole(board, holes)
        x_transitions = self.get_x_transitions(board, maxY)
        y_transitions = self.get_y_transitions(board, peaks)
        total_dy = self.get_total_dy(board, peaks)
        wells = self.get_wells(board, peaks)
        maxWell = np.max(wells)
        total_none_cols = self.get_total_none_cols(board)

        #20220806
        #eval_list = np.array([fullLines, nPeaks, maxY, maxY_right, nHoles, total_col_with_hole,
            #x_transitions, y_transitions, total_dy, maxWell])

        #20220810-1
        #eval_list = np.array([fullLines**2, nPeaks, maxY, nHoles,
            #x_transitions, y_transitions, total_dy, maxWell,total_col_with_hole, total_none_cols])

        #20220810-2
        if fullLines < 3:
            fullLines = 0
        #eval_list = np.array([fullLines, nPeaks, maxY, nHoles,
            #x_transitions, y_transitions, total_dy, maxWell,total_col_with_hole, total_none_cols])

        #20220820
        #eval_list = np.array([fullLines, nPeaks, maxY, nHoles, x_transitions, y_transitions])

        #20220824
        eval_list = np.array([nPeaks, nHoles, total_col_with_hole, total_dy,
            x_transitions, y_transitions, total_none_cols, maxWell, fullLines])
        
        #print("individual", self.individual)
        #print("eval_list", eval_list)
        score = np.dot(self.individual, np.transpose(eval_list))
        if mode == Mode.NORMAL and fullLines < 3:
            score -= 1000 * maxY_right

        #if mode == Mode.ATTACK and fullLines < 4:
            #score -= 1000 * maxY_right

        #print ("score", score)

        #if mode == Mode.NORMAL:
            #score -= nHoles * 10
            #score -= maxY * 50
            #score -= nPeaks * 1
            #score += dy * 1
        #elif mode == Mode.DEFENCE:
            #score -= nHoles * 10
            #score -= maxY * 50
            #score -= nPeaks * 1
            #score += dy * 1
        #elif mode == Mode.ATTACK:
            #if fullLines < 3:
                #score -= 1000 * maxY_right
            #score -= nHoles * 100
            #score -= maxY * 5
            #score -= nPeaks * 1
            #score += dy * 1
        return score
    
    def get_peaks(self, board):
        height = board.shape[0]
        width = board.shape[1]
        peaks_list = []
        for x in range(width):
            block_ind = board[:, x].nonzero()
            if  len(block_ind[0]) == 0:
                peaks_list.append(0)
            else:
                peaks_list.append(height -  block_ind[0][0])
        peaks = np.asarray(peaks_list)
        return peaks

    def get_holes(self, board, peaks = None):
        height = board.shape[0]
        width = board.shape[1]
        if peaks is None:
            peaks = self.get_peaks(board)
        holes_list = []
        for col in range(width):
            start_raw = height - peaks[col]
            if start_raw == 0:
                holes_list.append(0)
            else:
                holes_list.append(np.count_nonzero(board[start_raw:, col] == 0))
        holes = np.asarray(holes_list)
        return holes
    
    def get_fullLines(self, board):
        height = board.shape[0]
        width = board.shape[1]
        fullLines = 0
        for raw in range(height):
            blocks = np.count_nonzero(board[raw] != self.ShapeNone_index)
            if blocks == width:
                fullLines += 1
        return fullLines
    
    def get_total_cols_with_hole(self, board, holes = None):
        if holes is None:
            holes = self.get_holes(board)
        return np.count_nonzero(holes > 0)
    
    def get_x_transitions(self, board, maxY = None):
        if maxY is None:
            maxY = self.get_maxY(board)
        height = board.shape[0]
        width = board.shape[1]
        transitions = 0
        for y in range(height - maxY, height):
            for x in range(1, width):
                if board[y, x] != board[y, x-1]:
                    transitions += 1
        return transitions
    
    def get_y_transitions(self, board, peaks = None):
        if peaks is None:
            peaks = self.get_peaks(board)
        height = board.shape[0]
        width = board.shape[1]
        transitions = 0
        for x in range(width):
            for y in range(height - peaks[x], height -1):
                if board[y, x] != board[y+1, x]:
                    transitions += 1
        return transitions
    
    def get_total_dy(self, board, peaks = None):
        if peaks is None:
            peaks = self.get_peaks(board)
        total_dy = 0
        for x in range(len(peaks)-1):
            total_dy += np.abs(peaks[x+1] - peaks[x])
        return total_dy
    
    def get_wells(self, board, peaks = None):
        if peaks is None:
            peaks = self.get_peaks(board)
        wells = []
        for x in range(len(peaks)):
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
    
    def get_total_none_cols(self, board):
        return np.count_nonzero(np.count_nonzero(board, axis=0) == 0)

BLOCK_CONTROLLER = Block_Controller()