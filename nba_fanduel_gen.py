"""Generates Lineups for NBA FanDuel Scoring."""
from scrapers.numberfire_scraper import\
    retrieve_numberfire_nba_predictions_and_salaries
from tabulate import tabulate
import numpy as np
import conf
from util.util import is_number, lineup_dict_to_list
from lineup_optimizers.genetic_nba import GeneticNBA
import pdb

batter_df_numberfire = retrieve_numberfire_nba_predictions_and_salaries()
# merged_df = batter_df_numberfire.join(batter_df_sabersim, on=None, how='left', lsuffix='_nf', rsuffix='_ss')
position_results = {
    'PG': [],
    'PF': [],
    'C': [],
    'SG': [],
    'SF': []
}

players = []
"""PLAYER CONSOLIDATION"""
for batter in batter_df_numberfire.iterrows():
    player_info = batter[1]
    player_name = batter[0]
    # Skip specified players and teams
    if player_name in conf.excluded_nba_players or\
            player_info['nf_team'] in conf.excluded_nba_teams:
        continue
    player_cost = float(player_info['nf_cost'].replace('$', ''))
    if player_info['nf_pos'] in position_results:
        position_results[player_info['nf_pos']].append(
            [player_name.decode('utf-8'), player_info['nf_team'].decode('utf-8'), player_cost, player_info['nf_min'].decode('utf-8'),
             float(player_info['nf_pred'].decode('utf-8'))])
        players.append({
            "value": float(player_info['nf_pred']),
            "cost": player_cost,
            "pos": player_info['nf_pos'],
            "name": player_name,
            "team": player_info['nf_team'],
            "opp": player_info['nf_opp_team'].replace('@', ''),
            "min": float(player_info['nf_min']),
        })

"""OUTPUT PROJECTIONS"""
print'\n'

print "Center Projections"
print tabulate(sorted(position_results['C'], key=lambda player: player[4],
    reverse=True), headers=["Name", "Team", "Cost", "Min Pts", "Numberfire Pred"], tablefmt="plain")

print '\n'

print "Power Forward Projections"
print tabulate(sorted(position_results['PF'], key=lambda player: player[4],
    reverse=True), headers=["Name", "Team", "Cost", "Min Pts", "Numberfire Pred"], tablefmt="plain")

print '\n'

print "Point Guard Projections"
print tabulate(sorted(position_results['PG'], key=lambda player: player[4],
    reverse=True), headers=["Name", "Team", "Cost", "Min Pts", "Numberfire Pred"], tablefmt="plain")

print '\n'

print "Shooting Guard Projections"
print tabulate(sorted(position_results['SG'], key=lambda player: player[4],
    reverse=True), headers=["Name", "Team", "Cost", "Min Pts", "Numberfire Pred"], tablefmt="plain")

print '\n'

print "SF Projections"
print tabulate(sorted(position_results['SF'], key=lambda player: player[4],
    reverse=True), headers=["Name", "Team", "Cost", "Min Pts", "Numberfire Pred"], tablefmt="plain")

print '\n'

"""GENERATE LINEUPS"""
print "\nTOP GENETIC AVERAGED LINEUPS"
gen = GeneticNBA(conf.nba_max_salary)
lineups = gen.calculate(players)
print "Number 1"
print tabulate(lineup_dict_to_list(lineups[0]), headers=['name', 'team', 'pos', 'cost', 'points'], tablefmt="pretty")
print '\n'
print "Number 2"
print tabulate(lineup_dict_to_list(lineups[1]), headers=['name', 'team', 'pos', 'cost', 'points'],tablefmt="pretty")
print '\n'
print "Number 3"
print tabulate(lineup_dict_to_list(lineups[2]), headers=['name', 'team', 'pos', 'cost', 'points'],tablefmt="pretty")
print '\n'
print "Number 4"
print tabulate(lineup_dict_to_list(lineups[3]), headers=['name', 'team', 'pos', 'cost', 'points'],tablefmt="pretty")
print '\n'
print "Number 5"
print tabulate(lineup_dict_to_list(lineups[4]), headers=['name', 'team', 'pos', 'cost', 'points'],tablefmt="pretty")
print '\n'
print "Number 6"
print tabulate(lineup_dict_to_list(lineups[5]), headers=['name', 'team', 'pos', 'cost', 'points'],tablefmt="pretty")
print '\n'
print "Number 7"
print tabulate(lineup_dict_to_list(lineups[6]), headers=['name', 'team', 'pos', 'cost', 'points'],tablefmt="pretty")
print '\n'
print "Number 8"
print tabulate(lineup_dict_to_list(lineups[7]), headers=['name', 'team', 'pos', 'cost', 'points'],tablefmt="pretty")
print '\n'
print "Number 9"
print tabulate(lineup_dict_to_list(lineups[8]), headers=['name', 'team', 'pos', 'cost', 'points'],tablefmt="pretty")
print '\n'
print "Number 10"
print tabulate(lineup_dict_to_list(lineups[9]), headers=['name', 'team', 'pos', 'cost', 'points'],tablefmt="pretty")
print '\n'

