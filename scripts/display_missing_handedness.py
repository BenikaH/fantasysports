"""Write to a file the names we're missing from handedness."""
import csv
from util.data_loader import load_handedness_data
import scrapers.baseball_ref_scraper as brs
from baseball_simulator.team import Team
import conf
import pdb

print "Testing teams for missing handedness data"
hd = load_handedness_data()
fi = open('./data/missing_batters.csv', 'wb')
for team_name in conf.team_list:
    print "Checking %s" % team_name
    ros = brs.retrieve_team_roster(team_name)
    for player in ros.keys():
        pos = None
        if ros[player] == 'Pitcher':
            pos = 'P'
        else:
            pos = 'F'
        if player not in hd.index:
            fi.write('%s,%s,%s\n' % (player, pos, team_name))
