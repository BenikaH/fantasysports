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
    pit_probs = pitcher.get_probs(batter.get_handedness())
    bat_probs = batter.get_probs(pitcher.get_handedness())
    outcome_den = (
        ((bat_probs['1B'] * pit_probs['1B']) / conf.league_totals['PROBS']['1B']) +\
        ((bat_probs['2B'] * pit_probs['2B']) / conf.league_totals['PROBS']['2B']) +\
        ((bat_probs['3B'] * pit_probs['3B']) / conf.league_totals['PROBS']['3B']) +\
        ((bat_probs['HR'] * pit_probs['HR']) / conf.league_totals['PROBS']['HR']) +\
        ((bat_probs['BB'] * pit_probs['BB']) / conf.league_totals['PROBS']['BB']) +\
        ((bat_probs['HBP'] * pit_probs['HBP']) / conf.league_totals['PROBS']['HBP']) +\
        ((bat_probs['SO'] * pit_probs['SO']) / conf.league_totals['PROBS']['SO']) +\
        ((bat_probs['OUT'] * pit_probs['OUT']) / conf.league_totals['PROBS']['OUT'])
    )
    ran = r.rand()
    out_prob = ((bat_probs['OUT'] * pit_probs['OUT']) / conf.league_totals['PROBS']['OUT']) / outcome_den
    if ran < single_prob:
        return 'OUT'
    so_prob = ((bat_probs['SO'] * pit_probs['SO']) / conf.league_totals['PROBS']['SO']) / outcome_den
    if ran >= out_prob and ran < out_prob + so_prob:
        return 'SO'
    cumul = out_prob + so_prob
    single_prob = ((bat_probs['1B'] * pit_probs['1B']) / conf.league_totals['PROBS']['1B']) / outcome_den
    if ran >= cumul and ran < cumul + single_prob:
        return '1B'
    double_prob = ((bat_probs['2B'] * pit_probs['2B']) / conf.league_totals['PROBS']['2B']) / outcome_den
    cumul += single_prob
    if ran >= cumul and ran < cumul + double_prob:
        return '2B'
    triple_prob = ((bat_probs['3B'] * pit_probs['3B']) / conf.league_totals['PROBS']['3B']) / outcome_den
    cumul += double_prob
    if ran >= cumul and ran < cumul + triple_prob:
        return '3B'
    hr_prob = ((bat_probs['HR'] * pit_probs['HR']) / conf.league_totals['PROBS']['HR']) / outcome_den
    cumul += triple_prob
    if ran >= cumul and ran < cumul + hr_prob:
        return 'HR'
    bb_prob = ((bat_probs['BB'] * pit_probs['BB']) / conf.league_totals['PROBS']['BB']) / outcome_den
    cumul += hr_prob
    if ran >= cumul and ran < cumul + bb_prob:
        return 'BB'
    # hbp_prob = ((bat_probs['HBP'] * pit_probs['HBP']) / conf.league_totals['PROBS']['HBP']) / outcome_den
    cumul += bb_prob
    if ran >= cumul and ran < 1:
        return 'HBP'
    print 'At the end.'
    return 'OUT'
}
