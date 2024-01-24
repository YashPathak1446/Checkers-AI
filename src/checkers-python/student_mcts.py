""" Helper functions for the MCTS algorithm"""
from queue import Queue
from BoardClasses import Board

class MCTS_node:


    def __init__(self):
        self.wins = 0
        self.attempts = 0

    def ratio(self):
        """ Get the percentage of successful games """
        if self.attempts == 0:  # Avoid domain error
            return 0
        return self.wins / self.attempts

    def wins(self):
        """ Get the total number of wins """
        return self.wins

    def total_attempts(self):
        """ Get the total number of attempts """
        return self.attempts
    
    def add(self, win: int, attempts: int):
        """ Add a win count. If win == 0: loss (don't add to wins). If win == 1: tie (add half win). Else win == 2: win.
        Each attempt costs 2 games. """
        if win:
            self.wins += win
        self.attempts += attempts

    def __str__(self):
        return 'Wins: {wins}  Attempts: {attempts}'.format(wins=self.wins, attempts=self.attempts)

class MCTS_cache:
    """ Caches the objects from the MCTS' previous runs """

    def __init__(self):
        self.cache = Queue(maxsize=500)
        self.cache_retrieval = {}  # Str:MCTS

    def get_MCTS(self, board: Board) -> MCTS_node:
        """ Get MCTS if it exists. Return new MCTS object if DNE. """
        self._clear_cache()  # Clear the cache, if necessary

        position = self._get_position(board)
        if position not in self.cache_retrieval:  # Get the MCTS node. If not in dictionary, make a new one
            self.cache.put(position)
            self.cache_retrieval[position] = MCTS_node()
            
        return self.cache_retrieval[position]
        

    def _clear_cache(self) -> None:
        """ Clear an element if there is no space left. """
        if self.cache.full():  # Empty if full
            node_remove = self.cache.get()
            del self.cache_retrieval[node_remove]

    @staticmethod
    def _get_position(board: Board):
        """ Create a hashable position for the board. Needs to hash pieces differently.
            Uses lettered positions. aa -> 1,1      |       hh -> 8,8
            Also takes into account king pieces

            [lower][lower]: White -> aa
            [lower][Upper]: White King -> aA
            [Upper][Upper]: Black -> AA
            [Upper][Lower]: Black King -> Aa

            ord('@') + index = Capital
            ord('`') + index = lowercase

        """
        hash_string = ''
        for row_index in range(len(board.board)):
            for column_index in range(len(board.board[row_index])):
                checker = board.board[row_index][column_index]

                if checker.get_color() == ".":  # Skip empty space
                    continue

                elif checker.get_color() == 'W':  # White piece
                    if checker.is_king:  # aA
                        hash_string += lowercase(row_index) + capital(column_index)
                    else:  # aa
                        hash_string += lowercase(row_index) + lowercase(row_index)


                else:
                    if checker.is_king: #Aa
                        hash_string += capital(row_index) + lowercase(column_index)
                    else:
                        hash_string += capital(row_index) + capital(column_index)

        return hash_string


def capital(index: int) -> str:
    return chr(ord('@') + index)

def lowercase(index: int) -> str:
    return chr(ord('`') + index)



