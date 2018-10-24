#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction

# This library allows you to generate random numbers.
import random
import time
# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

from hlt.pathing import *





""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
ship_status = {}
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("Shamrodia74's bot")
cells_to_free = []


# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:
	tic = time.time()
	# This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
	#   running update_frame().
	game.update_frame()
	# You extract player metadata and the updated map metadata here for convenience.
	me = game.me
	game_map = game.game_map
	directions = Direction.get_all_cardinals()
	# A command queue holds all the commands you will run this turn. You build this list up and submit it at the
	#   end of the turn.
	command_queue = []
	ship_moves = []
	for ship in me.get_ships():
		logging.info("Calculating ship {}".format(ship.id))
		if ship.position in cells_to_free:
			direction = find_any_safe_direction(ship,game_map,ship_moves,cells_to_free)
			if direction == Direction.Still:
				cells_to_free.append(ship.position.directional_offset(Direction.North))
			else:
				cells_to_free = [cell for cell in cells_to_free if cell != ship.position]
				cell = game_map[ship.position.directional_offset(direction)]
				cell.mark_unsafe(ship)
				ship_moves.append(cell)
				command_queue.append(ship.move(direction))
		else:

			if ship.id not in ship_status:
				ship_status[ship.id] = "leaving"


			if ship.halite_amount >= constants.MAX_HALITE / 2 and (not game_map[me.shipyard].is_occupied) :
				ship_status[ship.id] = "returning"
					
			if ship_status[ship.id] == "returning":
				if ship.position == me.shipyard.position:
					ship_status[ship.id] = "leaving"
				else:
					move = game_map.naive_navigate(ship, me.shipyard.position)
					next_cell = map_cell_from_direction(ship,move,game_map)
					if next_cell.position in cells_to_free:
						best_cost = -1000
						choice = Direction.Still
						for direction in [d for d in directions if d != move]:
							cell = ship.position.directional_offset(direction)
							cell_cost = halite_cost(ship.position, cell, game_map)
							logging.info("test: {}".format(cell))
							game_cell = game_map[cell]
							if not game_cell.is_occupied and not game_cell in ship_moves and cell_cost > best_cost:
								best_cost = cell_cost
								choice = direction
						move = choice
						
					if move == Direction.Still:
						move = find_any_safe_direction(ship,game_map,ship_moves,cells_to_free)
					next_cell = map_cell_from_direction(ship,move,game_map)
					next_cell.mark_unsafe(ship)
					ship_moves.append(next_cell)
					command_queue.append(ship.move(move))


			elif ship_status[ship.id] == "leaving":

				direction = find_safe_direction(ship,game_map,ship_moves)
				if direction == Direction.Still:
					cells_to_free.append(ship.position.directional_offset(Direction.North))
				else:
					ship_status[ship.id] = "exploring"
				next_cell = map_cell_from_direction(ship,direction,game_map)
				next_cell.mark_unsafe(ship)
				ship_moves.append(next_cell)
				command_queue.append(ship.move(direction))

			else:
				best_cell = choose_best_move(ship,game_map,me.shipyard,radius=20)
				move = game_map.naive_navigate(ship, best_cell.position)
				next_cell = cell_from_direction(ship.position,move,game_map)
				if next_cell.position in cells_to_free:
					best_cost = -1000
					choice = Direction.Still
					choices = [d for d in directions if d != move]
					for direction in choices:
						cell = ship.position.directional_offset(direction)
						cell_cost = halite_cost(ship.position, cell, game_map)
						game_cell = game_map[cell]
						if (not game_cell.is_occupied) and game_cell not in ship_moves and cell_cost > best_cost:
							best_cost = cell_cost
							choice = direction
					move = choice
				next_cell = cell_from_direction(ship.position,move,game_map)
				ship_moves.append(next_cell)
				next_cell.mark_unsafe(ship)
				command_queue.append(ship.move(move))

	logging.info("ship_status {}".format(ship_status))
	logging.info("Cells to free {}".format(cells_to_free))
	if game.turn_number <= 150 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied and len(me.get_ships())<100:
		command_queue.append(me.shipyard.spawn())

	# Send your moves back to the game environment, ending this turn.
	tac = time.time()
	game.end_turn(command_queue)
	logging.info("Time for turn = {}s".format(tac-tic))