"""Generates lineups from pre-loaded projections."""
from __future__ import division
from scrapers.rotogrinder_scraper import\
    retrieve_mlb_player_salaries_and_positions, retrieve_mlb_batting_order
from dateutil.parser import parse
import datetime as dt
import pandas as pd
import numpy as np
import math
import conf
import pdb

if conf.projection_date == 'today':
    proj_date = dt.datetime.now()
else:
    proj_date = parse(conf.projection_date)
fmt_date = proj_date.strftime('%Y_%m_%d')

df = pd.read_csv('./projections/%s_%s_%s.csv' % (conf.site, fmt_date, conf.proj_iteration), index_col=0)
cov = df.transpose().cov()

idx = df.index[:]
means = []
# join our two data frames
projections_overall = df.join(pd.read_csv('./simplified_projections/%s_%s_%s.csv' % (conf.site, fmt_date, conf.proj_iteration), index_col=0))

print projections_overall

lineups = pd.read_csv('./lineups/%s_%s_%s.csv' % (conf.site, fmt_date, conf.proj_iteration), index_col=0)
l_var = []
l_cost = []

for l_num in lineups.index:
    var = 0
    salary = 0
    cur_lineup = lineups.loc[l_num]
    # pdb.set_trace()
    if conf.site == 'fanduel':
        for i in range(9):
            salary += projections_overall.at[cur_lineup['P%d' % (i + 1)], 'cost']
            for j in range(9 - i):
                if i == j:
                    var += cov.at[cur_lineup['P%d' % (i + 1)], cur_lineup['P%d' % (j + 1)]]
                else:
                    var += 2 * cov.at[cur_lineup['P%d' % (i + 1)], cur_lineup['P%d' % (j + 1)]]
    elif conf.site == 'draftkings':
        for i in range(10):
            salary += projections_overall.at[cur_lineup['P%d' % (i + 1)], 'cost']
            for j in range(10 - i):
                if i == j:
                    var += cov.at[cur_lineup['P%d' % (i + 1)], cur_lineup['P%d' % (j + 1)]]
                else:
                    var += 2 * cov.at[cur_lineup['P%d' % (i + 1)], cur_lineup['P%d' % (j + 1)]]
    l_var.append(var)
    l_cost.append(salary)

l_stdev = [math.sqrt(x) for x in l_var]
lineups['salary'] = l_cost
lineups['variance'] = l_var
lineups['stdev'] = l_stdev

lineups.to_csv('./lineups/%s_%s_%s.csv' % (conf.site, fmt_date, conf.proj_iteration))
