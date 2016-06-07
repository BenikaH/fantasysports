"""Generates Lineups for MLB FanDuel Scoring."""
from scrapers.sabersim_scraper import\
    get_saber_sim_projections_from_fangraphs
from scrapers.numberfire_scraper import\
    retrieve_numberfire_mlb_predictions_and_salaries
from scrapers.rotogrinder_scraper import\
    retrieve_rotogrinder_mlb_projections, retrieve_mlb_batting_order
from util.score_calculators import calculate_fanduel_hitter_score,\
    calculate_draftkings_hitter_score
from tabulate import tabulate
import numpy as np
import conf
from util.util import is_number, lineup_dict_to_list, print_lineup
from lineup_optimizers.genetic_mlb import GeneticMLB
import pdb

###################
# DATA EXTRACTION #
###################

# Rotogrinders
batter_df_rotogrinders, pitcher_df_rotogrinders =\
    retrieve_rotogrinder_mlb_projections()

# Sabersim
batter_df_sabersim, pitcher_df_sabersim =\
    get_saber_sim_projections_from_fangraphs()

# Merged RG + SS
merged_batter_df =\
    batter_df_rotogrinders.join(batter_df_sabersim, on=None, how='left')
merged_pitcher_df = pitcher_df_rotogrinders.join(pitcher_df_sabersim)

# Load Batting Orders
if conf.use_batting_orders:
    conf.batting_orders = retrieve_mlb_batting_order()

if conf.site == 'fanduel':
    # Numberfire (only for fanduel)
    batter_df_numberfire, pitcher_df_numberfire =\
        retrieve_numberfire_mlb_predictions_and_salaries()
    # Remerged for numberfire
    merged_batter_df =\
        merged_batter_df.join(batter_df_numberfire, on=None, how='left')
    merged_pitcher_df = pitcher_df_numberfire.join(
        merged_pitcher_df, on=None, how='left', lsuffix='_nf',
        rsuffix='_rg')

position_results = {
    'SS': [],
    '1B': [],
    '2B': [],
    '3B': [],
    'C': [],
    'OF': []
}

# Different Arrays for Aggregated Data OP
players = []
players_ss = []
players_nf = []
if conf.use_rotogrinder_scores or conf.site == 'draftkings':
    players_rg = []

"""BATTER CONSOLIDATION"""
for batter in merged_batter_df.iterrows():
    batter_info = batter[1]
    batter_name = batter[0]
    # Skip specified batters
    if conf.use_inclusion:
        if batter_name in conf.excluded_batters or\
                batter_info['rg_team'] not in conf.included_teams:
            continue
        elif batter_name not in conf.batting_orders[batter_info['rg_team']]:
            continue
    else:
        if batter_name in conf.excluded_batters or\
                batter_info['rg_team'] in conf.excluded_teams:
            continue
        elif batter_name not in conf.batting_orders[batter_info['rg_team']]:
            continue
    # sing, doub, trip, walk, hbp, hr, runs, rbi, sb
    if conf.site == 'fanduel':
        ss_score = float(batter_info['ss_fd_pred'])
    elif conf.site == 'draftkings':
        ss_score = float(batter_info['ss_dk_pred'])
    else:
        raise ValueError('Please choose either "fanduel" or "draftkings" in conf.site.')
    avg_score = None
    if conf.site == 'draftkings' or conf.supp_proj_site == 'rotogrinder':
        if is_number(ss_score) and is_number(batter_info['rg_pred']):
            avg_score = np.mean([float(ss_score), float(batter_info['rg_pred'])])
        elif is_number(ss_score):
            avg_score = ss_score
        elif is_number(batter_info['rg_pred']):
            avg_score = float(batter_info['rg_pred'])
        else:
            continue
    elif conf.use_rotogrinder_scores:
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
            avg_score = float(batter_info['nf_pred'])
        else:
            continue
    player_cost = float(batter_info['rg_cost'])
    if player_cost == 0.0:
        continue
    if batter_info['rg_pos'] in position_results:
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
        if conf.site == 'fanduel':
            if is_number(batter_info['nf_pred']):
                players_nf.append({
                    "value": float(batter_info['nf_pred']),
                    "cost": player_cost,
                    "pos": batter_info['rg_pos'],
                    "name": batter_name,
                    "team": batter_info['rg_team'],
                    "opp": batter_info['rg_opp_team'].replace('@', '')
                })
            position_results[batter_info['rg_pos']].append(
                [batter_name,
                 batter_info['rg_team'],
                 player_cost,
                 ss_score,
                 batter_info['rg_pred'],
                 batter_info['nf_pred'],
                 avg_score]
            )
        elif conf.site == 'draftkings':
            if is_number(batter_info['rg_pred']):
                players_rg.append({
                    "value": float(batter_info['rg_pred']),
                    "cost": player_cost,
                    "pos": batter_info['rg_pos'],
                    "name": batter_name,
                    "team": batter_info['rg_team'],
                    "opp": batter_info['rg_opp_team'].replace('@', '')
                })
            position_results[batter_info['rg_pos']].append(
                [batter_name,
                 batter_info['rg_team'],
                 player_cost,
                 ss_score,
                 batter_info['rg_pred'],
                 avg_score]
            )

"""PITCHER CALCULATIONS"""
pitchers_overall = []
for pitcher in merged_pitcher_df.iterrows():
    pitcher_info = pitcher[1]
    pitcher_name = pitcher[0]
    pitcher_cost = float(pitcher_info['rg_cost'])
    if conf.use_inclusion:
        if pitcher_name in conf.excluded_pitchers or\
                pitcher_info['rg_team'] not in conf.included_teams:
            continue
    else:
        if pitcher_name in conf.excluded_pitchers or\
                pitcher_info['rg_team'] in conf.excluded_teams:
            continue
    if conf.site == 'fanduel':
        ss_score = float(pitcher_info['ss_fd_pred'])
    elif conf.site == 'draftkings':
        ss_score = float(pitcher_info['ss_dk_pred'])
    else:
        raise ValueError('Please choose either "fanduel" or "draftkings" in conf.site.')
    avg_score = None
    if conf.site == 'draftkings' or conf.supp_proj_site == 'rotogrinder':
        if is_number(ss_score) and is_number(pitcher_info['rg_pred']):
            avg_score = np.mean([float(ss_score), float(pitcher_info['rg_pred'])])
        elif is_number(ss_score):
            avg_score = float(ss_score)
        else:
            continue
    elif conf.use_rotogrinder_scores:
        if is_number(pitcher_info['nf_pred']) and is_number(pitcher_info['ss_fd_pred']) and is_number(pitcher_info['rg_pred']):
            avg_score = np.mean([float(pitcher_info['nf_pred']), float(pitcher_info['ss_fd_pred']), float(pitcher_info['rg_pred'])])
        elif is_number(pitcher_info['ss_fd_pred']):
            avg_score = float(pitcher_info['ss_fd_pred'])
        else:
            continue
    else:
        if is_number(pitcher_info['nf_pred']) and is_number(pitcher_info['ss_fd_pred']):
            avg_score = np.mean([float(pitcher_info['nf_pred']), float(pitcher_info['ss_fd_pred'])])
        elif is_number(pitcher_info['ss_fd_pred']):
            avg_score = float(pitcher_info['ss_fd_pred'])
        else:
            continue
    players.append({
        "value": avg_score,
        "cost": pitcher_cost,
        "pos": 'P',
        "name": pitcher_name,
        "team": pitcher_info['rg_team'],
        "opp": pitcher_info['rg_opp_team']
    })

    if is_number(pitcher_info['ss_fd_pred']) and conf.site == 'fanduel':
        players_ss.append({
            "value": float(pitcher_info['ss_fd_pred']),
            "cost": pitcher_cost,
            "pos": 'P',
            "name": pitcher_name,
            "team": pitcher_info['rg_team'],
            "opp": pitcher_info['rg_opp_team']
        })
    elif is_number(pitcher_info['ss_dk_pred']) and conf.site == 'draftkings':
        players_ss.append({
            "value": float(pitcher_info['ss_dk_pred']),
            "cost": pitcher_cost,
            "pos": 'P',
            "name": pitcher_name,
            "team": pitcher_info['rg_team'],
            "opp": pitcher_info['rg_opp_team']
        })
    if conf.use_rotogrinder_scores:
        players_rg.append({
            "value": float(pitcher_info['rg_pred']),
            "cost": pitcher_cost,
            "pos": 'P',
            "name": pitcher_name,
            "team": pitcher_info['rg_team'],
            "opp": pitcher_info['rg_opp_team']
        })
    if conf.site == 'fanduel':
        players_nf.append({
            "value": float(pitcher_info['nf_pred']),
            "cost": pitcher_cost,
            "pos": 'P',
            "name": pitcher_name,
            "team": pitcher_info['rg_team'],
            "opp": pitcher_info['rg_opp_team']
        })
        pitchers_overall.append(
            [pitcher_name, pitcher_info['rg_team'], pitcher_cost,
             float(pitcher_info['nf_pred']), float(pitcher_info['rg_pred']),
             float(pitcher_info['ss_fd_pred']), avg_score])
    elif conf.site == 'draftkings':
        players_rg.append({
            "value": float(pitcher_info['rg_pred']),
            "cost": pitcher_cost,
            "pos": 'P',
            "name": pitcher_name,
            "team": pitcher_info['rg_team'],
            "opp": pitcher_info['rg_opp_team']
        })
        pitchers_overall.append(
            [pitcher_name, pitcher_info['rg_team'], pitcher_cost,
             float(pitcher_info['rg_pred']), float(pitcher_info['ss_dk_pred']),
             avg_score])


"""OUTPUT PROJECTIONS"""
print'\n'
if conf.site == 'fanduel':
    print "Pitcher Projections"
    print tabulate(sorted(pitchers_overall, key=lambda player: player[4],
                   reverse=True), headers=[
                   "Name", "Team", "Cost", "Numberfire Pred",
                   "Rotogrinders Pred", "Sabersim Pred", "Average Pred"], tablefmt="plain")

    print "\nShort Stop Projections"
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
        reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Avg Proj"], tablefmt="plain")

elif conf.site == 'draftkings':
    print "Pitcher Projections"
    print tabulate(sorted(pitchers_overall, key=lambda player: player[5],
                   reverse=True), headers=["Name", "Team", "Cost",
                   "Rotogrinders Pred", "Sabersim Pred", 'Average Pred'], tablefmt="plain")

    print "Short Stop Projections"
    print tabulate(sorted(position_results['SS'], key=lambda player: player[5],
        reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Avg Proj"], tablefmt="plain")

    print '\n'

    print "First Base Projections"
    print tabulate(sorted(position_results['1B'], key=lambda player: player[5],
        reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Avg Proj"], tablefmt="plain")

    print '\n'

    print "Second Base Projections"
    print tabulate(sorted(position_results['2B'], key=lambda player: player[5],
        reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Avg Proj"], tablefmt="plain")

    print '\n'

    print "Third Base Projections"
    print tabulate(sorted(position_results['3B'], key=lambda player: player[5],
        reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Avg Proj"], tablefmt="plain")

    print '\n'

    print "Catcher Projections"
    print tabulate(sorted(position_results['C'], key=lambda player: player[5],
        reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Avg Proj"], tablefmt="plain")

    print '\n'

    print "OF Projections"
    print tabulate(sorted(position_results['OF'], key=lambda player: player[5],
        reverse=True), headers=["Name", "Team", "Cost", "Sabersim Pred", "Rotogrinder Pred", "Avg Proj"], tablefmt="plain")

"""GENERATE LINEUPS"""
print "\nTOP GENETIC AVERAGED LINEUPS"
gen = GeneticMLB(conf.mlb_max_salary)
lineups = gen.calculate(players)
print "Average Fitness: %d\n" % gen.grade(lineups)
try:
    print "Number 1"
    print_lineup(lineups[0], gen)
    print "Number 2"
    print_lineup(lineups[1], gen)
    print "Number 3"
    print_lineup(lineups[2], gen)
    print "Number 4"
    print_lineup(lineups[3], gen)
    print 'Number 5'
    print_lineup(lineups[4], gen)
    print '\n'
except:
    pdb.set_trace()

print "TOP GENETIC SABERSIM LINEUPS WITH CURRENT SETTINGS"
lineups = gen.calculate(players_ss)
print "Average Fitness: %d\n" % gen.grade(lineups)
print "Number 1"
print_lineup(lineups[0], gen)
print "Number 2"
print_lineup(lineups[1], gen)
print "Number 3"
print_lineup(lineups[2], gen)
print "Number 4"
print_lineup(lineups[3], gen)
print 'Number 5'
print_lineup(lineups[4], gen)
print '\n'

if conf.use_rotogrinder_scores or conf.site == 'draftkings':
    print "TOP GENETIC ROTOGRINDERS LINEUPS WITH CURRENT SETTINGS"
    lineups = gen.calculate(players_rg)
    print "Average Fitness: %d\n" % gen.grade(lineups)
    print "Number 1"
    print_lineup(lineups[0], gen)
    print "Number 2"
    print_lineup(lineups[1], gen)
    print "Number 3"
    print_lineup(lineups[2], gen)
    print "Number 4"
    print_lineup(lineups[3], gen)
    print 'Number 5'
    print_lineup(lineups[4], gen)
    print '\n'

if conf.site == 'fanduel':
    print "TOP GENETIC NUMBERFIRE LINEUPS WITH CURRENT SETTINGS"
    lineups = gen.calculate(players_nf)
    print "Average Fitness: %d\n" % gen.grade(lineups)
    print "Number 1"
    print_lineup(lineups[0], gen)
    print "Number 2"
    print_lineup(lineups[1], gen)
    print "Number 3"
    print_lineup(lineups[2], gen)
    print "Number 4"
    print_lineup(lineups[3], gen)
    print 'Number 5'
    print_lineup(lineups[4], gen)
    print '\n'
