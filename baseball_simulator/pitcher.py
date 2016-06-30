"""Contains pitcher class."""
from __future__ import division
import scrapers.baseball_ref_scraper as brs
from player import Player
import util.data_loader as dl
import conf
import pdb


class Pitcher(Player):
    """Main pitcher class."""

    def __init__(self, name):
        """Initialization function."""
        super(Pitcher, self).__init__(name)
        self.handedness_pitching_stats = self._load_handedness_pitching_stats()
        if self.handedness_pitching_stats:
            self.handedness_pitching_stats = {}
            self.handedness_pitching_stats['RHB'] = conf.league_totals['PROBS']
            self.handedness_pitching_stats['LHB'] = conf.league_totals['PROBS']
        self._initialize_pitch_stats()

    def get_pitch_stats(self):
        return self.pitch_stats

    def get_handed_pitching_probs(self, opp_handedness):
        if opp_handedness == 'RIGHT':
            return self.handedness_pitching_stats['RHB']
        else:
            return self.handedness_pitching_stats['LHB']

    def start_new_game(self):
        super(Pitcher, self).start_new_game()
        self._initialize_pitch_stats()

    def _initialize_pitch_stats(self):
        self.pitch_stats = {
            'SO': 0,
            'BB': 0,
            'HBP': 0,
            'HA': 0,
            'ER': 0,
            'IP': 0,
            'PA': 0
        }

    def _load_handedness_pitching_stats(self):
        if conf.handedness_source == 'bbref':
            return brs.load_handed_probabilities(
                self.name, pit_or_bat='p')
        elif conf.handedness_source == 'steamers':
            return dl.load_steamer_handed_probabilities(
                self.name, pit_or_bat='p')

    def get_pitcher_sub_feats(self, gs, score_diff):
        return [
            [
                self.pitch_stats['SO'],
                self.pitch_stats['BB'],
                self.pitch_stats['HBP'],
                self.pitch_stats['PA'],
                self.pitch_stats['HA'],
                # gs.get_inning() - 1 + (gs.get_outs() * (1.0 / 3.0)),
                self.pitch_stats['IP'],
                self.pitch_stats['ER'],
                score_diff
            ]
        ]

    def get_pitching_handedness(self):
        """Return the handedness of the pitcher."""
        if conf.pitcher_handedness is None:
            conf.pitcher_handedness = dl.load_handedness_data('p')
        try:
            handedness = conf.pitcher_handedness.at[str(self.name), 'Throws']
        except:
            raise ValueError('Pitcher %s handedness not included in doc.' %
                             self.name)
        return handedness

    def add_batter_faced(self):
        self.pitch_stats['PA'] += 1

    def add_pitch_so(self):
        self.pitch_stats['SO'] += 1
        self.add_partial_ip()

    def add_pitch_ha(self):
        self.pitch_stats['HA'] += 1

    def add_pitch_hbp(self):
        self.pitch_stats['HBP'] += 1

    def add_pitch_bb(self):
        self.pitch_stats['BB'] += 1

    def add_pitch_er(self):
        self.pitch_stats['ER'] += 1

    def add_partial_ip(self):
        self.pitch_stats['IP'] += 1.0 / 3.0
