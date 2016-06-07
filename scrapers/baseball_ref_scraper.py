from util.cache import cache_disk
from bs4 import BeautifulSoup
import urllib3
import conf
from string import ascii_lowercase
import pdb

####################
# PLAYER FUNCTIONS #
####################

@cache_disk()
def retrieve_player_link_map():
    """Retrieve and cache the links to each player's page."""
    http = urllib3.PoolManager()
    player_link_map = {}
    for char in ascii_lowercase:
        r = http.urlopen(
            'GET', 'http://www.baseball-reference.com/players/%s/' % char,
            preload_content=False)
        soup = BeautifulSoup(r.data, 'html5lib')
        for block in soup.find_all('blockquote'):
            bolds = block.find_all('b')
            if len(bolds) > 0:
                for b in bolds:
                    link = b.a
                    player_link_map[link.get_text()] = link.get('href')
    return player_link_map

# ALL TODO FROM HERE ON

def get_player_statistics(player_name):
    if conf.player_link_map != None:
        conf.player_link_map = retrieve_player_link_map()
    http = urllib3.PoolManager()
    if player_name in conf.player_link_map:
        r = http.urlopen(
                'GET', 'http://www.baseball-reference.com%s' % conf.player_link_map[player_name],
                preload_content=False)
        soup = BeautifulSoup(r.data, 'html5lib')
        pdb.set_trace()
    else:
        except ValueError("Player %s not found." % player_name)
    return {}

##################
# TEAM FUNCTIONS #
##################
@cache_disk()
def retrieve_team_link_map():
    # TODO
    http = urllib3.PoolManager()
    team_link_map = {}
    for char in ascii_lowercase:
        r = http.urlopen
            'GET', 'http://www.baseball-reference.com/teams/%s/' % char,
            preload_content=False)
        soup = BeautifulSoup(r.data, 'html5lib')
        for block in soup.find_all('blockquote'):
            bolds = block.find_all('b')
            if len(bolds) > 0:
                for b in bolds:
                    link = b.a
                    team_link_map[link.get_text()] = link.get('href')

def retrieve_most_recent_batting_order(team_name):
    """Return the most recent batting order of a particular team."""
    return []

def get_player_list(team_name):
    return []
