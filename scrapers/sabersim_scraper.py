"""Extracts sabersim data from sabersim.com."""
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import conf
import re
import pandas as pd


def retrieve_saber_sim_player_predictions():
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
