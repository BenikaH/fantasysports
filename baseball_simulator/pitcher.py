"""Contains pitcher class."""
import scrapers.baseball_ref_scraper as brs
from player import Player
import util.data_loader as dl
import conf


class Pitcher(Player):
    """Main pitcher class."""

    def __init__(self, name):
        """Initialization function."""
        super(Pitcher, self).__init__(name)
        self.handedness_pitching_stats = self._load_handedness_pitching_stats()
        self.pitch_stats = {
            'SO': 0,
            'BB': 0,
            'HBP': 0,
            'HA': 0,
            'ER': 0
        }

    def get_handed_pitching_probs(self, opp_handedness):
        if opp_handedness == 'RIGHT':
            return self.handedness_pitching_stats['RHB']
        else:
            return self.handedness_pitching_stats['LHB']

    def _load_handedness_pitching_stats(self):
        return brs.load_handed_probabilities(
            self.name, pit_or_bat='p')

    def get_pitching_handedness(self):
        if conf.pitcher_handedness is None:
            conf.pitcher_handedness = dl.load_handedness_data('p')
        handedness = conf.pitcher_handedness.at[self.name, 'Throws']
        return handedness

    def add_pitch_so(self):
        self.pitch_stats['SO'] += 1

    def add_pitch_ha(self):
        self.pitch_stats['HA'] += 1

    def add_pitch_hbp(self):
        self.pitch_stats['HBP'] += 1

    def add_pitch_bb(self):
        self.pitch_stats['BB'] += 1
