"""Extracts sabersim data from sabersim.com."""
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import conf
# import re
import pdb
import pandas as pd


def retrieve_numberfire_batter_predictions_and_salaries():
    driver = webdriver.Chrome(conf.chromedriver_path)
    driver.get("https://www.numberfire.com/mlb/daily-fantasy/daily-baseball-projections")
    time.sleep(2)
    driver.find_element_by_id('login-google').click()
    time.sleep(2)
    driver.find_element_by_id(
        'Email').send_keys(conf.google_creds['email'])
    driver.find_element_by_id(
        'next').click()
    time.sleep(2)
    driver.find_element_by_id(
        'Passwd').send_keys(conf.google_creds['password'])
    driver.find_element_by_id(
        'signIn').click()
    time.sleep(5)
    table_info = driver.find_element_by_tag_name(
        'table').get_attribute('innerHTML')
    soup = BeautifulSoup(table_info, 'html5lib')
    player_lists = soup.get_text().replace('\t', '').split('\n')[204:]
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

    driver.quit()
    # separate names
    names = [item[0] for item in final_data]
    final_data = [item[1:] for item in final_data]
    # build data frame
    batter_data_frame = pd.DataFrame(final_data, index=names,
        columns=['nf_pos', 'nf_team', 'nf_name', 'nf_opp_team', 'nf_gametime',
                 'nf_pa', 'nf_bb', 'nf_1b', 'nf_2b', 'nf_3b', 'nf_hr', 'nf_r',
                 'nf_rbi', 'nf_sb', 'nf_so', 'nf_avg', 'nf_pred', 'nf_cost',
                 'nf_value'])
    return batter_data_frame
