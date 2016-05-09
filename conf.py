"""Configuration file."""

"""Account Credentials"""
sabersim_creds = {
    "username": "kevin.a.meurer@gmail.com",
    "password": "cowbell1"
}

google_creds = {
    "email": "kevin.a.meurer",
    "password": "cowbell453"
}

"""Local Paths"""
chromedriver_path = './chromedriver'

"""General Info"""
nba_max_salary = 60000
mlb_max_salary = 35000

# determines how much negative weight to assign to
# teams that play themselves
"""General Genetic Settings"""
genetic_generations = 1000# 75
retain = .6 # 0.35
random_select = .07 # 0.05
mutate_chance = 0.015
population_size = 150
# sort by "cost," "points," or both
sort_by = "both"

"""MLB-specific Genetic Settings"""
limit_conflicting_teams = True
self_defeating_weight = 5.0
same_team_bonus = True
same_team_weight = 5.0
stack_bonus = 25.0
min_different_teams = 3
excluded_pitchers = []
excluded_batters = ['Welington Castillo', 'Jacoby Ellsbury']
excluded_teams = ['OAK', 'NYY']

"""NBA-specific Genetic Settings"""
excluded_nba_players = []
excluded_nba_teams = []
