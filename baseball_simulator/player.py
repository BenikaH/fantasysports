"""Holds player class."""
import scrapers.baseball_ref_scraper as brs
import util.data_loader as dl
import conf
import pdb


class Player(object):
    """Main Player class."""

    def __init__(self, name):
        """Initialization function."""
        self.game_logs = None
        self.name = name
        self.handedness = None
        if name == 'generic':
            self.handedness = 'RIGHT'
            self.handedness_batting_stats = {}
            self.handedness_batting_stats['RHP'] = conf.league_totals['PROBS']
            self.handedness_batting_stats['LHP'] = conf.league_totals['PROBS']
            return
        self.handedness_batting_stats = self._load_handedness_batting_stats()
        # DEFAULT TO LEAGUE AVERAGE: FIX TO LOWER THRESHOLD
        if self.handedness_batting_stats is None:
            self.handedness_batting_stats = {}
            self.handedness_batting_stats['RHP'] = conf.league_totals['PROBS']
            self.handedness_batting_stats['LHP'] = conf.league_totals['PROBS']
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

    def get_handed_batting_probs(self, opp_handedness):
        """Return probabilities of batting outcomes."""
        if opp_handedness == 'RIGHT':
            return self.handedness_batting_stats['RHP']
        else:
            return self.handedness_batting_stats['LHP']

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
        return brs.load_handed_probabilities(self.name, '2015', '2016', pit_or_bat='b')

    def get_batting_handedness(self):
        """Return the handedness of the batter."""
        if conf.batter_handedness is None:
            conf.batter_handedness = dl.load_handedness_data('b')
        handedness = conf.batter_handedness.at[self.name, 'Bats']
        return handedness

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
