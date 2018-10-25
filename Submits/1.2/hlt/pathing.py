import hlt
from hlt import constants
from hlt.positionals import Direction
from hlt.game_map import GameMap
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

def cell_from_direction(position,direction,game_map):
    next_position = game_map.normalize(position.directional_offset(direction))
    cell = game_map[next_position]
    return cell


def map_cell_from_direction(ship,direction,game_map):
    position = ship.position.directional_offset(direction)
    cell = game_map[position]
    return cell

def halite_cost(source,target,game_map):
    cost = 0
    current_pos = source
    while current_pos != target:
        possible_moves = GameMap._get_target_direction(current_pos, target)
        best = 1001 
        choice = Direction.Still
        for direction in possible_moves:
            if direction == None:
                continue
            direction_cost = cell_from_direction(current_pos, direction, game_map).halite_amount/constants.MOVE_COST_RATIO
            if direction_cost < best:
                choice = direction
                best = direction_cost
        cost += direction_cost
        current_pos = current_pos.directional_offset(choice)
    return cost

def cost(ship,target,dropoff,game_map):
    target_cell = game_map[target]
    halite_amount = target_cell.halite_amount / constants.EXTRACT_RATIO
    ship_to_target = halite_cost(ship.position, target, game_map)
    target_to_dropoff = halite_cost(target, dropoff, game_map)
    return halite_amount - ship_to_target - target_to_dropoff
