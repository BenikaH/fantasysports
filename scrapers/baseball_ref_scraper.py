from util.cache import cache_disk
from bs4 import BeautifulSoup
import urllib3
import conf
import pandas as pd
from string import ascii_lowercase
from util.cache import cache_disk
import pdb
import re

####################
# PLAYER FUNCTIONS #
####################


@cache_disk()
def retrieve_player_id_map():
    """Retrieve and cache the links to each player's page."""
    http = urllib3.PoolManager()
    player_link_map = {}
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
                    player_link_map[b.a.get_text()] = link
    return player_link_map

# ALL TODO FROM HERE ON

# @cache_disk()
def load_historical_player_handedness(player_name, year='Career'):
    if conf.player_id_map is None:
        conf.player_id_map = retrieve_player_id_map()
    http = urllib3.PoolManager()
    if player_name in conf.player_id_map:
        r = http.urlopen('GET',
                         'http://www.baseball-reference.com/players/split.cgi?id=%s&year=%s' %
                         (conf.player_id_map[player_name], year),
                         preload_content=False)
    soup = BeautifulSoup(r.data, 'html5lib')
    player_split_data = soup.find(id='plato').find_all('tr')
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
    cols = [
        'G', 'GS', 'PA', 'AB', 'R', 'H', '2B', '3B', 'HR', 'RBI',
        'SB', 'CS', 'BB', 'SO', 'BA', 'OBP', 'SLG', 'OPS', 'TB', 'GDP',
        'HBP', 'SH', 'SF', 'IBB', 'ROE', 'BAbip', 'tOPS+', 'sOPS+'
    ]
    if year == 'Career':
        cols.pop()
    splits_df = pd.DataFrame(final_splits, index=key, columns=cols)
    return splits_df

@cache_disk()
def load_historical_player_game_logs(player_name, year='2015'):
    if conf.player_id_map is None:
        conf.player_id_map = retrieve_player_id_map()
    http = urllib3.PoolManager()
    agg_stats = None
    if player_name in conf.player_id_map:
        r = http.urlopen('GET',
                         'http://www.baseball-reference.com/players/gl.cgi?id=%s&t=b&year=%s' %
                         (conf.player_id_map[player_name], year),
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


# Same as above but with no caching
def load_recent_player_game_logs(player_name):
    if conf.player_id_map is None:
        conf.player_id_map = retrieve_player_id_map()
    http = urllib3.PoolManager()
    agg_stats = None
    if player_name in conf.player_id_map:
        r = http.urlopen('GET',
                         'http://www.baseball-reference.com/players/gl.cgi?id=%s&t=b&year=2016' %
                         (conf.player_id_map[player_name]),
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


@cache_disk()
def retrieve_team_link_map():
    # TODO
    http = urllib3.PoolManager()
    team_link_map = {}
    for char in ascii_lowercase:
        r = http.urlopen(
            'GET', 'http://www.baseball-reference.com/teams/%s/' % char,
            preload_content=False)
        soup = BeautifulSoup(r.data, 'html5lib')
        for block in soup.find_all('blockquote'):
            bolds = block.find_all('b')
            if len(bolds) > 0:
                for b in bolds:
                    link = b.a
                    team_link_map[link.get_text()] = link.get('href')


def retrieve_most_recent_batting_order(team_name):
    """Return the most recent batting order of a particular team."""
    return []

def get_player_list(team_name):
    return []
