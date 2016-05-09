"""Generates Lineups for MLB FanDuel Scoring."""
from scrapers.sabersim_scraper import retrieve_saber_sim_player_predictions
from scrapers.numberfire_scraper import\
    retrieve_numberfire_mlb_predictions_and_salaries
from score_calculators import calculate_fanduel_hitter_score, calculate_fanduel_pitcher_score
from tabulate import tabulate
import numpy as np
import conf
from util import is_number, lineup_dict_to_list
from lineup_optimizers.genetic_mlb import GeneticMLB
from lineup_optimizers.knapsack_mlb import Knapsack
import pdb

batter_df_sabersim = retrieve_saber_sim_player_predictions()
batter_df_numberfire, pitcher_df_numberfire =\
    retrieve_numberfire_mlb_predictions_and_salaries()
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
players_ss = []

"""BATTER CONSOLIDATION"""
for batter in merged_df.iterrows():
    batter_info = batter[1]
    batter_name = batter[0]
    # Skip specified batters
    if batter_name in conf.excluded_batters or\
            batter_info['nf_team'] in conf.excluded_teams:
        continue
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
        avg_score = float(batter_info['nf_pred'])
    else:
        continue
    player_cost = float(batter_info['nf_cost'].replace('$', ''))
    if batter_info['nf_pos'] in position_results:
        position_results[batter_info['nf_pos']].append(
            [batter_name.decode('utf-8'), batter_info['nf_team'].decode('utf-8'), player_cost, ss_score,
             batter_info['nf_pred'].decode('utf-8'), avg_score])
        players.append({
            "value": avg_score,
            "cost": player_cost,
            "pos": batter_info['nf_pos'],
            "name": batter_name,
            "team": batter_info['nf_team'],
            "opp": batter_info['nf_opp_team'].replace('@', '')
        })
        if is_number(ss_score):
            players_ss.append({
                "value": ss_score,
                "cost": player_cost,
                "pos": batter_info['nf_pos'],
                "name": batter_name,
                "team": batter_info['nf_team'],
                "opp": batter_info['nf_opp_team'].replace('@', '')
            })

"""PITCHER CALCULATIONS"""
pitchers_overall = []
for pitcher in pitcher_df_numberfire.iterrows():
    pitcher_info = pitcher[1]
    pitcher_name = pitcher[0]
    pitcher_cost = float(pitcher_info['nf_cost'].replace('$', ''))
    if pitcher_name in conf.excluded_pitchers or\
            pitcher_info['nf_team'] in conf.excluded_teams:
        continue
    # def calculate_fanduel_pitcher_score(er, ip, so, win):
    # return (3.0 * er) + (6.0 * ip) + (9.0 * so) + (3.0 * win)
    if is_number(pitcher_info['nf_pred']):
        players.append({
            "value": float(pitcher_info['nf_pred']),
            "cost": pitcher_cost,
            "pos": pitcher_info['nf_pos'],
            "name": pitcher_name,
            "team": pitcher_info['nf_team'],
            "opp": pitcher_info['nf_opp_team'].replace('@', '')
        })
        players_ss.append({
            "value": float(pitcher_info['nf_pred']),
            "cost": pitcher_cost,
            "pos": pitcher_info['nf_pos'],
            "name": pitcher_name,
            "team": pitcher_info['nf_team'],
            "opp": pitcher_info['nf_opp_team'].replace('@', '')
        })
        pitchers_overall.append([pitcher_name, pitcher_info['nf_team'], pitcher_cost, float(pitcher_info['nf_pred']), pitcher_info['nf_value']])


"""OUTPUT PROJECTIONS"""
print "Pitcher Projections"
print tabulate(sorted(pitchers_overall, key=lambda player: player[4],
    reverse=True), headers=["Name", "Team", "Cost", "Numberfire Pred", "Value"], tablefmt="plain")

print'\n'

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

"""GENERATE LINEUPS"""
print "\nTOP GENETIC AVERAGED LINEUPS"
gen = GeneticMLB(conf.max_salary)
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

print "TOP GENETIC SABERSIM LINEUPS"
lineups = gen.calculate(players_ss)
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

print "TOP KNAPSACK LINEUP"
ks = Knapsack(conf.max_salary)
print tabulate(ks.calculate(players), tablefmt="pretty")
print'\n'
