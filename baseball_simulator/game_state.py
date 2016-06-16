

class GameState(object):
    """Class to manage entire state of the game."""

    def __init__(self, inning=1):
        """Initialize game state."""
        self.inning = inning
        self.sp_thrown_pitches = 0
        self.inn_stage = 'top'
        self.outs = 0
        self.score = [0, 0]
        self.batting_pos = [0, 0]
        self.bases = [0, 0, 0]
        self.game_log = []

    def game_on(self):
        """Return whether the game is ongoing."""
        if self.inning < 10 or (self.score[0] == self.score[1]) or\
                (self.score[0] > self.score[1] and self.inn_stage == 'bot'):
            return True
        else:
            return False

    def get_game_stats(self):
        return self.game_log

    def update_game(self, outcome, batter, pitcher):
        """Check and update according to batting outcome."""
        # OUT
        if outcome == 'OUT':
            self.outs += 1
            self.sp_thrown_pitches += 3.83
            self.game_log.append(
                "%s.%d: Batter %s hits into an out." % (
                    self.inn_stage, self.inning, batter.get_name()))
        # STRIKE OUT
        elif outcome == 'SO':
            self.outs += 1
            self.game_log.append(
                "%s.%d: Batter %s strikes out against %s." % (
                    self.inn_stage, self.inning, batter.get_name(),
                    pitcher.get_name()))
            batter.add_so()
            self.sp_thrown_pitches += 5
        # WALK OR HBP
        elif outcome == 'BB' or outcome == 'HBP':
            if outcome == 'BB':
                self.game_log.append("Batter %s walks." % batter.get_name())
                batter.add_bb()
            elif outcome == 'HBP':
                self.game_log.append("Batter %s is hit by pitcher." % batter.get_name())
                batter.add_hbp()
            # if noone on first
            if self.bases[0] == 0:
                self.bases[0] == batter
            # if bases loaded
            elif self.bases_loaded():
                self.add_run(self.bases[2])
                self.game_log.append("%s.%d: %s scores." % (
                    self.inn_stage, self.inning,
                    self.bases[2].get_name()))
                self.bases[2] = self.bases[1]
                self.bases[1] = self.bases[0]
            else:
                if self.bases[1] == 0:
                    # second is open
                    self.bases[0] = self.bases[1]
                else:
                    # third is open
                    self.bases[2] = self.bases[1]
                    self.bases[1] = self.bases[0]
                # move guy on first forward, etc, etc
            self.bases[0] = batter
        # SINGLE
        elif outcome == '1B':
            self.game_log.append("%s.%d:Batter %s singles." % (
                self.inn_stage, self.inning, batter.get_name()))
            batter.add_1b()
            # advance runners
            # everyone moves forward 1 (may adapt later)
            if self.bases[2] != 0:
                self.add_run(self.bases[2])
                batter.add_rbi()
                self.bases[2] = 0
            if self.bases[1] != 0:
                self.bases[2] = self.bases[1]
                self.bases[1] = 0
            if self.bases[0] != 0:
                self.bases[1] = self.bases[0]
                self.bases[0] = 0
            self.bases[0] = batter
        # DOUBLE
        elif outcome == '2B':
            if self.bases[2] != 0:
                self.add_run(self.bases[2])
                batter.add_rbi()
                self.bases[2] = 0
            if self.bases[1] != 0:
                self.add_run(self.bases[1])
                batter.add_rbi()
                self.bases[1] = 0
            if self.bases[0] != 0:
                self.bases[2] = self.bases[0]
                self.bases[0] = 0
            self.bases[1] = batter
        # TRIPLE
        elif outcome == '3B':
            if self.bases[2] != 0:
                self.add_run(self.bases[2])
                batter.add_rbi()
                self.bases[2] = 0
            if self.bases[1] != 0:
                self.add_run(self.bases[1])
                batter.add_rbi()
                self.bases[1] = 0
            if self.bases[0] != 0:
                self.add_run(self.bases[0])
                batter.add_rbi()
                self.bases[0] = 0
            self.bases[2] = batter
        # HOME RUN
        elif outcome == 'HR':
            if self.bases[2] != 0:
                self.add_run(self.bases[2])
                batter.add_rbi()
                self.bases[2] = 0
            if self.bases[1] != 0:
                self.add_run(self.bases[1])
                batter.add_rbi()
                self.bases[1] = 0
            if self.bases[0] != 0:
                self.add_run(self.bases[0])
                batter.add_rbi()
                self.bases[0] = 0
            # update batter stats
            batter.add_hr()
            batter.add_rbi()
            self.add_run(batter)
        # check inning and update
        if self.outs == 3:
            self.start_new_inning()

    def bases_loaded(self):
        if 0 not in self.bases:
            return True
        else:
            return False

    def runners_on_base(self):
        for b in self.bases:
            if b != 0:
                return True
        return False

    def start_new_inning(self):
        self.outs = 0
        if self.inn_stage == 'top':
            self.inn_stage = 'bot'
        else:
            self.inn_stage = 'top'
            self.inning += 1

    def get_outs(self):
        return self.outs

    def add_out(self):
        self.outs += 1

    def add_run(self, scoring_runner):
        if self.inn_stage == 'top':
            self.score[0] += 1
        else:
            self.score[1] += 1
        self.game_log.append("%s.%d:%s scores." % (
            self.inn_stage, self.inning,
            scoring_runner.get_name()))
        scoring_runner.add_run()

    def get_stage(self):
        return self.inn_stage

    def update_inning(self):
        if self.inn_stage == 'bot':
            self.inn_stage = 'top'
            self.inning += 1
        else:
            self.inn_stage == 'top'
        self.bases = [0, 0, 0]

    def get_batting_pos(self):
        if self.inn_stage == 'top':
            self.batting_pos[0]
        else:
            self.batting_pos[1]

    def update_batters(self):
        if self.inn_stage == 'top':
            if self.batting_pos[0] == 8:
                self.batting_pos[0] = 0
            else:
                self.batting_pos[0] += 1
        else:
            if self.batting_pos[1] == 8:
                self.batting_pos[1] = 0
            else:
                self.batting_pos[1] += 1
