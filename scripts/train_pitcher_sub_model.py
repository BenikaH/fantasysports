import sklearn as sk
import conf
from os import listdir
import util.util as u
import pandas as pd
import re

# def load_retrosheet_roster():
roster_files = [f for f in listdir(conf.retrosheet_path) if '.ROS' in f]
roster = None
for r_f in roster_files:
    if roster is None:
        roster = pd.read_csv(
            '%s%s' % (conf.retrosheet_path, r_f),
            index_col=0,
            header=None,
            names=['last', 'first', 'bats', 'throws', 'team', 'pos'])
    else:
        roster = pd.concat(
            [roster, pd.read_csv(
                '%s%s' % (conf.retrosheet_path, r_f),
                index_col=0,
                header=None,
                names=['last', 'first', 'bats', 'throws', 'team', 'pos'])])
print roster

# training data: [inning, outs, pa, run_diff, so, er, w, h]
training_data = []

ev_files = [f for f in listdir(conf.retrosheet_path) if '.EVA' in f or '.EVN' in f]
print ev_files

for e_f in ev_files:
    fi = open('%s%s' % (conf.retrosheet_path, e_f), 'rb')
    line = fi.readline()
    while line != '':
        if 'id,' in line:
            innning = 0
            data = {
                'home': {
                    'hits': 0,
                    'er': 0,
                    'bb': 0,
                    'so': 0,
                    'pa': 0
                },
                'away': {
                    'hits': 0,
                    'er': 0,
                    'bb': 0,
                    'so': 0,
                    'pa': 0
                }
            }
            home_pitcher = None
            away_pitcher = None
            outs = 0
            inning = 1
            score = [0, 0]
            line = fi.readline()
            away_subbed = False
            home_subbed = False
            while home_pitcher is None and away_pitcher is None:
                if 'start,' in line:
                    line = line.split(',')
                    if line[3] == 0 and roster.at[line[1], 'pos'] == 'P':
                        away_pitcher = line[1]
                    elif line[3] == 1 and roster.at[line[1], 'pos'] == 'P':
                        home_pitcher = line[1]
                    line = fi.readline()
            while not away_subbed and not home_subbed and 'data,' not in line:
                if 'play,' in line:
                    line = line.split(',')
                    if line[6] == 'NP':
                        inning = line[1]
                        inn_stage = line[2]
                        # handle incoming sub
                        line = fi.readline()
                        line = line.split(',')
                        if line[5] == '9':
                            training_data.append(inning, outs, batters_faced, strikeouts, earned runs, walks, hits)

                    event = line[6].split('/')
                    event = [event[0]] + event[1].split('.')

                line = fi.readline()
        else:
            line = fi.readline()
            continue


        line = fi.readline()





# def load_retrosheet_pbp_data():
