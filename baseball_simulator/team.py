"""Contains class definitions for teams."""
from scrapers.rotogrinder_scraper import retrieve_mlb_batting_order
from scrapers.baseball_ref_scraper import retrieve_most_recent_batting_order
from scrapers import baseball_ref_scraper as brs
from player import Player
import util.util as util
import conf


class Team(object):
    """Class definition for team object."""

    def __init__(self, team_name):
        """Initialization function."""
        self.players = self._retrieve_players(team_name)
        self.batting_order = self._retrieve_projected_batting_order(team_name)
        for idx, player_name in enumerate(self.batting_order):
            self.batting_order[idx] = Player(player_name)

    def get_player(self, batting_pos):
        return self.batting_order[batting_pos]

    def get_named_batters(self):
        arr = []
        for player in self.batting_order:
            arr.append(player.get_name())
        return arr

    def _retrieve_players(self, name):
        player_name_list = brs.get_player_list(name)
        players = {}
        for name in player_name_list:
            players[name] = Player(name)
        return []

    def _retrieve_projected_batting_order(self, name):
        batting_orders = retrieve_mlb_batting_order()
        team_batting_order = None
        try:
            team_batting_order = batting_orders[util.standardize_team_name(name)]
        except:
            team_batting_order = retrieve_most_recent_batting_order(name)
        return team_batting_order
