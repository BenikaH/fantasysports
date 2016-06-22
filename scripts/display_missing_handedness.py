"""Write to a file the names we're missing from handedness."""
import csv
from util.data_loader import load_handedness_data
import scrapers.baseball_ref_scraper as brs
from baseball_simulator.team import Team
import conf
import pdb

print "Testing teams for missing handedness data"
hdb = load_handedness_data('b')
hdp = load_handedness_data('p')
fib = open('./data/missing_batters.csv', 'wb')
fip = open('./data/missing_pitchers.csv', 'wb')
for team_name in conf.team_list:
    print "Checking %s" % team_name
    ros = brs.retrieve_team_roster(team_name)
    for player in ros.keys():
        pos = None
        if ros[player] == 'Pitcher':
            pos = 'P'
        else:
            pos = 'F'
        if player not in hdb.index or (player not in hdp.index and pos == 'P'):
            bats, throws = brs.get_player_handedness(player)
            if player not in hdb.index:
                fib.write('%s,%s,%s,%s\n' % (player, pos, team_name, bats))
            if player not in hdp.index and pos == 'P':
                fip.write('%s,%s,%s\n' % (player, team_name, throws))
