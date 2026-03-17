import tkinter as tk
from board import ChessBoardGUI, RawChessBoard
import time
from agent import MonteCarloChessAgent, RandomChessAgent
from board import MAX_NUM_PLY
import sys

def play_game(first_color_to_move, board: ChessBoardGUI, agent1: RandomChessAgent, agent2: MonteCarloChessAgent, game_root: tk.Tk):
	num_of_plys_so_far = 0
	agents: list[RandomChessAgent | MonteCarloChessAgent] = [agent1, agent2]

	current_color_to_play  = None
	current_idx_agent_to_play = None

	#first move
	for agent_idx in range(len(agents)):
		agent = agents[agent_idx]
		if agent.color == first_color_to_move:
			current_idx_agent_to_play = agent_idx

			#make move for appropriate agent
			src_row, src_col, dest_row, dest_col = agent.get_next_move(board, is_init=True)
			board.move_piece(agent.color, src_row, src_col, dest_row, dest_col)

			current_idx_agent_to_play = 1 - current_idx_agent_to_play
			current_color_to_play = 'black' if agent.color == 'white' else 'white'
			num_of_plys_so_far += 1
			print("Move {0} made".format(num_of_plys_so_far))
			break


	#refresh game view
	game_root.update()

	#rest of the game moves

	while not board.uboard.is_terminal(current_color_to_play) and num_of_plys_so_far <= MAX_NUM_PLY:
		current_agent_to_play = agents[current_idx_agent_to_play]
		current_idx_agent_to_play = 1 - current_idx_agent_to_play
		
		src_row, src_col, dest_row, dest_col = current_agent_to_play.get_next_move(board)
		board.move_piece(current_agent_to_play.color, src_row, src_col, dest_row, dest_col)
		game_root.update()
		time.sleep(5)
		num_of_plys_so_far += 1
		
		print("Move {0} made".format(num_of_plys_so_far))
		
		checkmate_status = board.uboard.find_king_in_checkmate()
		if checkmate_status:
			print(checkmate_status, 'lost')
			sys.exit(0)
			
	print('Game over. Winner to be determined by material')

def main():
	root = tk.Tk()
	root.title("Auto chess")

	rboard = RawChessBoard()
	board = ChessBoardGUI(root, rboard)

	curr_color_to_move = 'white'
	agent1 = RandomChessAgent(curr_color_to_move) #random agent will play first
	agent2 = MonteCarloChessAgent('black', opponent = agent1)

	#UNCOMMENT THIS LINE to start game
	#root.after(3000, play_game, curr_color_to_move, board, agent1, agent2, root) #will start playing after 3 seconds
	
	root.mainloop()

if __name__ == "__main__":
	main()
