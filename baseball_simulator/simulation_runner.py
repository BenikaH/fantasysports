"""Contains runner functions for basic baseball simulation."""
from team import Team
from game_state import GameState
from numpy import random as r
import util.data_loader as dl
from sklearn.externals import joblib
import tabulate as t
import conf
import pdb


def run_simulated_games(away_team_name, home_team_name, game_count=10):
    """Run a number of simulated games between two teams."""
    print "Running simulations between %s and %s" %\
        (away_team_name, home_team_name)
    if conf.pitcher_sub_model is None:
        conf.pitcher_sub_model = joblib.load(
            './models/%s' % conf.used_pitcher_model_name)
    away_team = Team(away_team_name)
    home_team = Team(home_team_name)
    agg_batters = []
    agg_scores = []
    agg_pitchers = []
    game_no = 0
    while game_no < game_count:
        print "Running game %d of %d. (%s vs. %s)" %\
            (game_no + 1, game_count, away_team_name, home_team_name)
        away_team.start_new_game()
        home_team.start_new_game()
        game_log, score, pit_stats, bat_stats = play_game(away_team, home_team)
        agg_scores.append(score)
        agg_pitchers.append(pit_stats)
        agg_batters.append(bat_stats)
        game_no += 1

    """Convert data to final display format."""
    batters_fanduel = {}
    batters_draftkings = {}
    pitchers_fanduel = {}
    pitchers_draftkings = {}
    wins = {
        away_team_name: 0,
        home_team_name: 0
    }
    runs = {
        away_team_name: [],
        home_team_name: []
    }
    for idx, entry in enumerate(agg_scores):
        runs[away_team_name].append(entry[0])
        runs[home_team_name].append(entry[1])
        if entry[0] > entry[1]:
            wins[away_team_name] += 1
        else:
            wins[home_team_name] += 1
        for name in agg_batters[idx].index:
            if name in batters_draftkings:
                batters_draftkings[name].append(
                    agg_batters[idx].at[name, 'DKP'])
                batters_fanduel[name].append(agg_batters[idx].at[name, 'FDP'])
            else:
                batters_draftkings[name] = [agg_batters[idx].at[name, 'DKP']]
                batters_fanduel[name] = [agg_batters[idx].at[name, 'FDP']]
        for name in agg_pitchers[idx].index:
            if name in batters_draftkings:
                del batters_draftkings[name]
                del batters_fanduel[name]
            if name in pitchers_draftkings:
                pitchers_draftkings[name].append(
                    agg_pitchers[idx].at[name, 'DKP'])
                pitchers_fanduel[name].append(
                    agg_pitchers[idx].at[name, 'FDP'])
            else:
                pitchers_draftkings[name] = [agg_pitchers[idx].at[name, 'DKP']]
                pitchers_fanduel[name] = [agg_pitchers[idx].at[name, 'FDP']]
    return {
        'wins': wins,
        'runs': runs,
        'batters_fd': batters_fanduel,
        'batters_dk': batters_draftkings,
        'pitchers_fd': pitchers_fanduel,
        'pitchers_dk': pitchers_draftkings
    }


def play_game(away_team, home_team, starting_inn=1):
    """Run a single simulation between two teams."""
    gs = GameState(away_team, home_team, starting_inn)
    # play the game
    while gs.game_on():
        # play innings
        # test for stolen bases, pitcher replacement, etc
        stolen_base = steal_base(gs) # returns index of runner that's attempting
        if stolen_base >= 0:
            ran = r.rand()
            # if it's a success, give it to them.  If not, they're out.
            if ran < gs.bases[stolen_base].get_stolen_base_chance()['success']:
                gs.add_stolen_base(stolen_base)
            else:
                gs.remove_runner(stolen_base)
            continue
        # test if pitcher replaced
        if gs.get_stage() == 'top':
            if home_team.get_pitcher() == home_team.get_starting_pitcher():
                if replace_pitcher(gs, home_team.get_pitcher()):
                    home_team.replace_pitcher('Relief')
                    continue
        elif gs.get_stage() == 'bot':
            if away_team.get_pitcher() == away_team.get_starting_pitcher():
                if replace_pitcher(gs, away_team.get_pitcher()):
                    away_team.replace_pitcher('Relief')
        # compute batter outcomes
        if gs.get_stage() == 'top':
            batter = away_team.get_player(gs.batting_pos[0])
            pitcher = home_team.get_pitcher()
            outcome = play_batter(gs, batter, pitcher, home_team.get_name())
        else:
            batter = home_team.get_player(gs.batting_pos[1])
            pitcher = away_team.get_pitcher()
            outcome = play_batter(gs, batter, pitcher, home_team.get_name())
        gs.update_game(outcome, batter, pitcher)
    return gs.get_game_stats()


# TODO
def steal_base(gs):
    # if someone on first with second open
    if gs.bases[0] != 0 and gs.bases[1] == 0:
        ran = r.rand()
        sb_chance = gs.bases[0].get_stolen_base_chance()
        if ran < sb_chance['steal']:
            return 0
    # if someone on second with third open
    elif gs.bases[1] != 0 and gs.bases[2] == 0:
        ran = r.rand()
        sb_chance = gs.bases[1].get_stolen_base_chance()
        if ran < sb_chance['steal']:
            return 1
    return - 1


def replace_pitcher(gs, pitcher):
    if gs.get_stage() == 'top':
        score_diff = gs.score[1] - gs.score[0]
    else:
        score_diff = gs.score[0] - gs.score[1]
    feats = pitcher.get_pitcher_sub_feats(gs, score_diff)
    pred = conf.pitcher_sub_model.predict(feats)
    if pred[0] == 0:
        return False
    else:
        # print '%s subbed out with the following stats.' % pitcher.get_name()
        # print t.tabulate(
        #     feats,
        #     headers=['K', 'BB', 'HBP', 'PA', 'HA', 'IP', 'ER', 'RD'],
        #     tablefmt='plain'
        # )
        return True


def play_batter(gs, batter, pitcher, home_team_name=None):
    """Determine the outcome of a pitcher-batter matchup."""
    gs.update_batters()
    pitcher.add_batter_faced()
    outcome = calculate_hitting_outcome(gs, batter, pitcher, home_team_name)
    return outcome


def calculate_hitting_outcome(gs, batter, pitcher, home_team_name=None):
    """Calculate probabilities and choose outcome of interaction."""
    # possibilities: 1b, 2b, 3b, hr, bb, hbp, so, ground out
    bat_hand = batter.get_batting_handedness()
    pit_hand = pitcher.get_pitching_handedness()
    if bat_hand == 'S' and pit_hand == 'R':
        bat_hand = 'L'
    if bat_hand == 'S' and pit_hand == 'L':
        bat_hand = 'R'
    # determine relevant league average
    league_key = '%sv%s' % (bat_hand, pit_hand)

    pit_probs = dict(pitcher.get_handed_pitching_probs(bat_hand))
    bat_probs = dict(batter.get_handed_batting_probs(pit_hand))
    # probability adjustments for field, weather, etc
    bat_probs = adjust_probs_for_field_factors(bat_probs, bat_hand, home_team_name)

    # compute the denominator in advance
    outcome_den = (
        ((bat_probs['1B'] * pit_probs['1B']) /
            conf.league_average[league_key]['1B']) +
        ((bat_probs['2B'] * pit_probs['2B']) /
            conf.league_average[league_key]['2B']) +
        ((bat_probs['3B'] * pit_probs['3B']) /
            conf.league_average[league_key]['3B']) +
        ((bat_probs['HR'] * pit_probs['HR']) /
            conf.league_average[league_key]['HR']) +
        ((bat_probs['BB'] * pit_probs['BB']) /
            conf.league_average[league_key]['BB']) +
        ((bat_probs['HBP'] * pit_probs['HBP']) /
            conf.league_average[league_key]['HBP']) +
        ((bat_probs['SO'] * pit_probs['SO']) /
            conf.league_average[league_key]['SO']) +
        ((bat_probs['OUT'] * pit_probs['OUT']) /
            conf.league_average[league_key]['OUT'])
    )
    ran = r.rand()
    out_prob = ((bat_probs['OUT'] * pit_probs['OUT']) /
                conf.league_average[league_key]['OUT']) / outcome_den
    try:
        if ran < out_prob:
            return 'OUT'
    except:
        pdb.set_trace()
    so_prob = ((bat_probs['SO'] * pit_probs['SO']) /
               conf.league_average[league_key]['SO']) / outcome_den
    if ran >= out_prob and ran < out_prob + so_prob:
        return 'SO'
    cumul = out_prob + so_prob
    single_prob = ((bat_probs['1B'] * pit_probs['1B']) /
                   conf.league_average[league_key]['1B']) / outcome_den
    if ran >= cumul and ran < cumul + single_prob:
        return '1B'
    double_prob = ((bat_probs['2B'] * pit_probs['2B']) /
                   conf.league_average[league_key]['2B']) / outcome_den
    cumul += single_prob
    if ran >= cumul and ran < cumul + double_prob:
        return '2B'
    triple_prob = ((bat_probs['3B'] * pit_probs['3B']) /
                   conf.league_average[league_key]['3B']) / outcome_den
    cumul += double_prob
    if ran >= cumul and ran < cumul + triple_prob:
        return '3B'
    hr_prob = ((bat_probs['HR'] * pit_probs['HR']) /
               conf.league_average[league_key]['HR']) / outcome_den
    cumul += triple_prob
    if ran >= cumul and ran < cumul + hr_prob:
        return 'HR'
    bb_prob = ((bat_probs['BB'] * pit_probs['BB']) /
               conf.league_average[league_key]['BB']) / outcome_den
    cumul += hr_prob
    if ran >= cumul and ran < cumul + bb_prob:
        return 'BB'
    cumul += bb_prob
    if ran >= cumul and ran < 1:
        return 'HBP'
    return 'OUT'


def adjust_probs_for_field_factors(probs, batter_handedness, home_team_name):
    """Adjust hitting probabilities according to field factors."""
    if home_team_name is None:
        return probs
    if conf.field_factors is None:
        conf.field_factors = dl.load_field_factors()
    ff = conf.field_factors.loc[home_team_name]
    b_h = batter_handedness[0]
    """
    Adjustments work as follows:
    -increase/decrease prob by multiplying prop by ff
    -take increase and subtract from out probability
    or
    -take decrease and add to out probability
    this all ensures that total probs = 1
    """
    # adjust singles
    orig_single = probs['1B']
    new_single = ff['1B_%s' % b_h] * orig_single
    diff = new_single - orig_single
    probs['OUT'] -= diff
    probs['1B'] = new_single
    # adjust doubles
    orig_double = probs['2B']
    new_double = ff['2B_%s' % b_h] * orig_double
    diff = new_double - orig_double
    probs['OUT'] -= diff
    probs['2B'] = new_double
    # adjust triples
    orig_triple = probs['3B']
    new_triple = ff['3B_%s' % b_h] * orig_triple
    diff = new_triple - orig_triple
    probs['OUT'] -= diff
    probs['3B'] = new_triple
    # adjust home runs
    orig_hr = probs['HR']
    new_hr = ff['HR_%s' % b_h] * orig_hr
    diff = new_hr - orig_hr
    probs['OUT'] -= diff
    probs['HR'] = new_hr
    return probs
