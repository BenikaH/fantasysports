"""Utility File."""
import math
import pdb


def is_number(str):
    """Determine whether a passed value is a number."""
    if str == 'nan':
        return False
    try:
        num = float(str)
        if math.isnan(num):
            return False
        return True
    except ValueError:
        return False


def lineup_dict_to_list(dict_list):
    """
    Convert a lineup dictionary to a list.

    Stores in the format name, team, pos, cost, value.
    """
    final_list = []
    for entry in dict_list:
        for player in dict_list[entry]:
            final_list.append(player_dict_to_list(player))
    return final_list


def player_dict_to_list(player):
    """Convert player dictionary to list."""
    new_player = []
    new_player.append(player['name'])
    new_player.append(player['team'])
    new_player.append(player['pos'])
    new_player.append(player['cost'])
    new_player.append(player['value'])
    return new_player
