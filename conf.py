"""Configuration file."""
sabersim_creds = {
    "username": "kevin.a.meurer@gmail.com",
    "password": "cowbell1"
}

google_creds = {
    "email": "kevin.a.meurer",
    "password": "cowbell453"
}

chromedriver_path = './chromedriver'

# 'nfl', 'nba', or 'mlb'
sport_type = 'mlb'
max_salary = 35000

# determines how much negative weight to assign to
# teams that play themselves
genetic_generations = 75

limit_conflicting_teams = True
self_defeating_weight = 5.0

same_team_bonus = True
same_team_weight = 5.0
stack_bonus = 25.0
min_different_teams = 3

excluded_pitchers = []
excluded_batters = ['Welington Castillo', 'Jacoby Ellsbury']
excluded_teams = ['OAK', 'NYY']

excluded_nba_players = []
excluded_nba_teams = []