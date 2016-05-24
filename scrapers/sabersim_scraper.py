"""Extracts sabersim data from sabersim.com."""
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import urllib3
import conf
import re
import pandas as pd
import pdb


def get_saber_sim_projections_from_fangraphs():
    """Retrieve predictions from fangraph."""
    http = urllib3.PoolManager()
    """BATTERS"""
    batter_data = []
    for team_idx in range(1, 30):
        r = http.urlopen('GET', 'http://www.fangraphs.com/dailyprojections.aspx?pos=all&stats=bat&type=sabersim&team=%s&lg=all&players=0' % team_idx, preload_content=False)
        soup = BeautifulSoup(r.data, 'html5lib')
        team_data_table = soup.find('table', class_='rgMasterTable')
        projections = team_data_table.find('tbody')
        tds = projections.find_all('td')
        player_info = [t.get_text() for t in tds]
        idx = 0
        while idx < len(player_info):
            batter_data.append(player_info[idx: idx + 19])
            idx += 19
    batter_names = [batter[0] for batter in batter_data]
    batter_data = [batter[1:] for batter in batter_data]
    batter_data_frame =\
        pd.DataFrame(batter_data, index=batter_names, columns=
                     ['ss_team', 'ss_game', 'ss_pos', 'ss_pa', 'ss_h', 'ss_1b',
                      'ss_2b', 'ss_3b', 'ss_hr', 'ss_r', 'ss_rbi',
                      'ss_sb', 'ss_cs', 'ss_bb', 'ss_so', 'ss_yahoo_pred',
                      'ss_fd_pred', 'ss_dk_pred'])
    """PITCHERS"""
    leagues = ['al', 'nl']
    pitcher_data = []
    for l in leagues:
        r = http.urlopen('GET', 'http://www.fangraphs.com/dailyprojections.aspx?pos=all&stats=pit&type=sabersim&team=0&lg=%s&players=0' % l, preload_content=False)
        soup = BeautifulSoup(r.data, 'html5lib')
        league_data_table = soup.find('table', class_='rgMasterTable')
        projections = league_data_table.find('tbody')
        tds = projections.find_all('td')
        pitcher_info = [t.get_text() for t in tds]
        idx = 0
        while idx < len(pitcher_info):
            pitcher_data.append(pitcher_info[idx: idx + 16])
            idx += 16
    pitcher_names = [pitcher[0] for pitcher in pitcher_data]
    pitcher_data = [pitcher[1:] for pitcher in pitcher_data]
    pitcher_data_frame =\
        pd.DataFrame(pitcher_data, index=pitcher_names, columns=
                     ['ss_team', 'ss_game', 'ss_w', 'ss_ip', 'ss_tbf', 'ss_h',
                      'ss_1b', 'ss_2b', 'ss_3b', 'ss_hr', 'ss_bb',
                      'ss_so', 'ss_yahoo_pred', 'ss_fd_pred', 'ss_dk_pred'])
    return batter_data_frame, pitcher_data_frame

def retrieve_saber_sim_player_predictions():
    """Deprecated."""
    driver = webdriver.Chrome(conf.chromedriver_path)
    driver.get('https://www.sabersim.com/mlb')
    driver.find_element_by_partial_link_text('Sign in').click()
    driver.find_element_by_id(
        'signinEmail').send_keys(conf.sabersim_creds['username'])
    driver.find_element_by_id(
        'signinPassword').send_keys(conf.sabersim_creds['password'])
    driver.find_element_by_id('signinPassword').submit()
    time.sleep(4)
    driver.find_elements_by_tag_name('a')[5].click()
    time.sleep(8)
    # batter info
    table_info = driver.find_element_by_tag_name(
        'table').get_attribute('innerHTML')
    soup = BeautifulSoup(table_info, 'html5lib')
    data_text = soup.get_text().split('\n')
    for idx, txt in enumerate(data_text):
        data_text[idx] = re.sub(r'\s{2,}', '', txt)
    data_text[3:len(data_text) - 3]
    final_data = []
    index = 3
    while index < len(data_text) - 3:
        final_data.append(data_text[index: index + 14])
        index += 15
    driver.quit()
    names = [item[0] for item in final_data]
    final_data = [item[1:] for item in final_data]
    batter_data_frame =\
        pd.DataFrame(final_data, index=names,
            columns=['ss_team', 'ss_position', 'ss_h', 'ss_hr', 'ss_rbi',
                     'ss_r', 'ss_bb', 'ss_so', 'ss_sb', 'ss_avg', 'ss_obp',
                     'ss_slg', 'ss_ops'])
    return batter_data_frame
