"""Utility File."""
import math
import pdb
import conf
from tabulate import tabulate
import numpy as np


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


def print_top_df_lineups(lineup_list, gen, num=10):
    for i in xrange(num):
        print '\nLineup %d:' % (i + 1)
        print_df_lineup(lineup_list[i], gen)


def print_df_lineup(lineup, gen):
    """Print the full lineup of dataframe objects and its fitness, salary, and proj. points."""
    print tabulate(
        sorted(df_lineup_dict_to_list(lineup), key=lambda x: (x[1], x[5])),
        headers=['name', 'team', 'pos', 'cost', 'mean', 'batting_pos'],
        tablefmt="pretty")
    print "\nFitness: %s" % gen.fitness(lineup)
    print "Salary: %s" % gen.get_team_salary(lineup)
    print '\n'


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


"""DATA FRAME OPTIONS"""
def df_lineup_dict_to_list(dict_list):
    """
    Convert a lineup dictionary to a list.

    Stores in the format name, team, pos, cost, value.
    """
    final_list = []
    for entry in dict_list:
        for player in dict_list[entry]:
            final_list.append(player_df_dict_to_list(player))
    return final_list

def player_df_dict_to_list(player):
    new_player = []
    team = player.loc['team']
    name = player.name
    new_player.append(name)
    new_player.append(team)
    new_player.append(player.loc['pos'])
    new_player.append(player.loc['cost'])
    new_player.append(get_player_projection_mean(player))
    try:
        if name in conf.batting_orders[team]:
            new_player.append(
                conf.batting_orders[team].index(name) + 1)
        else:
            new_player.append('NL')
    except:
        new_player.append('NL')
    return new_player


def get_player_projection_mean(player):
    proj = []
    for i in xrange(conf.simulated_game_count):
        proj.append(player.loc[str(i)])
    return np.mean(proj)


"""NON DATA FRAME OPTIONS"""
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


def standardize_team_name(name):
    if name in conf.long_to_short_names:
        return conf.long_to_short_names[name]
    elif name not in conf.short_to_long_names:
        return "Do not cover %s" % name
    return conf.long_to_short_names[
        conf.short_to_long_names[name]]
