"""Extracts sabersim data from sabersim.com."""
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib3
import time
import conf
import pdb
import pandas as pd


def retrieve_numberfire_mlb_predictions_and_salaries():
    """
    MLB Projection Retrieval
    """
    """HITTERS"""
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://www.numberfire.com/mlb/daily-fantasy/daily-baseball-projections')
    soup = BeautifulSoup(r.data, 'html5lib')
    player_lists = soup.find(id='projection-data').get_text().replace('\t', '').split('\n')
    player_lists = [el for el in player_lists if el]
    final_data = []
    index = 0
    while index < len(player_lists):
        entry = player_lists[index + 2:index + 20]
        if 'OUT' not in entry:
            final_data.append(entry)
            index += 20
        else:
            index += 21
    # split up the player info
    for idx, player in enumerate(final_data):
        split_info = final_data[idx][0].replace(')', '').split(' (')
        player_split = [split_info[0]] + split_info[1].split(', ')
        final_data[idx] = player_split + final_data[idx][1:]

    # separate names
    names = [item[0] for item in final_data]
    final_data = [item[1:] for item in final_data]
    # build data frame
    batter_data_frame = pd.DataFrame(final_data, index=names,
        columns=['nf_pos', 'nf_team', 'nf_name', 'nf_opp_team', 'nf_gametime',
                 'nf_pa', 'nf_bb', 'nf_1b', 'nf_2b', 'nf_3b', 'nf_hr', 'nf_r',
                 'nf_rbi', 'nf_sb', 'nf_so', 'nf_avg', 'nf_pred', 'nf_cost',
                 'nf_value'])
    """PITCHERS"""
    r = http.request('GET', 'https://www.numberfire.com/mlb/daily-fantasy/daily-baseball-projections')
    soup = BeautifulSoup(r.data, 'html5lib')
    time.sleep(4)
    pitcher_lists = soup.find(id='projection-data').get_text().replace('\t', '').split('\n')
    pitcher_lists = [el for el in pitcher_lists if el]
    pitcher_data = []
    index = 0
    while index < len(pitcher_lists):
        entry = pitcher_lists[index + 2:index + 20]
        if 'OUT' not in entry:
            pitcher_data.append(entry)
            index += 20
        else:
            index += 21
    pdb.set_trace()
    # split up the player info
    for idx, player in enumerate(pitcher_data):
        split_info = pitcher_data[idx][0].replace(')', '').split(' (')
        player_split = [split_info[0]] + split_info[1].split(', ')
        pitcher_data[idx] = player_split + pitcher_data[idx][1:]

    names = [item[0] for item in pitcher_data]
    pitcher_data = [item[1:] for item in pitcher_data]
    # build data frame
    pitcher_data_frame = pd.DataFrame(pitcher_data, index=names,
        columns=['nf_pos', 'nf_team', 'nf_name', 'nf_opp_team', 'nf_gametime',
                 'nf_w', 'nf_l', 'nf_sv', 'nf_ip', 'nf_h', 'nf_er', 'nf_hr', 'nf_so',
                 'nf_bb', 'nf_era', 'nf_whip', 'nf_pred', 'nf_cost',
                 'nf_value'])
    return batter_data_frame, pitcher_data_frame


def retrieve_numberfire_nba_predictions_and_salaries():
    """
    NBA Projection Retrieval.
    """
    driver = webdriver.Chrome(conf.chromedriver_path)
    driver.get("https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections")
    time.sleep(2)
    table_info = driver.find_element_by_id(
        'projection-data').get_attribute('innerHTML')
    soup = BeautifulSoup(table_info, 'html5lib')
    driver.quit()
    player_lists = soup.get_text().replace('\t', '').split('\n')
    player_lists = [el for el in player_lists if el]
    player_data = []
    index = 0
    while index < len(player_lists):
        entry = player_lists[index + 2:index + 15]
        if 'OUT' not in entry and 'GTD' not in entry:
            player_data.append(entry)
            index += 15
        else:
            index += 16
    # split up the player info
    for idx, player in enumerate(player_data):
        split_info = player_data[idx][0].replace(')', '').split(' (')
        player_split = [split_info[0]] + split_info[1].split(', ')
        player_data[idx] = player_split + player_data[idx][1:]

    names = [item[0] for item in player_data]
    player_data = [item[1:] for item in player_data]
    # build data frame
    player_data_frame = pd.DataFrame(player_data, index=names,
        columns=['nf_pos', 'nf_team', 'nf_name', 'nf_opp_team', 'nf_min',
                 'nf_pts', 'nf_reb', 'nf_ast', 'nf_stl', 'nf_blk', 'nf_to',
                 'nf_pred', 'nf_cost', 'nf_value'])
    return player_data_frame
