from reconchess import *
import chess.engine
import os
import random
import math
from functools import reduce

STOCKFISH_ENV_VAR = 'STOCKFISH_EXECUTABLE'

class Mikh_AI_lTal(Player):



    def __init__(self):
        self.board = None
        self.color = None
        self.my_piece_captured_square = None
        self.engine = chess.engine.SimpleEngine.popen_uci("C:\python36\RBC\stockfish-11-win\Windows\stockfish_20011801_x64", setpgrp=True)
        self.counter = 0


    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.board = board
        self.color = color

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        # if the opponent captured our piece, remove it from our board.
        self.my_piece_captured_square = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> \
            Optional[Square]:
        self.counter+=1

        # if our piece was just captured, sense one square towards the center of where it was captured
        if self.my_piece_captured_square:
            return self.my_piece_captured_square
        
        if self.counter == 5:
            if self.color == True:
                return 44
            else:
                return 20
        if self.counter == 10:
            if self.color == True:
                return 53
            else:
                return 13
        if self.counter == 20:
            if self.color == True:
                return 50
            else:
                return 10
        
        
        
        # calculate opponent possible moves, and sense at the most probable square opponent moved to
    
        mass_list=[]
        response_list=[]
        self.board.turn = not self.color
        for x in self.board.pseudo_legal_moves:
            self.board.push(x)
            lib = self.engine.analyse(self.board, chess.engine.Limit(time=1, depth=10))
            response_list.append((math.exp(lib['score'].pov(not self.color).score(mate_score=10000)/100), x.to_square))
            self.board.pop()
        self.board.turn = self.color

        normalize = reduce(lambda a,b:a+b, [i[0] for i in response_list])
        normalized_list = [(i[0]/normalize, i[1]) for i in response_list]
        tuple_board = [(0,i) for i in range(0,64)]
        for x in normalized_list:
            tuple_board[x[1]] = tuple(map(sum,zip((x[0],0), tuple_board[x[1]])))
            
        def mass(square: int):
            mass_squares =[n-9, n-8, n-7, n-1, n, n+1, n+7, n+8, n+9]
            value = 0
            for x in mass_squares:
                if 0 <= x <= 63: 
                    value += tuple_board[x][0]
            return value
            
        for n in range(0,64):
            mass_list.append((mass(n),n))
            
        self.board.clear_stack()
        if mass_list:
            return sorted(mass_list, key=lambda x:x[0], reverse=True)[0][1]

        else:
            for square, piece in self.board.piece_map().items():
                if piece.color == self.color:
                    return sense_actions.remove(square)
            try:
                return random.choice([set(27,28,35,36) & set(sense_actions)])
            except:
                pass

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # add the pieces in the sense result to our board
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        # if we might be able to take the king, try to
        enemy_king_square = self.board.king(not self.color)
        if enemy_king_square:
            # if there are any ally pieces that can take king, execute one of those moves
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
            if enemy_king_attackers:
                attacker_square = enemy_king_attackers.pop()
                return chess.Move(attacker_square, enemy_king_square)
            # if there is a piece that can give check w/o taking a piece, play the best move that does so

            self.board.clear_stack()
            self.board.turn=self.color
            silent_check_dict={}
            for x in self.board.pseudo_legal_moves:
                if self.board.gives_check(x) and not self.board.is_capture(x):
                    self.board.push(x)
                    silent_check_dict[x]=self.engine.analyse(self.board, chess.engine.Limit(time=1, depth=10))["score"].pov(self.color)
                    self.board.pop()
            if silent_check_dict:
                return sorted(silent_check_dict.items(), key=lambda x:x[1], reverse=True)[0][0]

        # otherwise, try to move with the stockfish chess engine
        try:
            self.board.turn = self.color
            self.board.clear_stack()
            result = self.engine.play(self.board, chess.engine.Limit(time=2, depth=10))
            return result.move
        except chess.engine.EngineTerminatedError:
            print('Stockfish Engine died')
        except chess.engine.EngineError:
            print('Stockfish Engine bad state at "{}"'.format(self.board.fen()))

        # if all else fails, pass
        return None

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[Square]):
        # if a move was executed, apply it to our board
        if taken_move is not None:
            self.board.push(taken_move)

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
                        game_history: GameHistory):
        try:
            # if the engine is already terminated then this call will throw an exception
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass
