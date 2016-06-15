import scrapers.baseball_ref_scraper as brs

class Player(object):
	"""Main Player class."""

    def __init__(self, name):
        """Initialization function."""
        self.game_logs = None
        self.handedness_stats = None
        self.name = name
        self.stats = {
        	'SO': 0,
        	'BB': 0,
        	'HBP': 0,
        	'H': 0,
        	'R': 0,
        	'1B': 0,
        	'2B': 0,
        	'3B': 0,
        	'HR': 0,
        	'RBI': 0
        }

    def get_handedness_stats(self):
    	return self.handed

    def get_name(self):
    	return self.name

    def add_run(self):
    	self.stats['R'] += 1

    def add_so(self):
    	self.stats['SO'] += 1

    def add_1b(self):
    	self.stats['1B'] += 1
    	self.stats['H'] += 1
    
    def add_2b(self):
    	self.stats['2B'] += 1
    	self.stats['H'] += 1

    def add_3b(self):
    	self.stats['3B'] += 1
    	self.stats['H'] += 1

    def add_hr(self):
 	   	self.stats['HR'] += 1
 	   	self.stats['H'] += 1

    def add_rbi(self):
    	self.stats['RBI'] += 1

    def add_hbp(self):
    	self.stats['HBP'] += 1

    def add_bb(self):
    	self.stats['BB'] += 1
