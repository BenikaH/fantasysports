"""Contains class definitions for teams."""
from scrapers.rotogrinder_scraper import retrieve_mlb_batting_order
from scrapers.baseball_ref_scraper import retrieve_most_recent_batting_order
from scrapers import baseball_ref_scraper as brs
from player import Player
from pitcher import Pitcher
import util.util as util
import conf


class Team(object):
    """Class definition for team object."""

    def __init__(self, team_name):
        """Initialization function."""
        # self.players = self._retrieve_players(team_name)
        self.batting_order, pit_rot = self._retrieve_projected_batting_order(
            team_name)
        self.roster = self._load_team_roster(team_name)
        self.pitcher = self.roster[pit_rot[0]]
        self.bullpen = brs.load_team_bullpen(team_name)
        for idx, player_name in enumerate(self.batting_order):
            if player_name in self.roster:
                self.batting_order[idx] = self.roster[player_name]
            else:
                self.batting_order[idx] = Player(player_name)
                # self.batting_order[idx] = Player('generic')

    def _load_team_roster(self, team_name):
        """Load team's roster."""
        roster = brs.retrieve_team_roster(team_name)
        for p_name in roster:
            if roster[p_name] == 'Pitcher':
                roster[p_name] = Pitcher(p_name)
            else:
                roster[p_name] = Player(p_name)
        return roster

    def get_pitcher(self):
        return self.pitcher

    def get_player(self, batting_pos):
        return self.batting_order[batting_pos]

    def get_named_batters(self):
        arr = []
        for player in self.batting_order:
            arr.append(player.get_name())
        return arr

    # def _retrieve_players(self, name):
    #     player_name_list = brs.get_player_list(name)
    #     players = {}
    #     for name in player_name_list:
    #         players[name] = Player(name)
    #     return []

    def _retrieve_projected_batting_order(self, name):
        batting_orders = retrieve_mlb_batting_order()
        team_batting_order = None
        team_pitching_rotation = brs.retrieve_pitching_rotation(name)
        try:
            team_batting_order = batting_orders[
                util.standardize_team_name(name)]
        except:
            team_batting_order = retrieve_most_recent_batting_order(name)
            if len(team_batting_order) < 9:
                team_batting_order.append(team_pitching_rotation[0])
        return team_batting_order, team_pitching_rotation
