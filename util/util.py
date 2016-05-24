"""Utility File."""
import math
# import pdb
import conf
from tabulate import tabulate


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


def print_lineup(lineup, gen):
    """Print the full lineup and its fitness, salary, and proj. points."""
    print tabulate(
        sorted(lineup_dict_to_list(lineup), key=lambda x: (x[1], x[5])),
        headers=['name', 'team', 'pos', 'cost', 'points', 'batting_pos'],
        tablefmt="pretty")
    print "\nFitness: %s" % gen.fitness(lineup)
    print "Salary: %s" % gen.get_team_salary(lineup)
    print "Projected Points: %s" % gen.get_team_point_total(lineup)
    print '\n'


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
    team = player['team']
    name = player['name']
    new_player.append(name)
    new_player.append(team)
    new_player.append(player['pos'])
    new_player.append(player['cost'])
    new_player.append(player['value'])
    try:
        if name in conf.batting_orders[team]:
            new_player.append(
                conf.batting_orders[team].index(name) + 1)
        else:
            new_player.append('NL')
    except:
        new_player.append('NL')
    return new_player
