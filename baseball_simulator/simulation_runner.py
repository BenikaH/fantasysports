"""Contains runner functions for basic baseball simulation."""
from team import Team
from game_state import GameState
from numpy import random as r
import conf
import pdb


def run_simulated_games(away_team_name, home_team_name, game_count=10):
    away_team = Team(away_team_name)
    home_team = Team(home_team_name)
    game_no = 0
    while game_no < game_count:
        away_team.start_new_game()
        home_team.start_new_game()
        game_log, score, pit_stats, bat_stats = play_game(away_team, home_team)
        print score
        print pit_stats
        print bat_stats
        game_no += 1


def play_game(away_team, home_team, starting_inn=1):
    """Run a simulation between two teams."""
    gs = GameState(away_team, home_team, starting_inn)
    # play the game
    while gs.game_on():
        # play innings

        if gs.get_stage() == 'top':
            batter = away_team.get_player(gs.batting_pos[0])
            pitcher = home_team.get_pitcher()
            outcome = play_batter(gs, batter, pitcher)
        else:
            batter = home_team.get_player(gs.batting_pos[1])
            pitcher = away_team.get_pitcher()
            outcome = play_batter(gs, batter, pitcher)
        gs.update_game(outcome, batter, pitcher)
    return gs.get_game_stats()


def play_batter(gs, batter, pitcher):
    """Determing the outcome of a pitcher-batter matchup."""
    gs.update_batters()
    outcome = calculate_hitting_outcome(gs, batter, pitcher)
    return outcome


def calculate_hitting_outcome(gs, batter, pitcher):
    """Calculate probabilities and choose outcome of interaction."""
    # possibilities: 1b, 2b, 3b, hr, bb, hbp, so, ground out
    bat_hand = batter.get_batting_handedness()
    pit_hand = pitcher.get_pitching_handedness()
    if bat_hand == 'SWITCH' and pit_hand == 'RIGHT':
        bat_hand == 'LEFT'
    if bat_hand == 'SWITCH' and pit_hand == 'LEFT':
        bat_hand == 'RIGHT'
    pit_probs = pitcher.get_handed_pitching_probs(bat_hand)
    bat_probs = batter.get_handed_batting_probs(pit_hand)
    try:
        outcome_den = (
            ((bat_probs['1B'] * pit_probs['1B']) /
                conf.league_totals['PROBS']['1B']) +
            ((bat_probs['2B'] * pit_probs['2B']) /
                conf.league_totals['PROBS']['2B']) +
            ((bat_probs['3B'] * pit_probs['3B']) /
                conf.league_totals['PROBS']['3B']) +
            ((bat_probs['HR'] * pit_probs['HR']) /
                conf.league_totals['PROBS']['HR']) +
            ((bat_probs['BB'] * pit_probs['BB']) /
                conf.league_totals['PROBS']['BB']) +
            ((bat_probs['HBP'] * pit_probs['HBP']) /
                conf.league_totals['PROBS']['HBP']) +
            ((bat_probs['SO'] * pit_probs['SO']) /
                conf.league_totals['PROBS']['SO']) +
            ((bat_probs['OUT'] * pit_probs['OUT']) /
                conf.league_totals['PROBS']['OUT'])
        )
    except:
        pdb.set_trace()
    ran = r.rand()
    out_prob = ((bat_probs['OUT'] * pit_probs['OUT']) /
                conf.league_totals['PROBS']['OUT']) / outcome_den
    if ran < out_prob:
        return 'OUT'
    so_prob = ((bat_probs['SO'] * pit_probs['SO']) /
               conf.league_totals['PROBS']['SO']) / outcome_den
    if ran >= out_prob and ran < out_prob + so_prob:
        return 'SO'
    cumul = out_prob + so_prob
    single_prob = ((bat_probs['1B'] * pit_probs['1B']) /
                   conf.league_totals['PROBS']['1B']) / outcome_den
    if ran >= cumul and ran < cumul + single_prob:
        return '1B'
    double_prob = ((bat_probs['2B'] * pit_probs['2B']) /
                   conf.league_totals['PROBS']['2B']) / outcome_den
    cumul += single_prob
    if ran >= cumul and ran < cumul + double_prob:
        return '2B'
    triple_prob = ((bat_probs['3B'] * pit_probs['3B']) /
                   conf.league_totals['PROBS']['3B']) / outcome_den
    cumul += double_prob
    if ran >= cumul and ran < cumul + triple_prob:
        return '3B'
    hr_prob = ((bat_probs['HR'] * pit_probs['HR']) /
               conf.league_totals['PROBS']['HR']) / outcome_den
    cumul += triple_prob
    if ran >= cumul and ran < cumul + hr_prob:
        return 'HR'
    bb_prob = ((bat_probs['BB'] * pit_probs['BB']) /
               conf.league_totals['PROBS']['BB']) / outcome_den
    cumul += hr_prob
    if ran >= cumul and ran < cumul + bb_prob:
        return 'BB'
    cumul += bb_prob
    if ran >= cumul and ran < 1:
        return 'HBP'
    return 'OUT'
