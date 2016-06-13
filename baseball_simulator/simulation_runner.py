"""Contains runner functions for basic baseball simulation."""


def run_simulation(away_team, home_team):
    """Runs a simulation between two teams."""
    player_stats = {}
    game_stats = {}
    gs = GameState()
    # play the game
    while gs.game_on():
        # play inning
        while gs.get_outs() < 3:
            if gs.get_stage() == 'top':
                play_batter(gs, away_team.get_player(gs.get_batting_pos()),
                            home_team.get_pitcher())
            else:
                play_batter(gs, home_team.get_player(gs.get_batting_pos()),
                            away_team.get_pitcher())

    return player_stats, game_stats


def play_batter(state, batter, pitcher):
    
    return 'HIT'


class GameState(object):

    def __init__(self):
        self.inning = 1
        self.inn_stage = 'top'
        self.outs = 0
        self.score = [0, 0]
        self.batting_pos = [0, 0]
        self.bases = [0, 0, 0]

    def game_on(self):
        if self.innings < 10 or (self.score[0] == self.score[1]) or\
                (self.score[0] > self.score[1] and self.inn_stage == 'bot'):
            return True
        else:
            return False

    def get_outs(self):
        return self.outs

    def add_out(self):
        self.outs += 1

    def get_stage(self):
        return self.inn_stage

    def update_inning(self):
        if self.inn_stage == 'bot':
            self.inn_stage = 'top'
            self.inning += 1
        else:
            self.inn_stage == 'top'

    def get_batting_pos(self):
        if self.inn_stage == 'top'
            self.batting_pos[0]
        else:
            self.batting_pos[1]

    def update_batters(self):
        if self.inn_stage == 'top'
            if self.batting_pos[0] == 8:
                self.batting_pos[0] = 0
            else:
                self.batting_pos[0] += 1
        else:
            if self.batting_pos[1] == 8:
                self.batting_pos[1] = 0
            else:
                self.batting_pos[1] += 1
