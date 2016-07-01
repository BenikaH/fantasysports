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


def load_steamer_batter_projections():
    df = pd.read_csv(conf.steamer_ros_split_bat_path, index_col=0)
    # returns steamer projections by mlb_id
    return df


def load_steamer_pitcher_projections():
    df = pd.read_csv(conf.steamer_preseason_split_pit_path, index_col=5)
    return df

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
