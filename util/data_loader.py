"""Contains methods for loading Local Data"""
import csv
from cache import cache_disk
import pandas as pd
import conf


@cache_disk()
def load_mlb_schedule():
    sch = open(conf.schedule_path)
    data = csv.reader(sch)
    data_entries = [entry for entry in data]
    df = pd.DataFrame(data_entries,
                      columns=['date', 'null', 'day', 'rg_opp_team', 'rg_pred']
                      )
    return df


@cache_disk()
def load_handedness_data(pit_or_bat='b'):
    if pit_or_bat == 'p':
        hand = open(conf.pitcher_handedness_path)
    elif pit_or_bat == 'b':
        hand = open(conf.batter_handedness_path, 'rU')
    else:
        raise ValueError('Please specify "p" or "b" for handedness type.')
    data = csv.reader(hand)
    data_entries = [entry for entry in data]
    names = [entry[0] for entry in data_entries]
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
