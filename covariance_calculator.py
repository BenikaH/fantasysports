"""Generates lineups from pre-loaded projections."""
from __future__ import division
from scrapers.rotogrinder_scraper import\
    retrieve_mlb_player_salaries_and_positions, retrieve_mlb_batting_order
from dateutil.parser import parse
import sys
import datetime as dt
import pandas as pd
import numpy as np
import math
import conf
import pdb

fmt_date = sys.argv[1]
site = sys.argv[2]
conf.proj_iteration = sys.argv[3]

df = pd.read_csv('./projections/%s_%s_%s.csv' % (site, fmt_date, conf.proj_iteration), index_col=0)
cov = df.transpose().cov()

idx = df.index[:]
means = []
# join our two data frames
projections_overall = df.join(pd.read_csv('./simplified_projections/%s_%s_%s.csv' % (site, fmt_date, conf.proj_iteration), index_col=0))

print projections_overall

lineups = pd.read_csv('./lineups/%s_%s_%s_linear.csv' % (site, fmt_date, conf.proj_iteration), index_col=0)
l_var = []
l_cost = []

for l_num in lineups.index:
    var = 0
    salary = 0
    cur_lineup = lineups.loc[l_num]
    # pdb.set_trace()
    if site == 'fanduel':
        for i in range(9):
            salary += projections_overall.at[cur_lineup[i], 'cost']
            for j in range(9 - i):
                if i == j:
                    var += cov.at[cur_lineup[i], cur_lineup[j]]
                else:
                    var += 2 * cov.at[cur_lineup[i], cur_lineup[j]]
    elif site == 'draftkings':
        for i in range(10):
            salary += projections_overall.at[cur_lineup[i], 'cost']
            for j in range(10 - i):
                if i == j:
                    var += cov.at[cur_lineup[i], cur_lineup[j]]
                else:
                    var += 2 * cov.at[cur_lineup[i], cur_lineup[j]]
    l_var.append(var)
    l_cost.append(salary)

l_stdev = [math.sqrt(x) for x in l_var]
lineups['salary'] = l_cost
lineups['variance'] = l_var
lineups['stdev'] = l_stdev

lineups.to_csv('./lineups/%s_%s_%s_linear.csv' % (site, fmt_date, conf.proj_iteration))
