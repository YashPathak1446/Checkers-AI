from random import randint
import random
from BoardClasses import Move
from BoardClasses import Board
from copy import deepcopy
import math
from student_mcts import MCTS_cache, MCTS_node
from typing import Tuple, List
import time

#The following part should be completed by students.
#Students can modify anything except the class name and exisiting functions and varibles.
class StudentAI():

    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2  # Automatically sets to W
        self.time = 0

        # Scoring
        self.king_score = 1.5
        self.man_score = 1
        self.piececount = p * col / 2  # NOTE: p * col guaranteed to be even
        self.bestScore = self.piececount * self.king_score * 2 # Best Score: we win and no piece has died and everyone is a king


    def get_move(self,move: Move):
                  
        if len(move) != 0:  # Get list of availalbe
            self.board.make_move(move,self.opponent[self.color])
        else:
            self.color = 1  # We have first move. Sets to B~

        moves = self.board.get_all_possible_moves(self.color)
        # index = randint(0,len(moves)-1)
        # inner_index =  randint(0,len(moves[index])-1)
        # move = moves[index][inner_index]
        move = self.next_best_move(moves)
        self.board.make_move(move, self.color)
        return move

    def next_best_move(self, moves: Move) -> Move:
        moves = self.decompose_move_list(moves)  # First, flatten list
        move_map = {i: MCTS_node() for i in range(len(moves))}  # Key of {moves[index]: MCTS}

        cache = MCTS_cache()
        # Let the max time for deciding a move be 5 seconds
        # Value is subject to change
        max_time = 10.0
        # Start the timer
        start_time = time.time()
        
        for key in move_map:  # x Successions
            # for i in range(5):
            # Instead of going to depth 5, exit when you have crossed the time limit
            if time.time() - start_time >= max_time:
                print('broken inside move map loop')
                break # Stop the loop if total time has crossed the max time in selecting move
            print('entered move map loop')
            # Run the MCTS. If it is a win, add it to the win column.
            new_board = deepcopy(self.board)
            new_board.make_move(moves[key], turn=self.color)
            success_score, cache = self.mcts(board=new_board, curr_player=self.opponent[self.color], depth=1, cache=cache)
            move_map[key].add(win=success_score, attempts=self.bestScore)

        # Sort moves based on success rate
        # Sorted in descending order based off the ratio (success rate) of every move
        sorted_moves = sorted(move_map.keys(), key = lambda x: move_map[x].ratio(), reverse = True)
        # Explore all the moves in the sorted moves list until the time limit is reached
        # The point of the second loop is to ecaluate each branches to a depth, and hcoose the next best move
        for index_next_move in sorted_moves:
            if time.time() - start_time >= max_time:
                print('broken inside sorted moves loop')
                break
            print('entered sorted loop')
            
            new_board = deepcopy(self.board)
            new_board.make_move(moves[index_next_move], turn=self.color)
            # Changed depth to 3 so that we can go upto at least depth 3 for each node
            success_score, cache = self.mcts(board=new_board, curr_player=self.opponent[self.color], depth=1, cache=cache)
            best_move = None
            best_score = float('-inf')
            # Update move_map with the new success_score if needed
            move_map[index_next_move].add(win=success_score, attempts=self.bestScore)
            # calculate a standard for the score to obtain the best ratio possible
            score = success_score * move_map[index_next_move].total_attempts()
            print('Score:', score)
            print('Success Score:', success_score)
            if score > best_score:
                best_score = score
                best_move = moves[index_next_move]
                
            # print(index_next_move, str(move_map[index_next_move]))

        # Return the best possible move
        return best_move
            
        # index_best_move = 0
        # best_move = move_map[index_best_move].ratio() # Assume there is a move. Thus, 0 MUST be in the move_map
        # for key, value in move_map.items():  # Now, find the best-scoring
        #     success_rate = value.ratio()
        #     if success_rate > best_move:  # Only pick a better move iff it is more successful
        #         index_best_move = key
        #         best_move = success_rate

        # for key in move_map:
        #     print(key, str(move_map[key]))

        # return moves[index_best_move]


    @staticmethod
    def mcts_exploration(mcts_node: MCTS_node, num_parent_visits: int, flip=False):  # -> bool
        """ Given a node, figure out its exploration parameter.
        flip: Flip the ratio. All MCTS nodes track how well WE ARE DOING. Need to flip the ratio for success rates of OTHER PLAYER"""

        current_attempts = 1 if mcts_node.total_attempts() == 0 else mcts_node.total_attempts()  # No domain errors on division

        if not flip:
            ucb = mcts_node.ratio() + (math.sqrt(2) * math.sqrt(math.log(1 + num_parent_visits) / current_attempts))  # UCB = current_avg + (C * sqrt( ln(parent_attemps) / child_attempts )
        else:  # Switch success rate
            ucb = (1 - mcts_node.ratio()) + (math.sqrt(2) * math.sqrt(math.log(1 + num_parent_visits) / current_attempts))
        return ucb

    def mcts(self, board: Board, curr_player: int, depth: int, cache: MCTS_cache):
        """ For each move, pick the next move to be explored."""
        board = deepcopy(board)  # Make sure that we have a copy of the board.

        # First, check if someone won.
        who_won = board.is_win(turn=self.color)
        if who_won == self.color:
            return 16, cache  # We won! Return that we have won
        elif who_won != 0:
            return 0, cache  # We lost! Return that we lost

        # No winner. Now check if we have recursed enough. Otherwise
        if depth >= 3:  # Currently, recurse to the 3rd level. This checks if WE are winning in at this point
            score = self.board_evaluation(board, player=self.color) + 8
            return score, cache

        else:  # If not the next level, we need to keep moving toward the bottom
            moves = board.get_all_possible_moves(curr_player)

            if not len(moves):  # No moves. This is a loss for current player
                return (curr_player != self.color), cache

            moves = self.decompose_move_list(moves)  # Flatten list
            move_map = {}  # {index: MCTS_node}
            for i in range(len(moves)):
                new_board = deepcopy(board)
                new_board.make_move(moves[i], turn=curr_player)
                move_map[i] = cache.get_MCTS(new_board)

            # Get the best next node to explore. Some move must exist, so we know 0 must be there
            index_next_move = 0
            flip_mcts = (curr_player != self.color)  # Flip success values if True. Explained more in mcts_exploration
            best_ucb = self.mcts_exploration(move_map[index_next_move], num_parent_visits=0, flip=flip_mcts)

            for key, value in move_map.items():  # Find the next move to explore
                curr_ucb = self.mcts_exploration(move_map[key], num_parent_visits=0)
                if curr_ucb > best_ucb:
                    best_ucb = curr_ucb
                    index_next_move = key

            if best_ucb == 0:  # Randomly choose a node, if no promising nodes
                index_next_move = random.choice(list(move_map.keys()))

            # Now that we have the best move, get the other best moves.
            new_board = deepcopy(board)
            new_board.make_move(moves[index_next_move], turn=curr_player)  # Make the index of the next move
            return self.mcts(board=new_board, curr_player=self.opponent[curr_player], depth=depth+1, cache=cache)

    @staticmethod
    def board_evaluation(board_to_check: Board, player: int) -> int:
        """ This function evaluates the checkers on the board. Score is a value that
        returns the evaluation of the board.
        Negative: worse position
        Positive: better position
        Zero: even position
        """
        color = "B" if player == 1 else "W"  # Rewrite color to be the STRING VALUE of the checker color
        for row_index in range(len(board_to_check.board)):
            for checker_index in range(len(board_to_check.board[row_index])):
                checker = board_to_check.board[row_index][checker_index]
                curr_color = checker.get_color()
                if curr_color == ".":  # Empty space on board
                    continue

                if curr_color == color:
                    if checker.is_king:
                        score += self.king_score
                    else:
                        score += self.man_score
                else:
                    if checker.is_king: 
                        score -= self.king_score
                    else:
                        score -= self.man_score
        return score
        
    @staticmethod
    def decompose_move_list(moves: List[List[Move]]) -> List[Move]:
        """ From a move list, decompose it. That is, flatten it and make a 1D list of moves."""
        flattened_list = []
        for i in range(len(moves)):
            for j in range(len(moves[i])):
                flattened_list.append(moves[i][j])

        return flattened_list
