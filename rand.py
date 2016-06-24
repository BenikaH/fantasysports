
import scrapers.baseball_ref_scraper as brs
brs.load_handed_probabilities('Julio Urias')

from baseball_simulator.simulation_runner import play_game
from baseball_simulator.team import Team
play_game(Team('LAA'), Team('NYM'))

from baseball_simulator.simulation_runner import run_simulated_games
run_simulated_games('SFG', 'PIT')

# cache id: 762225ac9efd5a98af338ede8cd583e0
