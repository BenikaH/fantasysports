"""Generates Lineups for MLB FanDuel Scoring."""
from scrapers.sabersim_scraper import retrieve_saber_sim_player_predictions
from scrapers.numberfire_scraper import\
    retrieve_numberfire_mlb_predictions_and_salaries
from scrapers.rotogrinder_scraper import\
    retrieve_rotogrinder_mlb_projections, retrieve_mlb_batting_order
from util.score_calculators import calculate_fanduel_hitter_score,\
    calculate_draftkings_hitter_score
from tabulate import tabulate
import numpy as np
import conf
from util.util import is_number, lineup_dict_to_list
from lineup_optimizers.genetic_mlb import GeneticMLB
import pdb


batter_df_rotogrinders, pitcher_df_rotogrinders =\
    retrieve_rotogrinder_mlb_projections()
batter_df_sabersim = retrieve_saber_sim_player_predictions()
merged_batter_df = batter_df_rotogrinders.join(batter_df_sabersim, on=None,
                                               how='left', lsuffix='_nf',
                                               rsuffix='_ss')

if conf.use_batting_orders:
    conf.batting_orders = retrieve_mlb_batting_order()


if conf.site == 'fanduel':
    batter_df_numberfire, pitcher_df_numberfire =\
        retrieve_numberfire_mlb_predictions_and_salaries()
    merged_batter_df = merged_batter_df.join(batter_df_numberfire, on=None,
                                             how='left')
    merged_pitcher_df = pitcher_df_numberfire.join(
        pitcher_df_rotogrinders, on=None, how='left', lsuffix='_nf',
        rsuffix='_rg')
elif conf.site == 'draftkings':
    merged_pitcher_df = pitcher_df_rotogrinders

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
players_rg = []
players_nf = []

"""BATTER CONSOLIDATION"""
print merged_batter_df
for batter in merged_batter_df.iterrows():
    batter_info = batter[1]
    batter_name = batter[0]
    # Skip specified batters
    if batter_name in conf.excluded_batters or\
            batter_info['rg_team'] in conf.excluded_teams:
        continue
    # sing, doub, trip, walk, hbp, hr, runs, rbi, sb
    if conf.site == 'fanduel':
        ss_score = calculate_fanduel_hitter_score(
            float(batter_info['ss_h']) * .65, float(batter_info['ss_h']) * .2,
            float(batter_info['ss_h']) * .05, float(batter_info['ss_bb']), 0,
            float(batter_info['ss_hr']), float(batter_info['ss_r']),
            float(batter_info['ss_rbi']), float(batter_info['ss_sb']))
    elif conf.site == 'draftkings':
        ss_score = calculate_draftkings_hitter_score(
            float(batter_info['ss_h']) * .65, float(batter_info['ss_h']) * .2,
            float(batter_info['ss_h']) * .05, float(batter_info['ss_bb']), 0,
            float(batter_info['ss_hr']), float(batter_info['ss_r']), float(batter_info['ss_rbi']),
            float(batter_info['ss_sb']))
    else:
        raise ValueError('Please choose either "fanduel" or "draftkings" in conf.site.')
    avg_score = None
    if conf.use_rotogrinder_scores == True:
        if is_number(ss_score) and is_number(batter_info['rg_pred']) and is_number(batter_info['nf_pred']):
            avg_score = np.mean([float(ss_score), float(batter_info['rg_pred']), float(batter_info['nf_pred'])])
        elif is_number(batter_info['rg_pred']) and is_number(batter_info['nf_pred']):
            avg_score = np.mean([float(batter_info['rg_pred']), float(batter_info['nf_pred'])])
        elif is_number(ss_score) and is_number(batter_info['nf_pred']):
            avg_score = np.mean([float(ss_score), float(batter_info['nf_pred'])])
        elif is_number(batter_info['rg_pred']) and is_number(ss_score):
            avg_score = np.mean([float(batter_info['rg_pred']), ss_score])
        elif is_number(ss_score):
            avg_score = ss_score
        else:
            continue
    else:
        if is_number(ss_score) and is_number(batter_info['nf_pred']):
            avg_score = np.mean([float(ss_score), float(batter_info['nf_pred'])])
        elif is_number(ss_score):
            avg_score = ss_score
        elif is_number(batter_info['nf_pred']):
            avg_score = float(batter_info['nf_pred']
        else:
            continue
    player_cost = float(batter_info['rg_cost'].replace('$', ''))
    if player_cost == 0.0:
        print batter_name
        continue
    if batter_info['rg_pos'] in position_results:
        position_results[batter_info['rg_pos']].append(
            [batter_name.decode('utf-8'), batter_info['rg_team'].decode('utf-8'), player_cost, ss_score,
             batter_info['rg_pred'], batter_info['nf_pred'], avg_score])
        players.append({
            "value": avg_score,
            "cost": player_cost,
            "pos": batter_info['rg_pos'],
            "name": batter_name,
            "team": batter_info['rg_team'],
            "opp": batter_info['rg_opp_team'].replace('@', '')
        })
        if is_number(ss_score):
            players_ss.append({
                "value": ss_score,
                "cost": player_cost,
                "pos": batter_info['rg_pos'],
                "name": batter_name,
                "team": batter_info['rg_team'],
                "opp": batter_info['rg_opp_team'].replace('@', '')
            })
        if is_number(batter_info['rg_pred']):
            players_rg.append({
                "value": float(batter_info['rg_pred']),
                "cost": player_cost,
                "pos": batter_info['rg_pos'],
                "name": batter_name,
                "team": batter_info['rg_team'],
                "opp": batter_info['rg_opp_team'].replace('@', '')
            })
        if is_number(batter_info['nf_pred']):
            players_nf.append({
                "value": float(batter_info['nf_pred']),
                "cost": player_cost,
                "pos": batter_info['nf_pos'],
                "name": batter_name,
                "team": batter_info['nf_team'],
                "opp": batter_info['rg_opp_team'].replace('@', '')
            })

"""PITCHER CALCULATIONS"""
pitchers_overall = []
for pitcher in merged_pitcher_df.iterrows():
    pitcher_info = pitcher[1]
    pitcher_name = pitcher[0]
    pitcher_cost = float(pitcher_info['rg_cost'])
    if pitcher_name in conf.excluded_pitchers or\
            pitcher_info['rg_team'] in conf.excluded_teams:
        continue
    avg_score = None
    if conf.use_rotogrinder_scores:
        if conf.site == 'draftkings':
            avg_score = float(pitcher_info['rg_pred'])
        elif is_number(pitcher_info['nf_pred']) and is_number(pitcher_info['rg_pred']):
            avg_score = np.mean([float(pitcher_info['nf_pred']), float(pitcher_info['rg_pred'])])
        elif is_number(pitcher_info['rg_pred']):
            avg_score = float(pitcher_info['rg_pred'])
        else:
            continue
    else:
        avg_score = float(pitcher_info['nf_pred'])
    players.append({
        "value": avg_score,
        "cost": pitcher_cost,
        "pos": 'P',
        "name": pitcher_name,
        "team": pitcher_info['rg_team'],
        "opp": pitcher_info['rg_opp_team']
    })
    players_ss.append({
        "value": avg_score,
        "cost": pitcher_cost,
        "pos": 'P',
        "name": pitcher_name,
        "team": pitcher_info['rg_team'],
        "opp": pitcher_info['rg_opp_team']
    })
    players_rg.append({
        "value": float(pitcher_info['rg_pred']),
        "cost": pitcher_cost,
        "pos": 'P',
        "name": pitcher_name,
        "team": pitcher_info['rg_team'],
        "opp": pitcher_info['rg_opp_team']
    })
    players_nf.append({
        "value": float(pitcher_info['nf_pred']),
        "cost": pitcher_cost,
        "pos": 'P',
        "name": pitcher_name,
        "team": pitcher_info['rg_team'],
        "opp": pitcher_info['rg_opp_team']
    })
    if conf.site == 'fanduel':
        pitchers_overall.append(
            [pitcher_name, pitcher_info['rg_team'], pitcher_cost,
             float(pitcher_info['nf_pred']), float(pitcher_info['rg_pred']),
             avg_score])
    elif conf.site == 'draftkings':
        pitchers_overall.append(
            [pitcher_name, pitcher_info['rg_team'], pitcher_cost,
             float(pitcher_info['rg_pred'])])

"""OUTPUT PROJECTIONS"""
print "Pitcher Projections"
if conf.site == 'fanduel':
    print tabulate(sorted(pitchers_overall, key=lambda player: player[4],
                   reverse=True), headers=[
                   "Name", "Team", "Cost", "Numberfire Pred",
                   "Rotogrinders Pred", "Average Pred"], tablefmt="plain")
elif conf.site == 'draftkings':
    print tabulate(sorted(pitchers_overall, key=lambda player: player[3],
                   reverse=True), headers=["Name", "Team", "Cost",
                   "Rotogrinders Pred"], tablefmt="plain")

print'\n'

print "Short Stop Projections"
print tabulate(sorted(position_results['SS'], key=lambda player: player[6],
    reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Numberfire Pred", "Avg Proj"], tablefmt="plain")

print '\n'

print "First Base Projections"
print tabulate(sorted(position_results['1B'], key=lambda player: player[6],
    reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Numberfire Pred", "Avg Proj"], tablefmt="plain")

print '\n'

print "Second Base Projections"
print tabulate(sorted(position_results['2B'], key=lambda player: player[6],
    reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Numberfire Pred", "Avg Proj"], tablefmt="plain")

print '\n'

print "Third Base Projections"
print tabulate(sorted(position_results['3B'], key=lambda player: player[6],
    reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Numberfire Pred", "Avg Proj"], tablefmt="plain")

print '\n'

print "Catcher Projections"
print tabulate(sorted(position_results['C'], key=lambda player: player[6],
    reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Numberfire Pred", "Avg Proj"], tablefmt="plain")

print '\n'

print "OF Projections"
print tabulate(sorted(position_results['OF'], key=lambda player: player[6],
    reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Numberfire Pred", "Avg Proj"], tablefmt="plain")

"""GENERATE LINEUPS"""
print "\nTOP GENETIC AVERAGED LINEUPS"
gen = GeneticMLB(conf.mlb_max_salary)
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

print "TOP GENETIC SABERSIM LINEUPS WITH CURRENT SETTINGS"
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

if conf.use_rotogrinder_scores:
    print "TOP GENETIC ROTOGRINDERS LINEUPS WITH CURRENT SETTINGS"
    lineups = gen.calculate(players_rg)
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

print "TOP GENETIC NUMBERFIRE LINEUPS WITH CURRENT SETTINGS"
lineups = gen.calculate(players_rg)
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
