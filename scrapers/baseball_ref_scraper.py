"""Handles all scraping of baseball ref."""
from __future__ import division
import sys
from util.cache import cache_disk
from bs4 import BeautifulSoup
from string import ascii_lowercase
import urllib3
import conf
import pandas as pd
import numpy as np
import pdb
import re

####################
# PLAYER FUNCTIONS #
####################


@cache_disk()
def retrieve_player_id_map():
    """Retrieve and cache the links to each player's page."""
    http = urllib3.PoolManager()
    player_id_map = {}
    for char in ascii_lowercase:
        r = http.urlopen(
            'GET', 'http://www.baseball-reference.com/players/%s/' % char,
            preload_content=False)
        soup = BeautifulSoup(r.data, 'html5lib')
        for block in soup.find_all('blockquote'):
            bolds = block.find_all('b')
            if len(bolds) > 0:
                for b in bolds:
                    try:
                        link = b.a.get('href')
                        link = re.sub(r'/players\/[a-z]\/', '', link)
                        link = link.replace('.shtml', '')
                    except:
                        pdb.set_trace()
                    player_id_map[b.a.get_text()] = link
    player_id_map['Tyrell Jenkins'] = 'jenkin001tyr'
    player_id_map['A.J. Reed'] = 'reed--000and'
    player_id_map['Dillon Overton'] = 'overto001dil'
    player_id_map['Joel De La Cruz'] = 'delacr002joe'
    player_id_map['Brock Stewart'] = 'stewar001bro'
    player_id_map['Kevin Gausman'] = 'gausmke01'
    return player_id_map


def get_player_handedness(player_name):
    u.check_load_player_id_map()
    http = urllib3.PoolManager()
    r = http.urlopen(
            'GET',
            'http://www.baseball-reference.com/players/%s/%s.shtml' %
            (conf.player_id_map[player_name][0], conf.player_id_map[player_name]),
            preload_content=False
    )
    soup = BeautifulSoup(r.data, 'html5lib')
    try:
        txt = soup.find('tr').get_text()
        bats = re.search(r'Bats:\s([a-zA-Z]*),', txt).group(1).upper()
        throws = re.search(r'Throws:\s([a-zA-Z]*)\n', txt).group(1).upper()
    except:
        bats = 'RIGHT'
        throws = 'RIGHT'
    return bats, throws


@cache_disk()
def load_handed_probabilities(player_name, start_year='2015', end_year='2016', pit_or_bat='b'):
    ha = load_historical_player_handedness(player_name, start_year, pit_or_bat)
    hist = None
    if ha is not None:
        hist = ha
    year = int(start_year) + 1
    end_year = int(end_year)
    while year <= end_year:
        hand = load_historical_player_handedness(
            player_name, str(year), pit_or_bat)
        if hand is not None:
            if hist is not None:
                hist = hist.add(hand, fill_value=0)
            else:
                hist = hand
        year += 1
    # if they have less than 120 plate appearances, average their stats with
    # league avg
    try:
        probs = calculate_probs_from_hist(hist, pit_or_bat)
        # for less prolific batters, average down to league average
        if (hist.at['RHP', 'PA'] + hist.at['LHP', 'PA']) < 150:
            normalize_batting_by_league_avg(probs, pit_or_bat)
    except:
        # fallback to below average hitting stats
        print "No hitting stats found for %s." % player_name
        return {
            'vL': {
                'OUT': .50,
                '1B': .105,
                '2B': .03,
                '3B': .004,
                'HR': .01,
                'BB': .05,
                'SO': .25,
                'HBP': .001
            },
            'vR': {
                'OUT': .50,
                '1B': .105,
                '2B': .03,
                '3B': .004,
                'HR': .01,
                'BB': .05,
                'SO': .25,
                'HBP': .001
            }
        }
    return probs

def calculate_probs_from_hist(hist, pit_or_bat='b'):
    try:
        if pit_or_bat == 'b':
            single_count_rhp = (hist.at['RHP', 'H'] - (
                hist.at['RHP', '2B'] + hist.at['RHP', '3B'] +
                hist.at['RHP', 'HR']))
            single_count_lhp = (hist.at['LHP', 'H'] - (
                hist.at['LHP', '2B'] + hist.at['LHP', '3B'] +
                hist.at['LHP', 'HR']))
            probs = {
                'vR': {
                    'OUT': (hist.at['RHP', 'PA'] - (
                        single_count_rhp + hist.at['RHP', '2B'] +
                        hist.at['RHP', '3B'] + hist.at['RHP', 'HR'] +
                        hist.at['RHP', 'BB'] + hist.at['RHP', 'SO'] +
                        hist.at['RHP', 'HBP'])) / hist.at['RHP', 'PA'],
                    '1B': single_count_rhp / hist.at['RHP', 'PA'],
                    '2B': hist.at['RHP', '2B'] / hist.at['RHP', 'PA'],
                    '3B': hist.at['RHP', '3B'] / hist.at['RHP', 'PA'],
                    'HR': hist.at['RHP', 'HR'] / hist.at['RHP', 'PA'],
                    'BB': hist.at['RHP', 'BB'] / hist.at['RHP', 'PA'],
                    'SO': hist.at['RHP', 'SO'] / hist.at['RHP', 'PA'],
                    'HBP': hist.at['RHP', 'HBP'] / hist.at['RHP', 'PA']
                },
                'vL': {
                    'OUT': (hist.at['LHP', 'PA'] - (
                        single_count_lhp + hist.at['LHP', '2B'] +
                        hist.at['LHP', '3B'] + hist.at['LHP', 'HR'] +
                        hist.at['LHP', 'BB'] + hist.at['LHP', 'SO'] +
                        hist.at['LHP', 'HBP'])) / hist.at['LHP', 'PA'],
                    '1B': single_count_lhp / hist.at['LHP', 'PA'],
                    '2B': hist.at['LHP', '2B'] / hist.at['LHP', 'PA'],
                    '3B': hist.at['LHP', '3B'] / hist.at['LHP', 'PA'],
                    'HR': hist.at['LHP', 'HR'] / hist.at['LHP', 'PA'],
                    'BB': hist.at['LHP', 'BB'] / hist.at['LHP', 'PA'],
                    'SO': hist.at['LHP', 'SO'] / hist.at['LHP', 'PA'],
                    'HBP': hist.at['LHP', 'HBP'] / hist.at['LHP', 'PA']
                }
            }
        if pit_or_bat == 'p':
            single_count_rhb = (hist.at['RHB', 'H'] - (
                hist.at['RHB', '2B'] + hist.at['RHB', '3B'] +
                hist.at['RHB', 'HR']))
            single_count_lhb = (hist.at['LHB', 'H'] - (
                hist.at['LHB', '2B'] + hist.at['LHB', '3B'] +
                hist.at['LHB', 'HR']))
            probs = {
                'vR': {
                    'OUT': (hist.at['RHB', 'PA'] - (
                        single_count_rhb + hist.at['RHB', '2B'] +
                        hist.at['RHB', '3B'] + hist.at['RHB', 'HR'] +
                        hist.at['RHB', 'BB'] + hist.at['RHB', 'SO'] +
                        hist.at['RHB', 'HBP'])) / hist.at['RHB', 'PA'],
                    '1B': single_count_rhb / hist.at['RHB', 'PA'],
                    '2B': hist.at['RHB', '2B'] / hist.at['RHB', 'PA'],
                    '3B': hist.at['RHB', '3B'] / hist.at['RHB', 'PA'],
                    'HR': hist.at['RHB', 'HR'] / hist.at['RHB', 'PA'],
                    'BB': hist.at['RHB', 'BB'] / hist.at['RHB', 'PA'],
                    'SO': hist.at['RHB', 'SO'] / hist.at['RHB', 'PA'],
                    'HBP': hist.at['RHB', 'HBP'] / hist.at['RHB', 'PA']
                },
                'vL': {
                    'OUT': (hist.at['LHB', 'PA'] - (
                        single_count_lhb + hist.at['LHB', '2B'] +
                        hist.at['LHB', '3B'] + hist.at['LHB', 'HR'] +
                        hist.at['LHB', 'BB'] + hist.at['LHB', 'SO'] +
                        hist.at['LHB', 'HBP'])) / hist.at['LHB', 'PA'],
                    '1B': single_count_lhb / hist.at['LHB', 'PA'],
                    '2B': hist.at['LHB', '2B'] / hist.at['LHB', 'PA'],
                    '3B': hist.at['LHB', '3B'] / hist.at['LHB', 'PA'],
                    'HR': hist.at['LHB', 'HR'] / hist.at['LHB', 'PA'],
                    'BB': hist.at['LHB', 'BB'] / hist.at['LHB', 'PA'],
                    'SO': hist.at['LHB', 'SO'] / hist.at['LHB', 'PA'],
                    'HBP': hist.at['LHB', 'HBP'] / hist.at['LHB', 'PA']
                }
            }
    except:
        # fallback to below average hitting stats
        print "No hitting stats found for %s." % player_name
        return conf.below_avg_batting_probs
    return probs


def normalize_batting_by_league_avg(probs, pit_or_bat='b'):
    # LHP
    probs['vL']['OUT'] = np.mean(
        [probs['vL']['OUT'],
         conf.below_avg_batting_probs['vL']['OUT']])
    probs['vL']['1B'] = np.mean(
        [probs['vL']['1B'],
         conf.below_avg_batting_probs['vL']['1B']])
    probs['vL']['2B'] = np.mean(
        [probs['vL']['2B'],
         conf.below_avg_batting_probs['vL']['2B']])
    probs['vL']['3B'] = np.mean(
        [probs['vL']['3B'],
         conf.below_avg_batting_probs['vL']['3B']])
    probs['vL']['HR'] = np.mean(
        [probs['vL']['HR'],
         conf.below_avg_batting_probs['vL']['HR']])
    probs['vL']['BB'] = np.mean(
        [probs['vL']['BB'],
         conf.below_avg_batting_probs['vL']['BB']])
    probs['vL']['SO'] = np.mean(
        [probs['vL']['SO'],
         conf.below_avg_batting_probs['vL']['SO']])
    probs['vL']['HBP'] = np.mean(
        [probs['vL']['HBP'],
         conf.below_avg_batting_probs['vL']['HBP']])
    # RHP
    probs['vR']['OUT'] = np.mean(
        [probs['vR']['OUT'],
         conf.below_avg_batting_probs['vR']['OUT']])
    probs['vR']['1B'] = np.mean(
        [probs['vR']['1B'],
         conf.below_avg_batting_probs['vR']['1B']])
    probs['vR']['2B'] = np.mean(
        [probs['vR']['2B'],
         conf.below_avg_batting_probs['vR']['2B']])
    probs['vR']['3B'] = np.mean(
        [probs['vR']['3B'],
         conf.below_avg_batting_probs['vR']['3B']])
    probs['vR']['HR'] = np.mean(
        [probs['vR']['HR'],
         conf.below_avg_batting_probs['vR']['HR']])
    probs['vR']['BB'] = np.mean(
        [probs['vR']['BB'],
         conf.below_avg_batting_probs['vR']['BB']])
    probs['vR']['SO'] = np.mean(
        [probs['vR']['SO'],
         conf.below_avg_batting_probs['vR']['SO']])
    probs['vR']['HBP'] = np.mean(
        [probs['vR']['HBP'],
         conf.below_avg_batting_probs['vR']['HBP']])


@cache_disk()
def load_historical_player_handedness(player_name, year='Career', pit_or_bat='b'):
    idm = retrieve_player_id_map()
    if player_name in conf.known_player_conversions:
        player_name = conf.known_player_conversions[player_name]
    http = urllib3.PoolManager()
    if player_name in idm:
        r = http.urlopen('GET',
                         'http://www.baseball-reference.com/players/split.cgi?id=%s&year=%s&t=%s' %
                         (idm[player_name], year, pit_or_bat),
                         preload_content=False)
    elif player_name in conf.known_player_conversions and\
            conf.known_player_conversions[player_name] in idm:
        r = http.urlopen('GET',
                         'http://www.baseball-reference.com/players/split.cgi?id=%s&year=%s&t=%s' %
                         (idm[player_name], year, pit_or_bat),
                         preload_content=False)
    else:
        pdb.set_trace()
        raise ValueError("Player %s not found in Baseball Reference." % player_name)
    soup = BeautifulSoup(r.data, 'html5lib')
    if soup.find(id='plato'):
        player_split_data = soup.find(id='plato').find_all('tr')
    else:
        return None
    final_splits = []
    for row in player_split_data:
        if len(row.find_all('th')) > 0:
                continue
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        if year == 'Career':
            cols = cols[1:]
        # cols = [ele for ele in cols if ele]
        cols[0] = cols[0].replace('vs ', '')
        final_splits.append(cols)
    key = [sp[0] for sp in final_splits]
    final_splits = [sp[1:] for sp in final_splits]
    if pit_or_bat == 'b':
        cols = [
            'G', 'GS', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI',
            'SB', 'CS', 'BB', 'SO', 'BA', 'OBP', 'SLG', 'OPS', 'TB', 'GDP',
            'HBP', 'SH', 'SF', 'IBB', 'ROE', 'BAbip', 'tOPS+', 'sOPS+'
        ]
    if pit_or_bat == 'p':
        cols = [
            'G', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'SB',
            'CS', 'BB', 'SO', 'SO/W', 'BA', 'OBP', 'SLG', 'OPS', 'TB', 'GDP',
            'HBP', 'SH', 'SF', 'IBB', 'ROE', 'BAbip', 'tOPS+', 'sOPS+'
        ]
    if year == 'Career':
        cols.pop()
    splits_df = pd.DataFrame(final_splits, index=key, columns=cols)
    splits_df = splits_df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
    return splits_df


@cache_disk()
def load_historical_player_game_logs(player_name, year='2015'):
    """Load logs of a player's games from a specific year."""
    u.check_load_player_id_map()
    http = urllib3.PoolManager()
    agg_stats = None
    if player_name in conf.player_id_map:
        r = http.urlopen('GET',
                         'http://www.baseball-reference.com/players/gl.cgi?' +
                         'id=%s&t=b&year=%s' %
                         (conf.player_id_map.at[player_name, 'BREFID'], year),
                         preload_content=False)
        soup = BeautifulSoup(r.data, 'html5lib')
        player_games = soup.find(id='batting_gamelogs').find_all('tr')
        game_logs = []
        for game in player_games:
            if len(game.find_all('th')) > 0:
                continue
            cols = game.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            cols = [ele for ele in cols if ele]
            if cols[5] == '@':
                cols[5] = 'a'
            else:
                cols.insert(5, 'h')
            game_logs.append(cols)
        agg_stats = game_logs.pop()
        agg_stats.pop(5)
    else:
        raise ValueError("Player %s not found." % player_name)
    try:
        gl_df = pd.DataFrame(game_logs, columns=[
            'num', 'gcar', 'gtm', 'date', 'tm', 'h/a', 'opp', 'rslt', 'inngs',
            'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'IBB', 'SO',
            'HBP', 'SH', 'SF', 'ROE', 'GDP', 'SB', 'CS', 'BA', 'OBP', 'SLG',
            'OPS', 'BOP', 'aLI', 'WPA', 'RE24', 'DFS(DK)', 'DFS(FD)', 'Pos'])
    except:
        return None
    agg_stats = pd.DataFrame([agg_stats], columns=[
        'team', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'IBB',
        'SO', 'HBP', 'SH', 'SF', 'GDP', 'SB', 'CS', 'BA', 'OBP', 'SLG',
        'OPS'])
    return gl_df, agg_stats


def load_recent_player_game_logs(player_name):
    """Load same as above but with no caching."""
    u.check_load_player_id_map()
    http = urllib3.PoolManager()
    agg_stats = None
    if player_name in conf.player_id_map:
        r = http.urlopen('GET',
                         'http://www.baseball-reference.com/players/gl.cgi?id=%s&t=b&year=2016' %
                         (conf.player_id_map.at[player_name, 'BREFID']),
                         preload_content=False)
        soup = BeautifulSoup(r.data, 'html5lib')
        player_games = soup.find(id='batting_gamelogs').find_all('tr')
        game_logs = []
        for game in player_games:
            if len(game.find_all('th')) > 0:
                continue
            cols = game.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            cols = [ele for ele in cols if ele]
            if cols[5] == '@':
                cols[5] = 'a'
            else:
                cols.insert(5, 'h')
            game_logs.append(cols)
        agg_stats = game_logs.pop()
        agg_stats.pop(5)
    else:
        raise ValueError("Player %s not found." % player_name)
    try:
        gl_df = pd.DataFrame(game_logs, columns=[
            'num', 'gcar', 'gtm', 'date', 'tm', 'h/a', 'opp', 'rslt', 'inngs',
            'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'IBB', 'SO',
            'HBP', 'SH', 'SF', 'ROE', 'GDP', 'SB', 'CS', 'BA', 'OBP', 'SLG',
            'OPS', 'BOP', 'aLI', 'WPA', 'RE24', 'DFS(DK)', 'DFS(FD)', 'Pos'])
    except:
        return None
    agg_stats = pd.DataFrame([agg_stats], columns=[
        'team', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI', 'BB', 'IBB',
        'SO', 'HBP', 'SH', 'SF', 'GDP', 'SB', 'CS', 'BA', 'OBP', 'SLG',
        'OPS'])
    return gl_df, agg_stats

##################
# TEAM FUNCTIONS #
##################

# @cache_disk()
# def retrieve_team_link_map():
#     """Retrieve links related to teams."""
#     if team_name in conf.bb_ref_teams:
#         team_name = conf.bb_ref_teams[team_name]
#     http = urllib3.PoolManager()
#     team_link_map = {}
#     for char in ascii_lowercase:
#         r = http.urlopen(
#             'GET', 'http://www.baseball-reference.com/teams/%s/' % char,
#             preload_content=False)
#         soup = BeautifulSoup(r.data, 'html5lib')
#         for block in soup.find_all('blockquote'):
#             bolds = block.find_all('b')
#             if len(bolds) > 0:
#                 for b in bolds:
#                     link = b.a
#                     team_link_map[link.get_text()] = link.get('href')


@cache_disk()
def retrieve_team_roster(team_name):
    """Retrieve the full roster of a specified team."""
    if team_name in conf.bb_ref_teams:
        team_name = conf.bb_ref_teams[team_name]
    http = urllib3.PoolManager()
    roster = {}
    r = http.urlopen(
        'GET', 'http://www.baseball-reference.com/teams/%s/2016-roster.shtml' %
        team_name,
        preload_content=False)
    soup = BeautifulSoup(r.data, 'html5lib')
    team_roster = soup.find(id='40man').find_all('tr')
    for row in team_roster:
        if len(row.find_all('th')) > 0:
            continue
        cols = row.find_all('td')
        if cols[2].find('strong'):
            roster[cols[2].text.strip()] = cols[4].text.strip()
    return roster


def retrieve_most_recent_batting_order(team_name):
    """Return the most recent batting order of a particular team."""
    if team_name in conf.rotochamp_teams:
        team_name = conf.rotochamp_teams[team_name]
    http = urllib3.PoolManager()
    bo = []
    r = http.urlopen(
        'GET', 'http://rotochamp.com/baseball/TeamPage.aspx?TeamID=%s' %
        team_name,
        preload_content=False)
    soup = BeautifulSoup(r.data, 'html5lib')
    try:
        order = soup.find(id='MainContent_gridProjectedLineup').find_all('tr')
        for row in order:
            if len(row.find_all('th')) > 0:
                continue
            cols = row.find_all('td')
            bo.append(cols[1].text.strip())
    except:
        pdb.set_trace()
        return None
    return bo


def retrieve_pitching_rotation(team_name):
    if team_name in conf.rotochamp_teams:
        team_name = conf.rotochamp_teams[team_name]
    http = urllib3.PoolManager()
    b_rotation = []
    r = http.urlopen(
        'GET', 'http://rotochamp.com/baseball/TeamPage.aspx?TeamID=%s' %
        team_name,
        preload_content=False)
    soup = BeautifulSoup(r.data, 'html5lib')
    rotation = soup.find(id='MainContent_gridProjectedRotation').find_all('tr')
    for row in rotation:
        if len(row.find_all('th')) > 0:
            continue
        cols = row.find_all('td')
        b_rotation.append(cols[1].text.strip())
    return b_rotation


def load_team_bullpen(team_name):
    """Load current team bullpen."""
    if team_name in conf.rotochamp_teams:
        team_name = conf.rotochamp_teams[team_name]
    http = urllib3.PoolManager()
    bullpen = []
    col_headers = None
    r = http.urlopen(
        'GET', 'http://rotochamp.com/baseball/TeamPage.aspx?TeamID=%s' %
        team_name,
        preload_content=False)
    soup = BeautifulSoup(r.data, 'html5lib')
    order = soup.find(id='MainContent_gridBullpen').find_all('tr')
    names = []
    for row in order:
        if len(row.find_all('th')) > 0:
            cols = row.find_all('th')
            col_headers = [ele.text.strip() for ele in cols]
            col_headers = [col_headers[0]] + col_headers[2:]
        else:
            cols = row.find_all('td')
            entry = [ele.text.strip() for ele in cols]
            names.append(entry[1])
            bullpen.append([entry[0]] + entry[2:])
    return pd.DataFrame(bullpen,
                        columns=col_headers,
                        index=names)
