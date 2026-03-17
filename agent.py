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
		tree = NODE(board.uboard, ply_mvs, self.color)

		# Textbook MCTS algorithm
		for _ in range(MAX_NUM_PLY):
			leaf = tree.SELECTION()
			leaf.EXPAND()
			for child in leaf.CHILDREN:
				sim_res = child.SIMULATE(self.opponent)
				child.BACK_PROPAGATE(sim_res[0], sim_res[1])

		next_move = tree.get_max_sim_node()
		return next_move['src_row'], next_move['src_col'], next_move['dest_row'], next_move['dest_col']
			
class RandomChessAgent(object):
	def __init__(self, color):
		self.color = color

	def get_next_move(self, board: ChessBoardGUI, is_init=False): #must return src_row, src_col, dest_row, dest_col
		moves = _get_playable_moves(board.uboard, self.color, is_init, board.uboard.is_check(self.color))
		
		# Terminal state
		if not moves:
			return None, None, None, None
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
	explore_val = 1.14 * math.sqrt((math.log(node.PARENT.SIMULATIONS)) / node.SIMULATIONS)

	return mean + explore_val

def _captures_first(board: RawChessBoard, playable_moves):
	capturing_moves = []
	for move in playable_moves:
		if board.board[move['src_row']][move['src_col']] is None:
			continue

		if board.is_capture(move['src_row'], move['src_col'], move['dest_row'], move['dest_col']):
			capturing_moves.append(move)
	
	return capturing_moves

def _check_giving_moves(board: RawChessBoard, playable_moves):
	check_giving_moves = []
	for move in playable_moves:
		if board.board[move['src_row']][move['src_col']] is None:
			continue

		if board.gives_check(move['src_row'], move['src_col'], move['dest_row'], move['dest_col'], 'white'):	# Opponent is always 'white
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
	def __init__(self, STATE: RawChessBoard, ACTIONS, COLOR):
		self.STATE = STATE
		self.ACTIONS = ACTIONS
		self.WINS = 0		# Initially zero
		self.SIMULATIONS = 0	# Initially zero
		self.PARENT: NODE = None		# Intiially root node
		self.CHILDREN: list[NODE] = []			# Initally empty
		self.COLOR = COLOR

	def EXPAND(self):
		if self.CHILDREN:
			return
		
		# Give unvisited children infinite priority
		for a in self.ACTIONS:
			safe_board = RawChessBoard(
				copy.deepcopy(self.STATE.board),
				self.STATE.number_of_total_moves,
				self.STATE.game_status
			)

			new_sate = RawChessBoard(
				safe_board.get_state_after_move(self.COLOR, a['src_row'], a['src_col'], a['dest_row'], a['dest_col']),
				self.STATE.number_of_total_moves+1,
				self.STATE.game_status
			)

			child_node = NODE(
				new_sate,
				_get_playable_moves(
					new_sate,
					'black' if self.COLOR == 'white' else 'white',
					is_init=False,
					in_check=new_sate.is_check(self.COLOR)
				),
				'black' if self.COLOR == 'white' else 'white'
			)
			child_node.PARENT = self
			self.CHILDREN.append(child_node)

	def SELECTION(self):
		# Base case : Unexpanded leaf
		if not self.CHILDREN:
			return self
		
		# Give unvisited children infinite priority
		child_UCB1s = [_UCB1(child) if child.SIMULATIONS > 0 else float('inf') for child in self.CHILDREN]

		max_ucb = max(child_UCB1s)
		max_idx = child_UCB1s.index(max_ucb)
		return self.CHILDREN[max_idx].SELECTION()
	
	def SIMULATE(self, opponent: RandomChessAgent):
		current_state = RawChessBoard(
			copy.deepcopy(self.STATE.board),
			self.STATE.number_of_total_moves, 
				self.STATE.game_status
		)

		# Initially color is white
		color = 'white'

		while not current_state.is_terminal(color):
			if color == 'white':
				# Wrap is a minimal object so RandomChessAgent's interface still works
				class _Wrap: uboard = current_state
				move = opponent.get_next_move(_Wrap, is_init=False)		# Mid game
				if move[0] is None:		# Guard against empty current positions
					break

				current_state.move_piece(color, move[0], move[1], move[2], move[3])
			else:
				playable_moves = _get_playable_moves(current_state, color, is_init=False, in_check=current_state.is_check(color))
				if not playable_moves:
					break
				
				move = _get_next_move(current_state, playable_moves)
				current_state.move_piece(color, move['src_row'], move['src_col'], move['dest_row'], move['dest_col'])
			color = 'black' if color == 'white' else 'white'

		loss_color = current_state.find_king_in_checkmate()
		if loss_color is None or (self.COLOR == loss_color):
			self.WINS = 0
		else:
			self.WINS = 1
		self.SIMULATIONS = 1
		return self.WINS, self.SIMULATIONS
		
	def BACK_PROPAGATE(self, delta_wins, delta_sims):
		# On first call, delta is the result of the just completed simulation
		if delta_wins is None:
			delta_wins = self.WINS

		# Base case: reached root
		if self.PARENT is None:
			return
		
		self.PARENT.WINS += delta_wins
		self.PARENT.SIMULATIONS += delta_sims
		self.PARENT.BACK_PROPAGATE(delta_wins, delta_sims)
	
	def get_max_sim_node(self):
		max_sim_idx = max(range(len(self.CHILDREN)), key=lambda i: self.CHILDREN[i].SIMULATIONS)
		return self.ACTIONS[max_sim_idx]
