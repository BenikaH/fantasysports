from bs4 import BeautifulSoup
import urllib3
from util.util import standardize_team_name, standardize_player_name
import pandas as pd

def load_prev_mlb_salaries_and_points(date, site):
    http = urllib3.PoolManager()
    if site == 'fanduel':
        code = 'fd'
    else:
        code = 'dk'
    fmt_date = date.strftime("%m%d")
    
    """HITTERS"""
    r = http.urlopen('GET', "http://rotoguru1.com/cgi-bin/byday.pl?date=%s&game=%s" % (fmt_date, code),
                     preload_content=False)

def retrieve_previous_mlb_batting_order(date):
    return None