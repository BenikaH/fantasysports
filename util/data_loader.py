"""Contains methods for loading Local Data"""
import csv
from cache import cache_disk
from util import standardize_team_name
import pandas as pd
import conf
import pdb


# @cache_disk()
def load_mlb_schedule():
    sch = open(conf.schedule_path)
    data = csv.reader(sch)
    data_entries = [entry for entry in data]
    for ent in data_entries:
        ent[2] = standardize_team_name(ent[2])
        ent[5] = standardize_team_name(ent[5])
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
                      index=[standardize_team_name(ent[0]) for ent in data_entries]
                      )
    return df


def load_handedness_data(pit_or_bat='b'):
    if pit_or_bat == 'p':
        hand = open(conf.pitcher_handedness_path, 'rU')
    elif pit_or_bat == 'b':
        hand = open(conf.batter_handedness_path, 'rU')
    else:
        raise ValueError('Please specify "p" or "b" for handedness type.')
    data = csv.reader(hand)
    data_entries = [entry for entry in data]
    names = [str(entry[0]) for entry in data_entries]
    data_entries = [entry[1:] for entry in data_entries]
    if pit_or_bat == 'b':
        df = pd.DataFrame(data_entries,
                          columns=['Pos', 'Team', 'Bats'],
                          index=names)
    else:
        df = pd.DataFrame(data_entries,
                          columns=['Team', 'Throws'],
                          index=names)
    return df
