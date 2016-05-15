from util.cache import cache_disk
from bs4 import BeautifulSoup
import urllib3
import conf
from string import ascii_lowercase
import pdb


@cache_disk()
def retrieve_player_link_map():
    http = urllib3.PoolManager()
    player_link_map = {}
    for char in ascii_lowercase:
        r = http.urlopen('GET', 'http://www.baseball-reference.com/players/%s/' % char, preload_content=False)
        soup = BeautifulSoup(r.data, 'html5lib')
        for block in soup.find_all('blockquote'):
            bolds = block.find_all('b')
            if len(bolds) > 0:
                for b in bolds:
                    link = b.a
                    player_link_map[link.get_text()] = link.get('href')
    return player_link_map

