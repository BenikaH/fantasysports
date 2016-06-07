"""Configuration file."""
import os

"""Local Paths"""
chromedriver_path = './chromedriver'
root_path = os.path.dirname(os.path.abspath(__file__))
cache_path = os.path.join(root_path, 'cache')


# 'fanduel' or 'draftkings'
site = 'draftkings'
include_numberfire = False

"""Web Paths"""
rotogrinder_hitter_path =\
    'http://rotogrinders.com/projected-stats/mlb-hitter.csv?site=%s' % site
rotogrinder_pitcher_path =\
    'http://rotogrinders.com/projected-stats/mlb-pitcher.csv?site=%s' % site
rotogrinder_nba_path =\
    'http://rotogrinders.com/projected-stats/nba-player.csv?site=%s' % site

"""General Info"""
nba_max_salary = 60000
if site == 'fanduel':
    mlb_max_salary = 35000
    supp_proj_site = 'numberfire'
elif site == 'draftkings':
    mlb_max_salary = 50000
    supp_proj_site = 'N/A'
use_rotogrinder_scores = False

# determines how much negative weight to assign to
# teams that play themselves
"""General Genetic Settings"""
'''
genetic_generations = 1000
retain = .6
random_select = .07
mutate_chance = 0.06
population_size = 150
'''

# how to sort the results: can be 'cost', 'points', 'cost-points',
# 'cost-fitness', 'fitness'
sort_by = 'cost-points'

"""
Original settings:
"""
genetic_generations = 50
retain = 0.35
random_select = 0.05
mutate_chance = 0.015
population_size = 10000

"""MLB-specific Genetic Settings"""
self_defeating_weight = 3.0
same_team_bonus_weight = 3.0
favored_team_bonus = 3.0
use_stack_bonus = False
stack_bonus = 0.0
use_batting_orders = True
min_different_teams = 3
excluded_pitchers = []
excluded_batters = []
use_inclusion = False
included_teams = []
excluded_teams = []
favored_teams = []

"""NBA-specific Genetic Settings"""
excluded_nba_players = []
excluded_nba_teams = []

short_to_long_names = {
    'OAK': 'Athletics',
    'LAA': 'Angels',
    'NYM': 'Mets',
    'KCR': 'Royals',
    'KC': 'Royals',
    'TOR': 'Blue Jays',
    'CIN': 'Reds',
    'LAD': 'Dodgers',
    'SD': 'Padres',
    'SDP': 'Padres',
    'SF': 'Giants',
    'SFG': 'Giants',
    'NYY': 'Yankees',
    'CHC': 'Cubs',
    'CHW': 'White Sox',
    'BOS': 'Red Sox'
}

long_to_short_names = {
    'Athletics': 'OAK',
    'Angels': 'LAA',
    'Mets': 'NYM',
    'Royals': 'KCR',
    'Blue Jays': 'TOR',
    'Reds': 'CIN',
    'Dodgers': 'LAD',
    'Padres': 'SD',
    'Padres': 'SDP',
    'Giants': 'SF',
    'Giants': 'SFG',
    'Yankees': 'NYY',
    'Cubs': 'CHC',
    'White Sox': 'CHW',
    'Red Sox': 'BOS'
}
