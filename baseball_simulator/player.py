"""Holds player class."""
import scrapers.baseball_ref_scraper as brs
import util.data_loader as dl
import util.util as u
import conf
import pdb


class Player(object):
    """Main Player class."""

    def __init__(self, name):
        """Initialization function."""
        self.game_logs = None
        self.name = u.standardize_player_name(name)
        self.bat_stats = {
            'SO': 0,
            'BB': 0,
            'HBP': 0,
            'H': 0,
            'R': 0,
            '1B': 0,
            '2B': 0,
            '3B': 0,
            'HR': 0,
            'RBI': 0,
            'SB': 0
        }
        self.game_history = []
        try:
            self.mlb_id = dl.get_player_mlb_id(self.name)
        except:
            self.mlb_id = None
            self.bat_handedness = 'R'
            return
        self.bat_handedness = self._load_batting_handedness()
        self.handedness_batting_stats = self._load_handedness_batting_stats()
        self.sb_stats = self._load_stolen_base_stats()
        # DEFAULT TO LEAGUE AVERAGE: FIX TO LOWER THRESHOLD
        if self.handedness_batting_stats is None:
            self.handedness_batting_stats = {}
            self.handedness_batting_stats['vR'] = conf.league_totals['PROBS']
            self.handedness_batting_stats['vL'] = conf.league_totals['PROBS']
            self.sb_stats = {}
            self.sb_stats['steal'] = 0
            self.sb_stats['success'] = 0
            self.sb_stats['cs'] = 0

    def get_handed_batting_probs(self, opp_handedness):
        """Return probabilities of batting outcomes."""
        if opp_handedness == 'R':
            return self.handedness_batting_stats['vR']
        else:
            return self.handedness_batting_stats['vL']

    def _load_batting_handedness(self):
        try:
            return conf.player_id_map[
                conf.player_id_map.mlb_id == self.mlb_id]['bats'][0]
        except:
            return 'R'

    def start_new_game(self):
        self.game_history.append(self.bat_stats)
        self.bat_stats = {
            'SO': 0,
            'BB': 0,
            'HBP': 0,
            'H': 0,
            'R': 0,
            '1B': 0,
            '2B': 0,
            '3B': 0,
            'HR': 0,
            'RBI': 0,
            'SB': 0
        }

    def _load_handedness_batting_stats(self):
        if conf.handedness_source == 'bbref':
            return brs.load_handed_probabilities(
                self.name, pit_or_bat='b')
        elif conf.handedness_source == 'steamer':
            try:
                ha = dl.load_steamer_handed_probabilities(
                    self.mlb_id, pit_or_bat='b')
            except:
                ha = brs.load_handed_probabilities(
                    self.name, pit_or_bat='b')
                if ha is None:
                    return conf.below_avg_batting_probs
            return ha

    def get_batting_handedness(self):
        """Return the handedness of the batter."""
        return self.bat_handedness

    def get_stolen_base_chance(self):
        return self.sb_stats

    def _load_stolen_base_stats(self):
        try:
            sb = dl.load_steamer_stolen_base_stats(self.mlb_id)
        except:
            return {'steal': 0, 'success': 0, 'cs': 0}
        return sb
    
    def get_name(self):
        """Return name of batter."""
        return self.name

    def get_bat_stats(self):
        """Return batting stats from simulated game."""
        return self.bat_stats

    def add_run(self):
        """Add a run from the simulated game."""
        self.bat_stats['R'] += 1

    def add_so(self):
        """Add a strikeout from the simulated game."""
        self.bat_stats['SO'] += 1

    def add_1b(self):
        """Add a single from the simultated game."""
        self.bat_stats['1B'] += 1
        self.bat_stats['H'] += 1

    def add_2b(self):
        """Add a double from the simulated game."""
        self.bat_stats['2B'] += 1
        self.bat_stats['H'] += 1

    def add_3b(self):
        """Add a triple from the simulated game."""
        self.bat_stats['3B'] += 1
        self.bat_stats['H'] += 1

    def add_hr(self):
        """Add a home run from the simulated game."""
        self.bat_stats['HR'] += 1
        self.bat_stats['H'] += 1

    def add_rbi(self):
        """Add an rbi from the simulated game."""
        self.bat_stats['RBI'] += 1

    def add_hbp(self):
        """Add a hit by pitch from the simulated game."""
        self.bat_stats['HBP'] += 1

    def add_bb(self):
        """Add a walk from the simulated game."""
        self.bat_stats['BB'] += 1

    def add_sb(self):
        """Add a walk from the simulated game."""
        self.bat_stats['SB'] += 1
