"""Runs game simulations and write the results to files."""
from __future__ import division
from dateutil.parser import parse
from baseball_simulator.simulation_runner import run_simulated_games
import datetime as dt
import util.data_loader as dl
import conf
import csv
import pdb

schedule = dl.load_mlb_schedule()
proj_date = parse(conf.projection_date)
fmt_date = proj_date.strftime('%Y%m%d')
current_time = dt.datetime.now().strftime('%H:%M')
games = schedule.loc[fmt_date]

fd_proj_file = open(
    '%s/fanduel_%s_%s.csv' % (
        conf.projection_output_dir, proj_date.strftime('%Y_%m_%d'),
        current_time), 'w')
writer_fd = csv.DictWriter(fd_proj_file,
                           fieldnames=['name'] +
                           range(conf.simulated_game_count))
writer_fd.writeheader()
dk_proj_file = open(
    '%s/draftkings_%s_%s.csv' % (
        conf.projection_output_dir, proj_date.strftime('%Y_%m_%d'),
        current_time), 'w')
writer_dk = csv.DictWriter(dk_proj_file,
                           fieldnames=['name'] +
                           range(conf.simulated_game_count))
writer_dk.writeheader()
home_teams = games.at[fmt_date, 'home_team']
away_teams = games.at[fmt_date, 'away_team']
for idx, t in enumerate(home_teams):
    h_team = t
    a_team = away_teams[idx]
    results = run_simulated_games(a_team, h_team, conf.simulated_game_count)
    for name in results['batters_fd']:
        fd = dict(enumerate(results['batters_fd'][name]))
        fd['name'] = name
        dk = dict(enumerate(results['batters_dk'][name]))
        dk['name'] = name
        writer_fd.writerow(fd)
        writer_dk.writerow(dk)
    for name in results['pitchers_fd']:
        fd = dict(enumerate(results['pitchers_fd'][name]))
        fd['name'] = name
        dk = dict(enumerate(results['pitchers_dk'][name]))
        dk['name'] = name
        writer_fd.writerow(fd)
        writer_dk.writerow(dk)
