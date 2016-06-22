"""Contains class definitions for teams."""
from scrapers.rotogrinder_scraper import retrieve_mlb_batting_order
from scrapers.baseball_ref_scraper import retrieve_most_recent_batting_order
from scrapers import baseball_ref_scraper as brs
from player import Player
from pitcher import Pitcher
import util.util as util
import pdb
import conf


class Team(object):
    """Class definition for team object."""

    def __init__(self, team_name):
        """Initialization function."""
        self.name = util.standardize_team_name(team_name)
        self.batting_order, pitcher_name = self._retrieve_projected_batting_order(
            team_name)
        self.roster = self._load_team_roster(team_name)
        if pitcher_name in self.roster:
            self.pitcher = self.roster[pitcher_name]
            self.starting_pitcher = self.pitcher
        else:
            self.pitcher = Pitcher(pitcher_name)
            self.roster[pitcher_name] = self.pitcher
            self.starting_pitcher = self.pitcher
        self.bullpen = brs.load_team_bullpen(team_name)
        for idx, player_name in enumerate(self.batting_order):
            if player_name in self.roster:
                self.batting_order[idx] = self.roster[player_name]
            else:
                pl = Player(str(player_name))
                self.batting_order[idx] = pl
                # add them to the roster
                self.roster[player_name] = pl

    def _load_team_roster(self, team_name):
        """Load team's roster."""
        roster = brs.retrieve_team_roster(conf.bb_ref_teams[team_name])
        for p_name in roster:
            if roster[p_name] == 'Pitcher':
                roster[p_name] = Pitcher(str(p_name))
            else:
                roster[p_name] = Player(str(p_name))
        return roster

    def start_new_game(self):
        for player in self.roster:
            self.roster[player].start_new_game()

    def get_starting_pitcher(self):
        return self.starting_pitcher

    def get_name(self):
        return self.name

    def get_pitcher(self):
        return self.pitcher

    def get_player(self, batting_pos):
        return self.batting_order[batting_pos]

    def get_batting_order(self):
        return self.batting_order

    def get_named_batters(self):
        arr = []
        for player in self.batting_order:
            arr.append(player.get_name())
        return arr

    def _retrieve_projected_batting_order(self, name):
        if conf.batting_orders is None:
            conf.batting_orders, conf.pitchers = retrieve_mlb_batting_order()
        team_batting_order = None
        try:
            conf.batting_orders[
                util.standardize_team_name(name)]
            return\
                conf.batting_orders[
                    util.standardize_team_name(name)][:],\
                conf.pitchers[
                    util.standardize_team_name(name)]
        except:
            team_batting_order = retrieve_most_recent_batting_order(name)
            team_pitching_rotation = brs.retrieve_pitching_rotation(
                name)
            if len(team_batting_order) < 9:
                team_batting_order.append(team_pitching_rotation[0])
            return team_batting_order, team_pitching_rotation[0]
