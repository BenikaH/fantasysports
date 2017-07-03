"""Contains methods for loading Local Data"""
from __future__ import division
import csv
from cache import cache_disk
import util
import scrapers.baseball_ref_scraper as brs
import pandas as pd
import numpy as np
import conf
import pdb

def load_mlb_schedule():
    sch = open(conf.schedule_path)
    data = csv.reader(sch)
    data_entries = [entry for entry in data]
    for ent in data_entries:
        ent[2] = util.standardize_team_name(ent[2])
        ent[5] = util.standardize_team_name(ent[5])
    df = pd.DataFrame([ent[1:] for ent in data_entries],
                      columns=['day', 'away_team', 'away_lg',
                               'away_count', 'home_team', 'home_lg',
                               'home_count', 'null'],
                      index=[ent[0] for ent in data_entries]
                      )
    return df


def load_field_factors():
    sch = open(conf.field_factors_path, 'rU')
    data = csv.reader(sch)
    data_entries = [entry for entry in data]
    cols = data_entries[0][1:]
    data_entries = data_entries[1:]
    df = pd.DataFrame([[float(en) / 100.0 for en in ent[1:]] for ent in data_entries],
                      columns=cols,
                      index=[util.standardize_team_name(ent[0]) for ent in data_entries]
                      )
    return df


def load_player_id_map():
    """Load the list of ids and handedness feats into memory."""
    return pd.read_csv(conf.id_map_path, index_col=1)


def get_player_name_from_id(mlb_id):
    """Get the mlb player id of a given player."""
    util.check_load_player_id_map()
    name = conf.player_id_map.iloc[
        np.where(
            conf.player_id_map['mlb_id'].values == mlb_id)[0][0]].name
    return name


def get_player_mlb_id(name):
    """Get the mlb player id of a given player."""
    util.check_load_player_id_map()
    mlb_id = conf.player_id_map.at[name, 'mlb_id']
    if type(mlb_id) == np.ndarray:
        birth_years = conf.player_id_map.at[name, 'birth_year']
        idx = np.argmax(birth_years)
        mlb_id[idx]
        return int(mlb_id[idx])
    else:
        return int(mlb_id)


def get_player_bb_ref_id(name):
    util.check_load_player_id_map()
    try:
        bref_id = conf.player_id_map.at[name, 'bref_id']
        return bref_id
    except:
        id_map = brs.retrieve_player_id_map()
        if name in id_map:
            bref_id = id_map[name]
            return bref_id
        else:
            return None


def load_steamer_handed_probabilities(play_id, pit_or_bat='b'):
    if pit_or_bat == 'b' and conf.steamer_batter_data is None:
        conf.steamer_batter_data = load_steamer_batter_projections()
    elif pit_or_bat == 'p' and conf.steamer_pitcher_data is None:
        if conf.steamer_pitcher_approach == 'ros':
            conf.steamer_pitcher_data, conf.steamer_preseason_splits = load_steamer_pitcher_projections()
        elif conf.steamer_pitcher_approach == 'preseason':
            conf.steamer_pitcher_data = load_steamer_pitcher_projections()
    probs = {'overall': {}, 'vL': {}, 'vR': {}}
    if pit_or_bat == 'b':
        counts = {'overall': {}, 'vL': {}, 'vR': {}}
        split = conf.steamer_batter_data.at[play_id, 'split']
        sing = conf.steamer_batter_data.at[play_id, '1B']
        doub = conf.steamer_batter_data.at[play_id, '2B']
        trip = conf.steamer_batter_data.at[play_id, '3B']
        hr = conf.steamer_batter_data.at[play_id, 'HR']
        bb = conf.steamer_batter_data.at[play_id, 'BB']
        so = conf.steamer_batter_data.at[play_id, 'K']
        hbp = conf.steamer_batter_data.at[play_id, 'HBP']
        pa = conf.steamer_batter_data.at[play_id, 'PA']
        for idx, val in enumerate(split):
            if '1B' in counts[val]:
                counts[val]['1B'] = np.mean([counts[val]['1B'], sing[idx]])
                counts[val]['2B'] = np.mean([counts[val]['2B'], doub[idx]])
                counts[val]['3B'] = np.mean([counts[val]['3B'], trip[idx]])
                counts[val]['HR'] = np.mean([counts[val]['HR'], hr[idx]])
                counts[val]['BB'] = np.mean([counts[val]['BB'], bb[idx]])
                counts[val]['SO'] = np.mean([counts[val]['SO'], so[idx]])
                counts[val]['HBP'] = np.mean([counts[val]['HBP'], hbp[idx]])
                counts[val]['PA'] = np.mean([counts[val]['PA'], pa[idx]])
            else:
                counts[val]['1B'] = sing[idx]
                counts[val]['2B'] = doub[idx]
                counts[val]['3B'] = trip[idx]
                counts[val]['HR'] = hr[idx]
                counts[val]['BB'] = bb[idx]
                counts[val]['SO'] = so[idx]
                counts[val]['HBP'] = hbp[idx]
                counts[val]['PA'] = pa[idx]
        for key in counts:
            probs[key]['1B'] = counts[key]['1B'] / counts[key]['PA']
            probs[key]['2B'] = counts[key]['2B'] / counts[key]['PA']
            probs[key]['3B'] = counts[key]['3B'] / counts[key]['PA']
            probs[key]['HR'] = counts[key]['HR'] / counts[key]['PA']
            probs[key]['BB'] = counts[key]['BB'] / counts[key]['PA']
            probs[key]['SO'] = counts[key]['SO'] / counts[key]['PA']
            probs[key]['HBP'] = counts[key]['HBP'] / counts[key]['PA']
            probs[key]['OUT'] =\
                (counts[key]['PA'] - (counts[key]['1B'] + counts[key]['2B'] +
                 counts[key]['3B'] + counts[key]['HR'] + counts[key]['BB'] +
                 counts[key]['SO'] + counts[key]['HBP'])) / counts[key]['PA']
    elif pit_or_bat == 'p':
        if conf.steamer_pitcher_approach == 'ros':
            player_name = get_player_name_from_id(play_id)
            if type(conf.steamer_pitcher_data.at[player_name, 'IP']) == np.ndarray:
                total_outs = (conf.steamer_pitcher_data.at[player_name, 'IP'][0] * 3.0)
                hits = (conf.steamer_pitcher_data.at[player_name, 'H'][0] -
                        conf.steamer_pitcher_data.at[player_name, 'HR'][0])
                so = conf.steamer_pitcher_data.at[player_name, 'SO'][0]
                bb = conf.steamer_pitcher_data.at[player_name, 'BB'][0]
                hr = conf.steamer_pitcher_data.at[player_name, 'HR'][0]
            else:
                total_outs = (conf.steamer_pitcher_data.at[player_name, 'IP'] * 3.0)
                hits = (conf.steamer_pitcher_data.at[player_name, 'H'] -
                        conf.steamer_pitcher_data.at[player_name, 'HR'])
                so = conf.steamer_pitcher_data.at[player_name, 'SO']
                bb = conf.steamer_pitcher_data.at[player_name, 'BB']
                hr = conf.steamer_pitcher_data.at[player_name, 'HR']
            pa = total_outs + hits + bb + hr
            # calculate general probs
            so_prob = so / pa
            out_prob = (total_outs - so) / pa
            hit_prob = hits / pa
            hr_prob = hr / pa
            bb_prob = bb / pa
            # find proportions of hits for a given pitcher so we know how to divide up their hit counts
            total_prop = conf.steamer_preseason_splits.at[play_id, '1B/PA'][0] + conf.steamer_preseason_splits.at[play_id, '2B/PA'][0] + conf.steamer_preseason_splits.at[play_id, '3B/PA'][0]
            single_proportion = conf.steamer_preseason_splits.at[play_id, '1B/PA'][0] / total_prop
            double_proportion = conf.steamer_preseason_splits.at[play_id, '2B/PA'][0] / total_prop
            triple_proportion = conf.steamer_preseason_splits.at[play_id, '3B/PA'][0] / total_prop
            # now find actual probabilities of single, double, triple
            single_prob = hit_prob * single_proportion
            double_prob = hit_prob * double_proportion
            triple_prob = hit_prob * triple_proportion
            if type(single_prob) == np.ndarray:
                pdb.set_trace()
                player_name = player_name[0]
            final_probs = {
                '1B': single_prob,
                '2B': double_prob,
                '3B': triple_prob,
                'HR': hr_prob,
                'BB': bb_prob,
                'SO': so_prob,
                'OUT': out_prob,
                'HBP': 0.0
            }
            probs['vL'] = final_probs.copy()
            probs['vR'] = final_probs.copy()
            probs['overall'] = final_probs.copy()
        elif conf.steamer_pitcher_approach == 'preseason':
            split = conf.steamer_pitcher_data.at[play_id, 'split']
            sing = conf.steamer_pitcher_data.at[play_id, '1B/PA']
            doub = conf.steamer_pitcher_data.at[play_id, '2B/PA']
            trip = conf.steamer_pitcher_data.at[play_id, '3B/PA']
            hr = conf.steamer_pitcher_data.at[play_id, 'HR/PA']
            bb = conf.steamer_pitcher_data.at[play_id, 'BB/PA']
            so = conf.steamer_pitcher_data.at[play_id, 'SO/PA']
            hbp = conf.steamer_pitcher_data.at[play_id, 'HBP/PA']
            for idx, val in enumerate(split):
                if val == 'total':
                    val = 'overall'
                if '1B' in probs[val]:
                    probs[val]['1B'] = np.mean([probs[val]['1B'], sing[idx]])
                    probs[val]['2B'] = np.mean([probs[val]['2B'], doub[idx]])
                    probs[val]['3B'] = np.mean([probs[val]['3B'], trip[idx]])
                    probs[val]['HR'] = np.mean([probs[val]['HR'], hr[idx]])
                    probs[val]['BB'] = np.mean([probs[val]['BB'], bb[idx]])
                    probs[val]['SO'] = np.mean([probs[val]['SO'], so[idx]])
                    probs[val]['HBP'] = np.mean([probs[val]['HBP'], hbp[idx]])
                    probs[val]['OUT'] = 1 - np.sum(
                        [probs[val]['1B'], probs[val]['2B'], probs[val]['3B'],
                         probs[val]['HR'], probs[val]['BB'], probs[val]['SO'],
                         probs[val]['HBP']])
                else:
                    probs[val]['1B'] = sing[idx]
                    probs[val]['2B'] = doub[idx]
                    probs[val]['3B'] = trip[idx]
                    probs[val]['HR'] = hr[idx]
                    probs[val]['BB'] = bb[idx]
                    probs[val]['SO'] = so[idx]
                    probs[val]['HBP'] = hbp[idx]
    return probs


def load_steamer_stolen_base_stats(play_id):
    if conf.steamer_batter_data is None:
        conf.steamer_batter_data = load_steamer_batter_projections()
    stats = {}
    # get plate appearances and multiply by OBP to get approximate steal opps.
    # Assume players will average 3 chances to steal per ob
    on_base_count = (conf.steamer_batter_data.at[play_id, 'PA'][0] * conf.steamer_batter_data.at[play_id, 'OBP'][0])
    total_attempts = (conf.steamer_batter_data.at[play_id, 'SB'][0] + conf.steamer_batter_data.at[play_id, 'CS'][0]) / 4
    stats['steal'] = total_attempts / on_base_count
    stats['success'] = conf.steamer_batter_data.at[play_id, 'SB'][0] / total_attempts
    stats['cs'] = conf.steamer_batter_data.at[play_id, 'CS'][0] / total_attempts
    return stats


def load_steamer_batter_projections():
    df = pd.read_csv(conf.steamer_ros_split_bat_path, index_col=0)
    # returns steamer projections by mlb_id
    return df


def load_steamer_pitcher_projections():
    if conf.steamer_pitcher_approach == 'preseason':
        df = pd.read_csv(conf.steamer_preseason_split_pit_path, index_col=5)
        return df
    elif conf.steamer_pitcher_approach == 'ros':
        df = pd.read_csv(conf.steamer_ros_pit_path, index_col=0)
        df2 = pd.read_csv(conf.steamer_preseason_split_pit_path, index_col=5)
        return df, df2

# def load_handedness_data(pit_or_bat='b'):
#     if pit_or_bat == 'p':
#         hand = open(conf.pitcher_handedness_path, 'rU')
#     elif pit_or_bat == 'b':
#         hand = open(conf.pitcher_handedness_path, 'rU')
#     else:
#         raise ValueError('Please specify "p" or "b" for handedness type.')
#     data = csv.reader(hand)
#     data_entries = [entry for entry in data]
#     names = [str(entry[0]) for entry in data_entries]
#     data_entries = [entry[1:] for entry in data_entries]
#     if pit_or_bat == 'b':
#         df = pd.DataFrame(data_entries,
#                           columns=['Pos', 'Team', 'Bats'],
#                           index=names)
#     else:
#         df = pd.DataFrame(data_entries,
#                           columns=['Team', 'Throws'],
#                           index=names)
#     return df
