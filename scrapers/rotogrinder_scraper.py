from bs4 import BeautifulSoup
import urllib3
import time
import csv
import io
import conf
import pdb
import pandas as pd


def retrieve_rotogrinder_mlb_projections():
    """
    MLB Projection Retrieval
    """
    http = urllib3.PoolManager()

    """HITTERS"""
    r = http.urlopen('GET', conf.rotogrinder_hitter_path, preload_content=False)
    hitter_data = csv.reader(r)
    data_formatted = [entry for entry in hitter_data]
    names = [entry[0] for entry in data_formatted][1:]
    batter_info = [entry[1:] for entry in data_formatted][1:]
    batter_info = [el[0:4] + [el[6]] for el in batter_info]
    batter_data_frame = pd.DataFrame(batter_info, index=names,
        columns=['rg_cost', 'rg_team', 'rg_pos', 'rg_opp_team','rg_pred'])

    """PITCHERS"""
    r = http.urlopen('GET', conf.rotogrinder_pitcher_path, preload_content=False)
    pitcher_data = csv.reader(r)
    data_formatted = [entry for entry in pitcher_data]
    names = [entry[0] for entry in data_formatted][1:]
    pitcher_info = [entry[1:] for entry in data_formatted][1:]
    pitcher_info = [el[0:4] + [el[6]] for el in pitcher_info]
    pitcher_data_frame = pd.DataFrame(pitcher_info, index=names,
        columns=['rg_cost', 'rg_team', 'rg_pos', 'rg_opp_team', 'rg_pred'])

    return batter_data_frame, pitcher_data_frame


def retrieve_rotogrinder_nba_projections():
    """
    NBA Projection Retrieval
    """
    http = urllib3.PoolManager()
    r = http.urlopen('GET', conf.rotogrinder_nba_path, preload_content=False)
    player_data = csv.reader(r)
    data_formatted = [entry for entry in player_data]
    names = [entry[0] for entry in data_formatted][1:]
    player_info = [entry[1:] for entry in data_formatted][1:]
    player_data_frame = pd.DataFrame(player_info, index=names,
        columns=['rg_cost', 'rg_team', 'rg_pos', 'rg_opp_team', 'rg_ceil', 'rg_floor', 'rg_pred'])
    return player_data_frame
