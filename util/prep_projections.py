"""Generates lineups from pre-loaded projections."""
from scrapers.rotogrinder_scraper import\
    retrieve_mlb_player_salaries_and_positions, retrieve_mlb_batting_order
from scrapers.general_scraper import\
    load_prev_mlb_salaries_and_points, retrieve_previous_mlb_batting_order
from dateutil.parser import parse
import datetime as dt
from util import is_number, print_top_df_lineups
import pandas as pd
import numpy as np
import conf
import pdb


def create_simplified_projections():
    for s in ['fanduel', 'draftkings']:
        conf.site = s
        conf.rotogrinder_hitter_path =\
            'http://rotogrinders.com/projected-stats/mlb-hitter.csv?site=%s' % conf.site
        conf.rotogrinder_pitcher_path =\
            'http://rotogrinders.com/projected-stats/mlb-pitcher.csv?site=%s' % conf.site

        sals_and_pos = retrieve_mlb_player_salaries_and_positions()
        if conf.batting_orders is None:
            conf.batting_orders, conf.pitchers = retrieve_mlb_batting_order()

        df = pd.read_csv('./projections/%s_%s_%s.csv' % (conf.site, conf.proj_date, conf.proj_iteration), index_col=0)

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
            elif name in conf.excluded_batters or name in\
                    conf.excluded_pitchers:
                to_drop.append(name)
            elif conf.use_inclusion is False and projections_overall.at[name, 'team'] in conf.excluded_teams:
                to_drop.append(name)
            elif conf.use_inclusion is True and projections_overall.at[name, 'team'] not in conf.included_teams:
                to_drop.append(name)
        projections_overall = projections_overall.drop(to_drop)
        projections_overall['exclude'] = 0
        projections_overall[['pos', 'mean', 'cost', 'team', 'exclude']].to_csv('./simplified_projections/%s_%s_%s.csv' % (conf.site, conf.proj_date, conf.proj_iteration))
