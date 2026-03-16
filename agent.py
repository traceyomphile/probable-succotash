from random import choice
from board import RawChessBoard, ChessBoardGUI
import copy
import math

class MonteCarloChessAgent(object):
	def __init__(self, color, opponent):
		self.color = color
		self.opponent = opponent


	def get_next_move(self, board): #must return src_row, src_col, dest_row, dest_col
		#TODO: complete
		return 0,0,0,0


class RandomChessAgent(object):
	def __init__(self, color):
		self.color = color

	def get_next_move(self, board: RawChessBoard, is_init=False): #must return src_row, src_col, dest_row, dest_col
		playable_moves = board.get_playable_moves(self.color)

		if is_init:
			rnd_move = choice(_get_init_moves(board, playable_moves))
			return rnd_move['src_row'], rnd_move['src_col'], rnd_move['dest_row'], rnd_move['dest_col']
		
		if board.is_check(self.color):
			rnd_move = choice(_get_king_playable_moves(board, playable_moves))
			return rnd_move['src_row'], rnd_move['src_col'], rnd_move['dest_row'], rnd_move['dest_col']
		
		rnd_move = choice(_get_playable_moves(board, playable_moves))
		return rnd_move['src_row'], rnd_move['src_col'], rnd_move['dest_row'], rnd_move['dest_col']
		

def _get_init_moves(board: RawChessBoard, playable_moves):
	valid_moves = []

	for move in playable_moves:
		if move['row'] in (1, 6):
			valid_moves.extend(_get_valid_moves(move))
		elif move['row'] in (0, 7) and move['col'] in (1, 6):
			valid_moves.extend(_get_valid_moves(move))
	return valid_moves

def _get_king_playable_moves(board: RawChessBoard, playable_moves):
	king_moves = []
	for km in playable_moves:
		if km['piece'].lower() == 'k':
			king_moves.extend(_get_valid_moves(km))
	return king_moves

def _get_playable_moves(board:RawChessBoard, playable_moves, ):
	valid_moves = []
	
	for move in playable_moves:
		valid_moves.extend(_get_valid_moves(move))
	return valid_moves

def _get_valid_moves(board: RawChessBoard, playable_move):	
		valid_moves = []
		for move in playable_move['moves']:
			if board.is_position_empty(move[0], move[1]) or board.is_capture(playable_move['row'], playable_move['col'], move[0], move[1]):
				valid_moves.append({'src_row': playable_move['row'], 'src_col': playable_move['col'], 'dest_row': move[0], 'dest_col': move[1]})
		return valid_moves

