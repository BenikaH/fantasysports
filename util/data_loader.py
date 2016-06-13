"""Contains methods for loading Local Data"""
import csv
from cache import cache_disk
import pandas as pd


@cache_disk()
def load_mlb_schedule():
    sch = open('schedule2016.txt')
    data = csv.reader(sch)
    data_entries = [entry for entry in data]
    df = pd.DataFrame(data_entries,
                      columns=['date', 'null', 'day', 'rg_opp_team', 'rg_pred'])
    return df