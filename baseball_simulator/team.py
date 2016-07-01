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

    def __init__(self, team_name, batting_order=None, pitcher=None):
        """Initialization function."""
        self.name = util.standardize_team_name(team_name)
        self.batting_order, pitcher_name = self._retrieve_projected_batting_order(
            team_name)
        # self.roster = self._load_team_roster(team_name)
        self.pitcher = Pitcher(pitcher_name)
        self.starting_pitcher = self.pitcher
        self.bullpen = brs.load_team_bullpen(team_name)
        for idx, player_name in enumerate(self.batting_order):
            self.batting_order[idx] = Player(util.standardize_player_name(str(player_name)))

    def _load_team_roster(self, team_name):
        """Load team's roster. NOT IN USE"""
        roster = brs.retrieve_team_roster(conf.bb_ref_teams[team_name])
        for p_name in roster:
            if roster[p_name] == 'Pitcher':
                roster[p_name] = Pitcher(util.standardize_player_name(
                    str(p_name)))
            else:
                roster[p_name] = Player(util.standardize_player_name(
                    str(p_name)))
        return roster

    def start_new_game(self):
        for player in self.batting_order:
            player.start_new_game()
        if self.pitcher == self.starting_pitcher:
            self.starting_pitcher.start_new_game()
        else:
            self.pitcher.start_new_game()
            self.starting_pitcher.start_new_game()
            self.pitcher = self.starting_pitcher

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

    def replace_pitcher(self, desired_role='Relief'):
        bp_dict = self.bullpen[['Role', 'IP']].to_dict()
        pot_pitchers = []
        for p in bp_dict['Role']:
            if bp_dict['Role'][p] == desired_role:
                pot_pitchers.append(p)
        ip_count = []
        for p in pot_pitchers:
            ip_count.append(int(bp_dict['IP'][p]))
        new_pit = pot_pitchers[ip_count.index(max(ip_count))]
        # pit is the name of the pitcher to be replaced
        new_pitcher = Pitcher(new_pit)
        if self.pitcher in self.batting_order:
            bat_idx = self.batting_order.index(self.pitcher)
            self.batting_order[bat_idx] = new_pitcher
        self.pitcher = new_pitcher

    def _retrieve_projected_batting_order(self, name):
        if conf.batting_orders is None:
            conf.batting_orders, conf.pitchers = retrieve_mlb_batting_order()
        team_batting_order = None
        try:
            b_o = conf.batting_orders[
                util.standardize_team_name(name)][:]
            if len(b_o) < 9:
                b_o.append(conf.pitchers[util.standardize_team_name(name)])
            return b_o, conf.pitchers[util.standardize_team_name(name)]
        except:
            team_batting_order = retrieve_most_recent_batting_order(name)
            team_pitching_rotation = brs.retrieve_pitching_rotation(
                name)
            if len(team_batting_order) < 9:
                team_batting_order.append(team_pitching_rotation[0])
            return team_batting_order, team_pitching_rotation[0]
