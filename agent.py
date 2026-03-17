from random import choice
from board import RawChessBoard, ChessBoardGUI, MAX_NUM_PLY
import copy
import math

class MonteCarloChessAgent(object):
	def __init__(self, color: str, opponent: 'RandomChessAgent'):
		self.color = color
		self.opponent = opponent


	def get_next_move(self, board: ChessBoardGUI): #must return src_row, src_col, dest_row, dest_col
		ply_mvs = None
		if board.uboard.number_of_total_moves == 1: 	# Init state, only black played.
			ply_mvs = _get_playable_moves(board.uboard, self.color, is_init=True, in_check=False)
		else:
			ply_mvs = _get_playable_moves(board.uboard, self.color, is_init=False, in_check=board.uboard.is_check(self.color))
		tree = NODE(board, ply_mvs, self.color)

		# Textbook MCTS algorithm
		for _ in range(MAX_NUM_PLY):
			leaf = tree.SELECTION()
			leaf.EXPAND()
			for child in leaf.CHILDREN:
				child.SIMULATE(self.opponent)
				child.BACK_PROPAGATE()

		next_move = tree.get_max_sim_node()
		return next_move['src_row'], next_move['src_col'], next_move['dest_row'], next_move['dest_col']

			

class RandomChessAgent(object):
	def __init__(self, color):
		self.color = color

	def get_next_move(self, board: ChessBoardGUI, is_init=False): #must return src_row, src_col, dest_row, dest_col
		moves = _get_playable_moves(board.uboard, self.color, is_init, board.uboard.is_check(self.color))
		
		rnd_move = choice(moves)
		return rnd_move['src_row'], rnd_move['src_col'], rnd_move['dest_row'], rnd_move['dest_col']
		

def _get_init_moves(board: RawChessBoard, playable_moves):
	valid_moves = []

	for move in playable_moves:
		if move['row'] in (1, 6):
			valid_moves.extend(_get_valid_moves(board, move))
		elif move['row'] in (0, 7) and move['col'] in (1, 6):
			valid_moves.extend(_get_valid_moves(board, move))
	return valid_moves

def _get_king_playable_moves(board: RawChessBoard, playable_moves):
	king_moves = []
	for km in playable_moves:
		if km['piece'].lower() == 'k':
			king_moves.extend(_get_valid_moves(board, km))
	return king_moves

def _get_playable_moves(board:RawChessBoard, color, is_init=False, in_check=False):
	playable_moves = board.get_playable_moves(color)	
	valid_moves = []

	if is_init:
		return _get_init_moves(board, playable_moves)
	
	if in_check:
		return _get_king_playable_moves(board, playable_moves)
		
	for move in playable_moves:
		valid_moves.extend(_get_valid_moves(board, move))
	return valid_moves

def _get_valid_moves(board: RawChessBoard, playable_move):	
		valid_moves = []

		for move in playable_move['moves']:
			if board.is_position_empty(move[0], move[1]) or board.is_capture(playable_move['row'], playable_move['col'], move[0], move[1]):
				valid_moves.append({'src_row': playable_move['row'], 'src_col': playable_move['col'], 'dest_row': move[0], 'dest_col': move[1]})
		return valid_moves

def _UCB1(node: NODE):
	mean = node.WINS / node.SIMULATIONS
	explore_val = math.sqrt((2 * math.log(node.PARENT.SIMULATIONS)) / node.SIMULATIONS)

	return mean + explore_val

def _captures_first(board: RawChessBoard, playable_moves):
	capturing_moves = []
	for move in playable_moves:
		if board.is_capture(move['src_row'], move['src_col'], move['dest_row'], move['dest_col']):
			capturing_moves.append(move)
	
	return capturing_moves

def _check_giving_moves(board: RawChessBoard, playable_moves):
	check_giving_moves = []
	for move in playable_moves:
		if board.gives_check(move['src_row'], move['src_col'], move['dest_row'], move['dest_col']):
			check_giving_moves.append(move)
	
	return check_giving_moves

def _random_moves(playable_moves):
	return choice(playable_moves)

def _get_next_move(board: RawChessBoard, playable_moves):
	captures_first = _captures_first(board, playable_moves)
	if len(captures_first) != 0:
		return choice(captures_first)
	
	gives_check = _check_giving_moves(board, playable_moves)
	if len(gives_check) != 0:
		return choice(gives_check)
	
	return _random_moves(playable_moves)

class NODE(object):
	def __init__(self, STATE: ChessBoardGUI, ACTIONS, COLOR):
		self.STATE = STATE
		self.ACTIONS = ACTIONS
		self.WINS = 0		# Initially zero
		self.SIMULATIONS = 0	# Initially zero
		self.PARENT: NODE = None		# Intiially root node
		self.CHILDREN: list[NODE] = []			# Initally empty
		self.COLOR = COLOR

	def EXPAND(self):
		# Here calling node is a leaf
		states_after_moves = [copy.deepcopy(self.STATE.uboard.get_state_after_move(self.COLOR, a['src_row'], a['src_col'], a['dest_row'], a['dest_col'])) for a in self.ACTIONS]
		
		for state in states_after_moves:
			rboard = RawChessBoard(state, self.STATE.uboard.number_of_total_moves+1, self.STATE.uboard.game_status)
			new_state = ChessBoardGUI(self.STATE.master, rboard)
			child_node = NODE(
				new_state, 
				_get_playable_moves(
					new_state.uboard, 
					'black' if self.COLOR == 'white' else 'white', 
					is_init=new_state.uboard.number_of_total_moves == 1, 
					in_check=new_state.uboard.is_check(self.COLOR)
					),
				'black' if self.COLOR == 'white' else 'white'
			)
			child_node.PARENT= self
			self.CHILDREN.append(child_node)

	def SELECTION(self):
		# Base case 1: calling node is a tree/root node
		if self.PARENT is None:		# No selection for root node
			return NODE(self.STATE, self.ACTIONS, self.COLOR)
		
		# Base case 2:
		if self.PARENT.SIMULATIONS == 0 or self.SIMULATIONS == 0:
			return NODE(self.STATE, self.ACTIONS, self.COLOR)
		
		# Use UCB1 to select for none root node.
		child_UCB1s = [_UCB1(child) for child in self.CHILDREN]

		max_ucb = max(child_UCB1s)
		max_idx = child_UCB1s.index(max_ucb)
		return self.CHILDREN[max_idx].SELECTION()
	
	def SIMULATE(self, opponent: RandomChessAgent):
		board = copy.deepcopy(self.STATE.uboard.board)
		current_state = ChessBoardGUI(
			self.STATE.master,
			RawChessBoard(board, 
				self.STATE.uboard.number_of_total_moves, 
				self.STATE.uboard.game_status
			)
		)

		# Initially color is white
		color = 'white'

		while not current_state.uboard.is_terminal(color):
			move = None
			if color == 'white':
				move = opponent.get_next_move(current_state, current_state.uboard.number_of_total_moves == 0)
				current_state.move_piece(color, move[0], move[1], move[2], move[3])
			else:
				move = _get_next_move(current_state.uboard, self.ACTIONS)
				current_state.move_piece(color, move['src_row'], move['src_col'], move['dest_row'], move['dest_col'])
			color = 'black' if color == 'white' else 'white'

		loss_color = current_state.uboard.find_king_in_checkmate()
		if loss_color is None or (self.COLOR == loss_color):
			self.WINS += 0
		else:
			self.WINS += 1
		self.SIMULATIONS += 1
		
	def BACK_PROPAGATE(self):
		# Base case 1: Root node
		if self.PARENT is None:
			return
		
		for child in self.CHILDREN:
			self.PARENT.WINS += child.WINS
			self.PARENT.SIMULATIONS += child.SIMULATIONS
		return self.PARENT.BACK_PROPAGATE()
	
	def get_max_sim_node(self):
		max_sim = max([child.SIMULATIONS for child in self.CHILDREN])
		max_sim_idx = self.CHILDREN.index(max_sim)
		return self.ACTIONS[max_sim_idx]
