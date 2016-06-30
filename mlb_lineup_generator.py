"""Generates lineups from pre-loaded projections."""
from scrapers.rotogrinder_scraper import\
    retrieve_mlb_player_salaries_and_positions, retrieve_mlb_batting_order
from dateutil.parser import parse
import datetime as dt
from util.util import is_number, print_top_df_lineups
from lineup_optimizers.proj_genetic_mlb import GeneticMLB
import pandas as pd
import numpy as np
import types
import conf
import pdb

sals_and_pos = retrieve_mlb_player_salaries_and_positions()
if conf.batting_orders is None:
    conf.batting_orders, conf.pitchers = retrieve_mlb_batting_order()

if conf.projection_date == 'today':
    proj_date = dt.datetime.now()
else:
    proj_date = parse(conf.projection_date)
fmt_date = proj_date.strftime('%Y_%m_%d')

# df = pd.read_csv('./projections/%s_%s.csv' % (
#     conf.site, '2016_06_23_00:08'),
#     index_col=0)
df = pd.read_csv('./projections/%s_%s_%d.csv' % (conf.site, fmt_date, conf.proj_iteration), index_col=0)
idx = df.index[:]
means = []
for p in idx:
    means.append([np.mean(df.loc[p][0:conf.simulated_game_count])])
mean_df = pd.DataFrame(means, index=idx, columns=['mean'])
df = df.join(mean_df)

pdb.set_trace()

# join our two data frames
projections_overall = df.join(sals_and_pos, how='left')

# drop players that weren't included
to_drop = []
for name in projections_overall.index:
    if not is_number(projections_overall.at[name, 'cost']):
        to_drop.append(name)
    # elif name in conf.excluded_batters or name in conf.excluded_pitchers:
    #     to_drop.append(name)
    elif conf.use_inclusion is False and projections_overall.at[name, 'team'] in conf.excluded_teams:
        to_drop.append(name)
    elif conf.use_inclusion is True and projections_overall.at[name, 'team'] not in conf.included_teams:
        to_drop.append(name)
projections_overall = projections_overall.drop(to_drop)
print projections_overall

# calculate lineups
gen = GeneticMLB(conf.mlb_max_salary)
lineups = gen.calculate(projections_overall)

print "\nAverage Lineup Fitness: %d" % np.mean([gen.fitness(l) for l in lineups])

print_top_df_lineups(lineups, gen)
