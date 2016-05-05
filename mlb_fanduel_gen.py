"""Generates Lineups for MLB FanDuel Scoring"""
from scrapers.sabersim_scraper import retrieve_saber_sim_player_predictions
from scrapers.numberfire_scraper import retrieve_numberfire_batter_predictions_and_salaries
from score_calculators import calculate_fanduel_hitter_score
from tabulate import tabulate
import numpy as np
from util import is_number
from lineup_optimizer import Knapsack
import pdb

batter_df_sabersim = retrieve_saber_sim_player_predictions()
batter_df_numberfire = retrieve_numberfire_batter_predictions_and_salaries()
merged_df = batter_df_numberfire.join(batter_df_sabersim, on=None, how='left', lsuffix='_nf', rsuffix='_ss')
position_results = {
    'SS': [],
    '1B': [],
    '2B': [],
    '3B': [],
    'C': [],
    'OF': []
}

players = []

for batter in merged_df.iterrows():
    batter_info = batter[1]
    batter_name = batter[0]
    # sing, doub, trip, walk, hbp, hr, runs, rbi, sb
    ss_score = calculate_fanduel_hitter_score(
        float(batter_info['ss_h']) * .65, float(batter_info['ss_h']) * .2,
        float(batter_info['ss_h']) * .05, float(batter_info['ss_bb']), 0,
        float(batter_info['ss_hr']), float(batter_info['ss_r']), float(batter_info['ss_rbi']),
        float(batter_info['ss_sb']))
    avg_score = None
    if is_number(ss_score) and is_number(batter_info['nf_pred']):
        avg_score = np.mean([float(ss_score), float(batter_info['nf_pred'])])
    elif is_number(batter_info['nf_pred']):
        avg_score = batter_info['nf_pred']
    elif is_number(ss_score):
        avg_score = ss_score
    player_cost = float(batter_info['nf_cost'].replace('$', ''))
    if batter_info['nf_pos'] in position_results:
        position_results[batter_info['nf_pos']].append(
            [batter_name, batter_info['nf_team'], player_cost, ss_score,
             batter_info['nf_pred'], avg_score])
        players.append((avg_score, player_cost, batter_info['nf_pos'], batter_name))


print "Short Stop Projections"
print tabulate(sorted(position_results['SS'], key=lambda player: player[5],
    reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Numberfire Pred", "Avg Proj"], tablefmt="plain")

print '\n'

print "First Base Projections"
print tabulate(sorted(position_results['1B'], key=lambda player: player[5],
    reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Numberfire Pred", "Avg Proj"], tablefmt="plain")

print '\n'

print "Second Base Projections"
print tabulate(sorted(position_results['2B'], key=lambda player: player[5],
    reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Numberfire Pred", "Avg Proj"], tablefmt="plain")

print '\n'

print "Third Base Projections"
print tabulate(sorted(position_results['3B'], key=lambda player: player[5],
    reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Numberfire Pred", "Avg Proj"], tablefmt="plain")

print '\n'

print "Catcher Projections"
print tabulate(sorted(position_results['C'], key=lambda player: player[5],
    reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Numberfire Pred", "Avg Proj"], tablefmt="plain")

print '\n'

print "OF Projections"
print tabulate(sorted(position_results['OF'], key=lambda player: player[5],
    reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Numberfire Pred", "Avg Proj"], tablefmt="plain")

ks = Knapsack(35000)
print ks.calculate(players)
