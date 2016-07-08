"""Configuration file."""
import os



"""
Original genetic settings:
"""
genetic_generations = 60
retain = 0.35
random_select = 0.05
mutate_chance = 0.015
population_size = 1000

# how to sort the results: can be 'cost', 'points', 'cost-points',
# 'cost-fitness', 'fitness'
sort_by = 'cost-fitness'


"""MLB-specific Genetic Settings"""
self_defeating_weight = 1.0
same_team_bonus_weight = 2.0
excluded_pitchers = []
excluded_batters = []
use_inclusion = False
included_teams = [
    'DET', 'TOR', 'WAS', 'NYM', 'NYY', 'CLE', 'ATL', 'CHC', 'MIN', 'TEX',
    'OAK', 'HOU', 'SEA', 'KCR', 'PHI', 'COL', 'SDP', 'LAD']
excluded_teams = []
favored_teams = []
# genetic algorithm settings for simple gen
# approach: can be 'mean' or 'profitability'
genetic_approach = 'mean'
profitable_cutoff = 180
# DEPRECATED OPTIONS
favored_team_bonus = 2.0
use_stack_bonus = False
stack_bonus = 7.0
use_batting_orders = True
min_different_teams = 3

"""Projection Generation Settings"""
# 'fanduel' or 'draftkings'
site = 'fanduel'
projection_date = 'today'
# number of games to simulate.  For an 8 game list, 2000 -> 9 minutes
simulated_game_count = 3000
optimizer_game_count = 3000
# 1 -> 1000, 2 -> 3000
proj_iteration = 'main'
proj_use_inclusion = False
proj_included_teams = [
    'DET', 'TOR', 'WAS', 'NYM', 'NYY', 'CLE', 'ATL', 'CHC', 'MIN', 'TEX',
    'OAK', 'HOU', 'SEA', 'KCR', 'PHI', 'COL', 'SDP', 'LAD']
# source of handedness projections (steamers or bbref)
handedness_source = 'steamer'


"""Modeling Settings"""
model_iteration = 3
# 3 -> 1 - 1 model
used_pitcher_model_name = 'pitcher_sub_model_3.pkl'
pitcher_neg_samples = 1
pitcher_total_samples = 3000

"""Local Paths"""
chromedriver_path = './chromedriver'
root_path = os.path.dirname(os.path.abspath(__file__))
cache_path = os.path.join(root_path, 'cache')
schedule_path = './data/schedule2016.txt'
batter_handedness_path = './data/batter_handedness.csv'
pitcher_handedness_path = './data/pitcher_handedness.csv'
field_factors_path = './data/field_factors.csv'
projection_output_dir = './projections/'
models_path = './models/'
retrosheet_path = './data/retrosheet/'
# id_map_path = './data/player_id_map.csv'
id_map_path = 'http://crunchtimebaseball.com/master.csv'
# steamer pitcher approach -> preseason or rest of season
steamer_pitcher_approach = 'ros'
steamer_preseason_split_pit_path =\
    './data/steamer_projections_pitchers_preseason.csv'
steamer_ros_pit_path = './data/pitchers_ros.csv'

"""Web Paths"""
rotogrinder_hitter_path =\
    'http://rotogrinders.com/projected-stats/mlb-hitter.csv?site=%s' % site
rotogrinder_pitcher_path =\
    'http://rotogrinders.com/projected-stats/mlb-pitcher.csv?site=%s' % site
rotogrinder_nba_path =\
    'http://rotogrinders.com/projected-stats/nba-player.csv?site=%s' % site
steamer_ros_split_bat_path = 'http://steamerprojections.com/hitters_ros_split.php'


"""General Genetic Settings"""
"""
genetic_generations = 1000 # used to be 1000
retain = .6
random_select = .07
mutate_chance = 0.05
population_size = 200
"""


"""NBA-specific Genetic Settings"""
excluded_nba_players = []
excluded_nba_teams = []

##################################
# NECESSARY TO RUN: DO NOT ALTER #
##################################
batting_orders = None
pitchers = None

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

"""Simulator Configuration"""
pitcher_handedness = None
batter_handedness = None
field_factors = None
pitcher_sub_model = None
steamer_batter_data = None
steamer_pitcher_data = None
steamer_preseason_splits = None

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
    'SD': 'San Diego',
    'SDN': 'San Diego'
}

long_to_short_names = {
    'Baltimore': 'BAL',
    'Orioles': 'BAL',
    'Boston': 'BOS',
    'Red Sox': 'BOS',
    'Toronto': 'TOR',
    'Blue Jays': 'TOR',
    'NY Yankees': 'NYY',
    'Yankees': 'NYY',
    'Tampa Bay': 'TBR',
    'Rays': 'TBR',
    'Cleveland': 'CLE',
    'Indians': 'CLE',
    'Detroit': 'DET',
    'Tigers': 'DET',
    'Kansas City': 'KCR',
    'Royals': 'KCR',
    'Chicago White Sox': 'CWS',
    'Chi White Sox': 'CWS',
    'White Sox': 'CWS',
    'Minnesota': 'MIN',
    'Twins': 'MIN',
    'Texas': 'TEX',
    'Rangers': 'TEX',
    'Seattle': 'SEA',
    'Mariners': 'SEA',
    'Houston': 'HOU',
    'Astros': 'HOU',
    'LA Angels': 'LAA',
    'Angels': 'LAA',
    'Oakland': 'OAK',
    'Athletics': 'OAK',
    'Washington': 'WAS',
    'Nationals': 'WAS',
    'NY Mets': 'NYM',
    'Mets': 'NYM',
    'Miami': 'MIA',
    'Marlins': 'MIA',
    'Philadelphia': 'PHI',
    'Phillies': 'PHI',
    'Atlanta': 'ATL',
    'Braves': 'ATL',
    'Chi Cubs': 'CHC',
    'Cubs': 'CHC',
    'Pittsburgh': 'PIT',
    'Pirates': 'PIT',
    'St. Louis': 'STL',
    'Cardinals': 'STL',
    'Milwaukee': 'MIL',
    'Brewers': 'MIL',
    'Cincinnatti': 'CIN',
    'Reds': 'CIN',
    'San Francisco': 'SFG',
    'Giants': 'SFG',
    'LA Dodgers': 'LAD',
    'Dodgers': 'LAD',
    'Colorado': 'COL',
    'Rockies': 'COL',
    'Arizona': 'ARI',
    'Diamondbacks': 'ARI',
    'San Diego': 'SDP',
    'Padres': 'SDP'
}

bb_ref_teams = {
    'BAL': 'BAL',
    'BOS': 'BOS',
    'TOR': 'TOR',
    'NYY': 'NYY',
    'TBR': 'TBR',
    'CLE': 'CLE',
    'DET': 'DET',
    'KCR': 'KC',
    'CWS': 'CHW',
    'MIN': 'MIN',
    'TEX': 'TEX',
    'SEA': 'SEA',
    'HOU': 'HOU',
    'LAA': 'LAA',
    'OAK': 'OAK',
    'WAS': 'WSN',
    'NYM': 'NYM',
    'MIA': 'MIA',
    'PHI': 'PHI',
    'ATL': 'ATL',
    'CHC': 'CHC',
    'PIT': 'PIT',
    'STL': 'STL',
    'MIL': 'MIL',
    'CIN': 'CIN',
    'SFG': 'SFG',
    'LAD': 'LAD',
    'COL': 'COL',
    'ARI': 'ARI',
    'SDP': 'SDP'
}

rotochamp_teams = {
    'ARI': 'ARI',
    'ATL': 'ATL',
    'BAL': 'BAL',
    'BOS': 'BOS',
    'CHC': 'CHC',
    'CIN': 'CIN',
    'CLE': 'CLE',
    'COL': 'COL',
    'CWS': 'CWS',
    'DET': 'DET',
    'HOU': 'HOU',
    'KCR': 'KAN',
    'LAA': 'LAA',
    'LAD': 'LAD',
    'MIA': 'MIA',
    'MIL': 'MIL',
    'MIN': 'MIN',
    'NYM': 'NYM',
    'NYY': 'NYY',
    'OAK': 'OAK',
    'PHI': 'PHI',
    'PIT': 'PIT',
    'SDP': 'SD',
    'SEA': 'SEA',
    'SFG': 'SF',
    'STL': 'STL',
    'TBR': 'TB',
    'TEX': 'TEX',
    'TOR': 'TOR',
    'WAS': 'WAS'
}

team_list = [
    'BAL', 'BOS', 'TOR', 'NYY', 'TBR', 'CLE', 'DET', 'KCR', 'CWS', 'MIN',
    'TEX', 'SEA', 'HOU', 'LAA', 'OAK', 'WAS', 'NYM', 'MIA', 'PHI', 'ATL',
    'CHC', 'PIT', 'STL', 'MIL', 'CIN', 'SFG', 'LAD', 'COL', 'ARI', 'SDP'
]

# http://www.baseball-reference.com/leagues/MLB/2014.shtml
league_average = {
    # BATvPIT
    'RvR': {
        'SO': 0.1880,
        '1B': 0.1570,
        '2B': 0.0459,
        '3B': 0.0039,
        'HR': 0.0269,
        'BB': 0.0707,
        'HBP': 0.0119,
        'OUT': 0.4957
    },
    'RvL': {
        'SO': 0.1677,
        '1B': 0.1577,
        '2B': 0.0510,
        '3B': 0.0042,
        'HR': 0.0285,
        'BB': 0.0918,
        'HBP': 0.0068,
        'OUT': 0.4924
    },
    'LvL': {
        'SO': 0.2137,
        '1B': 0.1527,
        '2B': 0.0405,
        '3B': 0.0049,
        'HR': 0.0227,
        'BB': 0.0795,
        'HBP': 0.0130,
        'OUT': 0.4730
    },
    'LvR': {
        'SO': 0.1718,
        '1B': 0.1569,
        '2B': 0.0482,
        '3B': 0.0063,
        'HR': 0.0272,
        'BB': 0.0977,
        'HBP': 0.0066,
        'OUT': 0.4853
    }
}

# from http://www.baseball-reference.com/leagues/MLB/2015-baserunning-batting.shtml
baserunning_avg = {
    # starting base, hit type, ending base
    '1S3': .27649510,
    '2SH': .57425549,
    '1DH': .43340206
}

below_avg_batting_probs = {
    'vL': {
        'OUT': .50,
        '1B': .105,
        '2B': .03,
        '3B': .004,
        'HR': .01,
        'BB': .05,
        'SO': .25,
        'HBP': .001
    },
    'vR': {
        'OUT': .50,
        '1B': .105,
        '2B': .03,
        '3B': .004,
        'HR': .01,
        'BB': .05,
        'SO': .25,
        'HBP': .001
    }
}

known_player_conversions = {
    'Michael Bolsinger': 'Mike Bolsinger',
    'Hyun-Soo Kim': 'Hyun Soo Kim',
    'Robert Refsnyder': 'Rob Refsnyder',
    'Timothy Anderson': 'Tim Anderson',
    'Norichika Aoki': 'Nori Aoki',
    'Jung-Ho Kang': 'Jung Ho Kang',
    'Matt Joyce': 'Matthew Joyce',
    'Melvin Upton Jr.': 'Melvin Upton',
    'Matthew Reynolds': 'Matt Reynolds',
    'Dae-Ho Lee': 'Dae-ho Lee',
    'Thomas Pham': 'Tommy Pham',
    'Michael Fiers': 'Mike Fiers',
    'Matthew Szczur': 'Matt Szczur',
    'Seung Hwan Oh': 'Seung-hwan Oh'
}
