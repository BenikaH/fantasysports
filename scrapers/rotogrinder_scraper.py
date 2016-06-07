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


def retrieve_mlb_batting_order():
    batting_orders = {}
    http = urllib3.PoolManager()
    r = http.urlopen('GET', 'https://rotogrinders.com/lineups/mlb?site=fanduel', preload_content=False)
    soup = BeautifulSoup(r.data, 'html5lib')
    container = soup.find('ul', class_='lineup')
    cards = container.find_all('li')
    for card in cards:
        team_names = card.find_all('span', class_='team-name')
        try:
            away_team = team_names[0].find(class_='shrt').get_text()
        except:
            continue
        away_players = card.find('div', class_='away-team').find('ul', class_='players').find_all('li', class_='player')
        away_order = []
        for player in away_players:
            try:
                away_order.append(player.find('a').get_text())
            except:
                continue
        batting_orders[away_team] = away_order
        home_team = team_names[1].find(class_='shrt').get_text()
        try:
            home_players = card.find('div', class_='home-team').find('ul', class_='players').find_all('li', class_='player')
        except:
            continue
        home_order = []
        for player in home_players:
            home_order.append(player.find('a').get_text())
        batting_orders[home_team] = home_order
    return batting_orders
