"""Contains runner functions for basic baseball simulation."""
from team import Team
from game_state import GameState
from numpy import random as r

def run_simulation(away_team_name, home_team_name, starting_inn=1):
    """Runs a simulation between two teams."""
    away_team = Team(away_team_name)
    home_team = Team(home_team_name)
    gs = GameState(starting_inn)
    # play the game
    while gs.game_on():
        # play inning
        if gs.get_stage() == 'top':
            batter = away_team.get_player(gs.batting_pos[0])
            pitcher = home_team.get_pitcher()
            outcome = play_batter(gs, batter, pitcher)
        else:
            batter = home_team.get_player(gs.batting_pos[1])
            pitcher = away_team.get_pitcher()
            outcome = play_batter(gs, batter, pitcher)
        gs.update_game(outcome)
    return gs.get_game_stats()

# given a state and player objects, calculate the outcome.
def play_batter(state, batter, pitcher):
    state.update_batters()
    calculate_hitting_outcome(state, batter, pitcher)

def calculate_hitting_outcome(batter, pitcher):
    # possibilities: 1b, 2b, 3b, hr, bb, hbp, so, ground out
    pitcher.get_probs(batter.get_handedness())
    ran = r.rand()
    return 'BB'

