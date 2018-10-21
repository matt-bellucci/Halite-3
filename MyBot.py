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

directions = Direction.get_all_cardinals()

def pick_next_cell(ship,game_map,ship_moves):
    ship_pos = ship.position
    surroundings = ship_pos.get_surrounding_cardinals()
    maxi = game_map[ship_pos].halite_amount
    choice = Direction.Still
    for direction in directions:
        cell = game_map[ship_pos.directional_offset(direction)]
        if (not cell.is_empty) or (cell in ship_moves):
            continue
        else:
            if cell.halite_amount > maxi:
                choice = direction
    return choice

def map_cell_from_direction(ship,direction,game_map):
    position = ship.position.directional_offset(direction)
    cell = game_map[position]
    return cell


""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()
ship_status = {}
# At this point "game" variable is populated with initial map data.
# This is a good place to do computationally expensive start-up pre-processing.
# As soon as you call "ready" function below, the 2 second per turn timer will start.
game.ready("MyPythonBot")



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

    # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
    #   end of the turn.
    command_queue = []
    ship_moves = []
    for ship in me.get_ships():

        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"
        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
            else:
                move = game_map.naive_navigate(ship, me.shipyard.position)
                next_cell = map_cell_from_direction(ship,move,game_map)
                next_cell.mark_unsafe(ship)
                ship_moves.append(next_cell)
                command_queue.append(ship.move(move))
                continue
        elif ship.halite_amount >= constants.MAX_HALITE / 3:
            ship_status[ship.id] = "returning"

        else:
            ship_direction = pick_next_cell(ship,game_map,ship_moves)
            next_cell = map_cell_from_direction(ship,ship_direction,game_map)
            ship_moves.append(next_cell)
            next_cell.mark_unsafe(ship)
            command_queue.append(ship.move(ship_direction))


    
    if game.turn_number <= 300 and me.halite_amount >= constants.SHIP_COST and not game_map[me.shipyard].is_occupied:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

