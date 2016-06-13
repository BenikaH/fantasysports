"""Configuration file."""
import os

"""Local Paths"""
chromedriver_path = './chromedriver'
root_path = os.path.dirname(os.path.abspath(__file__))
cache_path = os.path.join(root_path, 'cache')
schedule_path = './data/schedule.txt'


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
    max_team_repetition = 4
elif site == 'draftkings':
    mlb_max_salary = 50000
    supp_proj_site = 'N/A'
    max_team_repetition = 4
use_rotogrinder_scores = False
player_id_map = None

# determines how much negative weight to assign to
# teams that play themselves
"""General Genetic Settings"""
genetic_generations = 1000
retain = .6
random_select = .07
mutate_chance = 0.06
population_size = 150

# how to sort the results: can be 'cost', 'points', 'cost-points',
# 'cost-fitness', 'fitness'
sort_by = 'cost-fitness'

"""
Original settings:
"""
'''
genetic_generations = 50
retain = 0.35
random_select = 0.05
mutate_chance = 0.015
population_size = 10000
'''

"""MLB-specific Genetic Settings"""
self_defeating_weight = 3.0
same_team_bonus_weight = 3.0
favored_team_bonus = 2.0
use_stack_bonus = False
stack_bonus = 7.0
use_batting_orders = True
min_different_teams = 3
excluded_pitchers = []
excluded_batters = []
use_inclusion = True
included_teams = ['DET', 'NYY', 'KCR', 'CWS', 'NYM', 'MIL', 'BOS', 'MIN']
excluded_teams = []
favored_teams = []

"""NBA-specific Genetic Settings"""
excluded_nba_players = []
excluded_nba_teams = []

'USED TO ENFORCE CONTINUITY'
short_to_long_names = {
    'BAL': 'Baltimore',
    'BOS': 'Boston',
    'TOR': 'Toronto',
    'NYY': 'NY Yankees',
    'NY': 'NY Yankees',
    'NYA': 'NY Yankees',
    'TB': 'Tampa Bay',
    'TBR': 'Tampa Bay',
    'TBA': 'Tampa Bay',
    'CLE': 'Cleveland',
    'DET': 'Detroit',
    'KCR': 'Kansas City',
    'KCA': 'Kansas City',
    'KC': 'Kansas City',
    'CHW': 'Chi White Sox',
    'CWS': 'Chi White Sox',
    'CHA': 'Chi White Sox',
    'MIN': 'Minnesota',
    'TEX': 'Texas',
    'SEA': 'Seattle',
    'HOU': 'Houston',
    'LAA': 'LA Angels',
    'ANA': 'LA Angels',
    'OAK': 'Oakland',
    'WAS': 'Washington',
    'WSH': 'Washington',
    'NYM': 'NY Mets',
    'NYN': 'NY Mets',
    'MIA': 'Miami',
    'PHI': 'Philadelphia',
    'ATL': 'Atlanta',
    'CHC': 'Chi Cubs',
    'CHN': 'Chi Cubs',
    'PIT': 'Pittsburgh',
    'STL': 'St. Louis',
    'SLN': 'St. Louis',
    'MIL': 'Milwaukee',
    'CIN': 'Cincinnatti',
    'SF': 'San Francisco',
    'SFG': 'San Francisco',
    'SFN': 'San Francisco',
    'LAD': 'LA Dodgers',
    'LAN': 'LA Dodgers',
    'LOS': 'LA Dodgers',
    'LA': 'LA Dodgers',
    'COL': 'Colorado',
    'ARI': 'Arizona',
    'SDP': 'San Diego',
    'SD': 'San Diego'
}

long_to_short_names = {
    'Baltimore': 'BAL',
    'Boston': 'BOS',
    'Toronto': 'TOR',
    'NY Yankees': 'NYY',
    'Tampa Bay': 'TBR',
    'Cleveland': 'CLE',
    'Detroit': 'DET',
    'Kansas City': 'KCR',
    'Chi White Sox': 'CWS',
    'Minnesota': 'MIN',
    'Texas': 'TEX',
    'Seattle': 'SEA',
    'Houston': 'HOU',
    'LA Angels': 'LAA',
    'Oakland': 'OAK',
    'Washington': 'WAS',
    'NY Mets': 'NYM',
    'Miami': 'MIA',
    'Philadelphia': 'PHI',
    'Atlanta': 'ATL',
    'Chi Cubs': 'CHC',
    'Pittsburgh': 'PIT',
    'St. Louis': 'STL',
    'Milwaukee': 'MIL',
    'Cincinnatti': 'CIN',
    'San Francisco': 'SFG',
    'LA Dodgers': 'LAD',
    'Colorado': 'COL',
    'Arizona': 'ARI',
    'San Diego': 'SDP'
}

# http://www.baseball-reference.com/leagues/MLB/2014.shtml
league_totals = {
    '2013': {
        '1B': 28438.0,
        '2B': 8222.0,
        '3B': 772.0,
        'HR': 4661.0,
        'BB': 14640.0,
        'SO': 36710.0,
        'HBP': 1536.0,
        'OUT': 89894.0,
        'PA': 184873.0
    },
    '2014': {
        '1B': 28423.0,
        '2B': 8137.0,
        '3B': 849.0,
        'HR': 4186.0,
        'BB': 14020.0,
        'SO': 37441.0,
        'HBP': 1652.0,
        'OUT': 89221.0,
        'PA': 183929.0
    },
    '2015': {
        '1B': 28016.0,
        '2B': 8242.0,
        '3B': 939.0,
        'HR': 4909.0,
        'BB': 14073.0,
        'SO': 37446.0,
        'HBP': 1602.0,
        'OUT': 88401.0,
        'PA': 183628.0
    }
}
