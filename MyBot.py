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

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

from hlt.pathing import *





""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
ship_status = {}
nb_returning = 0
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("Shamrodia74's bot")



# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """

while True:
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
		if ship.id not in ship_status:
			ship_status[ship.id] = "leaving"

		if ship_status[ship.id] == "returning":
			if ship.position == me.shipyard.position:
				ship_status[ship.id] = "leaving"
				

			else:
				move = game_map.naive_navigate(ship, me.shipyard.position)
				next_cell = map_cell_from_direction(ship,move,game_map)
				next_cell.mark_unsafe(ship)
				ship_moves.append(next_cell)
				command_queue.append(ship.move(move))
				continue

		elif ship.halite_amount >= constants.MAX_HALITE / 3 and nb_returning < 5 :
			ship_status[ship.id] = "returning"
			nb_returning += 1

		elif ship_status[ship.id] == "leaving":

			direction = directions[0]
			i = 0
			while i<len(directions)-1 and map_cell_from_direction(ship,direction,game_map).is_occupied:
				i += 1
				direction = directions[i]

			next_cell = map_cell_from_direction(ship,direction,game_map)
			next_cell.mark_unsafe(ship)
			ship_moves.append(next_cell)
			command_queue.append(ship.move(direction))

			ship_status[ship.id] = "exploring"
			nb_returning -= 1
		else:
			best_cell = choose_best_move(ship,game_map,me.shipyard,radius=10)
			move = game_map.naive_navigate(ship, best_cell.position)
			next_cell = cell_from_direction(ship.position,move,game_map)
			ship_moves.append(next_cell)
			next_cell.mark_unsafe(ship)
			command_queue.append(ship.move(move))

	logging.info("ship_status {}".format(ship_status))
	
	if game.turn_number <= 200 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
		command_queue.append(me.shipyard.spawn())

	# Send your moves back to the game environment, ending this turn.
	game.end_turn(command_queue)