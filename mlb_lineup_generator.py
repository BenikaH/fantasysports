"""Generates lineups from pre-loaded projections."""
from scrapers.rotogrinder_scraper import\
    retrieve_mlb_player_salaries_and_positions, retrieve_mlb_batting_order
from dateutil.parser import parse
import datetime as dt
from util.util import is_number, print_top_df_lineups
from lineup_optimizers.proj_genetic_mlb import GeneticMLB
from scrapers.sabersim_scraper import\
    get_saber_sim_projections_from_fangraphs
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


df = pd.read_csv('./projections/%s_%s_%s.csv' % (conf.site, fmt_date, conf.proj_iteration), index_col=0)

idx = df.index[:]
means = []
for p in idx:
    means.append([np.mean(df.loc[p][0:conf.simulated_game_count])])
mean_df = pd.DataFrame(means, index=idx, columns=['mean'])
df = df.join(mean_df)

# join our two data frames
projections_overall = df.join(sals_and_pos, how='left')

# drop players that weren't included
to_drop = []
for name in projections_overall.index:
    if type(projections_overall.at[name, 'cost']) == np.ndarray:
        print name
        print projections_overall.loc[name]
        pdb.set_trace()
    if not is_number(projections_overall.at[name, 'cost']):
        to_drop.append(name)
    elif name in conf.excluded_batters or name in conf.excluded_pitchers:
        to_drop.append(name)
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

try:
    print_top_df_lineups(lineups, gen, 10)
except:
    pdb.set_trace()

print "\nCreating Secondary Lineups with Sabersim Data"
# Sabersim
batter_df_sabersim, pitcher_df_sabersim =\
    get_saber_sim_projections_from_fangraphs()

to_drop = []
for name in projections_overall.index:
    if name in batter_df_sabersim.index:
        if conf.site == 'fanduel':
            projections_overall.set_value(name, 'mean', np.mean(
                [float(projections_overall.at[name, 'mean']), float(batter_df_sabersim.at[
                 name, 'ss_fd_pred'])]))
        elif conf.site == 'draftkings':
            projections_overall.set_value(name, 'mean', np.mean(
                [float(projections_overall.at[name, 'mean']), float(batter_df_sabersim.at[
                 name, 'ss_dk_pred'])]))
    elif name in pitcher_df_sabersim.index:
        if conf.site == 'fanduel':
            projections_overall.set_value(name, 'mean', np.mean(
                [float(projections_overall.at[name, 'mean']),
                 float(pitcher_df_sabersim.at[name, 'ss_fd_pred'])]))
        elif conf.site == 'draftkings':
            projections_overall.set_value(name, 'mean', np.mean(
                [float(projections_overall.at[name, 'mean']),
                 float(pitcher_df_sabersim.at[name, 'ss_dk_pred'])]))
    else:
        to_drop.append(name)
projections_overall = projections_overall.drop(to_drop)

lineups2 = gen.calculate(projections_overall)
# print "\nAverage Lineup Fitness: %d" % np.mean([gen.fitness(l) for l in lineups2])

print_top_df_lineups(lineups2, gen, 15)

