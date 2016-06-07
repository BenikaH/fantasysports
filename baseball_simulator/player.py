import scrapers.baseball_ref_scraper as brs

class Player(object):
	"""Main Player class."""

    def __init__(self, name):
        """Initialization function."""
        self.stats = brs.get_player_statistics(name)
        self.name = name

    def get_stats(self):
    	return self.stats