import util.score_calculators as sc
import pandas as pd
import util.data_loader as dl
import math
import conf
import pdb


class GameState(object):
    """Class to manage entire state of the game."""

    def __init__(self, away_team, home_team, inning=1):
        """Initialize game state."""
        if conf.field_factors is None:
            conf.field_factors = dl.load_field_factors()
        self.field_adjustments = conf.field_factors
        self.inning = inning
        self.inn_stage = 'top'
        self.outs = 0
        self.score = [0, 0]
        self.batting_pos = [0, 0]
        self.bases = [0, 0, 0]
        self.game_log = []
        self.winning_pitcher = None
        self.home_team = home_team
        self.away_team = away_team

    def game_on(self):
        """Return whether the game is ongoing."""
        if self.inning < 10 or (self.score[0] == self.score[1]) or\
                (self.score[0] > self.score[1] and self.inn_stage == 'bot'):
            return True
        else:
            return False

    def get_game_stats(self):
        away_pit_name, away_pit = self._get_pitcher_stats(self.away_team.get_starting_pitcher())
        home_pit_name, home_pit = self._get_pitcher_stats(self.home_team.get_starting_pitcher())
        pitcher_stats = pd.DataFrame(
            [[self.away_team.get_name()] + away_pit, [self.home_team.get_name()] + home_pit],
            columns=['Team', 'SO', 'BB', 'HA', 'ER', 'HBP', 'FDP', 'DKP'],
            index=[away_pit_name, home_pit_name]
        )
        # for subbed out players, may need to use diff arg than batting order
        away_names, away_batter_stats = self._output_team_batting_stats(
            self.away_team.get_batting_order())
        home_names, home_batter_stats = self._output_team_batting_stats(
            self.home_team.get_batting_order())
        away_batter_stats = [[self.away_team.get_name()] + el for el in away_batter_stats]
        home_batter_stats = [[self.home_team.get_name()] + el for el in home_batter_stats]
        batter_stats = pd.DataFrame(
            away_batter_stats + home_batter_stats,
            columns=['Team', 'H', '1B', '2B', '3B', 'HR', 'R', 'RBI',
                     'BB', 'HBP', 'SO', 'FDP', 'DKP'],
            index=away_names + home_names
        )
        return self.game_log, self.score, pitcher_stats, batter_stats

    def _output_team_batting_stats(self, team_player_list):
        stats = []
        names = []
        for batter in team_player_list:
            stats.append(self._get_batter_stats(batter))
            names.append(batter.get_name())
        return names, stats

    def _get_pitcher_stats(self, pitcher):
        pit_stats = pitcher.get_pitch_stats()
        win = None
        if self.winning_pitcher == pitcher.get_name():
            win = 1
        else:
            win = 0
        return\
            pitcher.get_name(),\
            [
                pit_stats['SO'],
                pit_stats['BB'],
                pit_stats['HA'],
                pit_stats['ER'],
                pit_stats['HBP'],
                sc.calculate_fanduel_pitcher_score(
                    pit_stats['ER'],
                    pit_stats['IP'],
                    pit_stats['SO'],
                    win),
                sc.calculate_draftkings_pitcher_score(
                    pit_stats['ER'],
                    pit_stats['IP'],
                    pit_stats['SO'],
                    win,
                    pit_stats['BB'],
                    pit_stats['HBP'])
            ]

    def _get_batter_stats(self, batter):
        bat_stats = batter.get_bat_stats()
        return [
            bat_stats['H'],
            bat_stats['1B'],
            bat_stats['2B'],
            bat_stats['3B'],
            bat_stats['HR'],
            bat_stats['R'],
            bat_stats['RBI'],
            bat_stats['BB'],
            bat_stats['HBP'],
            bat_stats['SO'],
            sc.calculate_fanduel_hitter_score(
                bat_stats['1B'],
                bat_stats['2B'],
                bat_stats['3B'],
                bat_stats['BB'],
                bat_stats['HBP'],
                bat_stats['HR'],
                bat_stats['R'],
                bat_stats['RBI'],
                bat_stats['SB']
            ),
            sc.calculate_draftkings_hitter_score(
                bat_stats['1B'],
                bat_stats['2B'],
                bat_stats['3B'],
                bat_stats['BB'],
                bat_stats['HBP'],
                bat_stats['HR'],
                bat_stats['R'],
                bat_stats['RBI'],
                bat_stats['SB']
            )
        ]

    def update_game(self, outcome, batter, pitcher):
        """Check and update according to batting outcome."""
        # OUT
        if outcome == 'OUT':
            self.outs += 1
            self.game_log.append(
                "%s.%d: %s hits into an out." % (
                    self.inn_stage, self.inning, batter.get_name()))
            pitcher.add_partial_ip()
        # STRIKE OUT
        elif outcome == 'SO':
            self.outs += 1
            self.game_log.append(
                "%s.%d: %s strikes out against %s." % (
                    self.inn_stage, self.inning, batter.get_name(),
                    pitcher.get_name()))
            pitcher.add_pitch_so()
            batter.add_so()
        # WALK OR HBP
        elif outcome == 'BB' or outcome == 'HBP':
            if outcome == 'BB':
                self.game_log.append("%s walks." % batter.get_name())
                pitcher.add_pitch_bb()
                batter.add_bb()
            elif outcome == 'HBP':
                self.game_log.append("%s is hit by pitcher." % batter.get_name())
                pitcher.add_pitch_hbp()
                batter.add_hbp()
            # if noone on first
            if self.bases[0] == 0:
                self.bases[0] == batter
            # if bases loaded
            elif self.bases_loaded():
                self.add_run(self.bases[2], pitcher)
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
            pitcher.add_pitch_ha()
            self.game_log.append("%s.%d: %s singles." % (
                self.inn_stage, self.inning, batter.get_name()))
            batter.add_1b()
            # advance runners
            # everyone moves forward 1 (may adapt later)
            if self.bases[2] != 0:
                self.add_run(self.bases[2], pitcher)
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
            pitcher.add_pitch_ha()
            if self.bases[2] != 0:
                self.add_run(self.bases[2], pitcher)
                batter.add_rbi()
                self.bases[2] = 0
            if self.bases[1] != 0:
                self.add_run(self.bases[1], pitcher)
                batter.add_rbi()
                self.bases[1] = 0
            if self.bases[0] != 0:
                self.bases[2] = self.bases[0]
                self.bases[0] = 0
            self.bases[1] = batter
        # TRIPLE
        elif outcome == '3B':
            pitcher.add_pitch_ha()
            if self.bases[2] != 0:
                self.add_run(self.bases[2], pitcher)
                batter.add_rbi()
                self.bases[2] = 0
            if self.bases[1] != 0:
                self.add_run(self.bases[1], pitcher)
                batter.add_rbi()
                self.bases[1] = 0
            if self.bases[0] != 0:
                self.add_run(self.bases[0], pitcher)
                batter.add_rbi()
                self.bases[0] = 0
            self.bases[2] = batter
        # HOME RUN
        elif outcome == 'HR':
            pitcher.add_pitch_ha()
            if self.bases[2] != 0:
                self.add_run(self.bases[2], pitcher)
                batter.add_rbi()
                self.bases[2] = 0
            if self.bases[1] != 0:
                self.add_run(self.bases[1], pitcher)
                batter.add_rbi()
                self.bases[1] = 0
            if self.bases[0] != 0:
                self.add_run(self.bases[0], pitcher)
                batter.add_rbi()
                self.bases[0] = 0
            # update batter stats
            batter.add_hr()
            batter.add_rbi()
            self.add_run(batter, pitcher)
        # check inning and update
        if self.outs == 3:
            self.update_inning()

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

    def get_away_score(self):
        return self.score[0]

    def get_home_score(self):
        return self.score[0]

    def get_outs(self):
        return self.outs

    def add_out(self):
        self.outs += 1

    def add_run(self, scoring_runner, pitcher):
        if self.inn_stage == 'top':
            self.score[0] += 1
        else:
            self.score[1] += 1
        # calculate winning pitcher
        if math.fabs(self.score[0] - self.score[1]) == 1:
            if self.score[0] > self.score[1]:
                self.winning_pitcher = self.away_team.get_pitcher().get_name()
            else:
                self.winning_pitcher = self.home_team.get_pitcher().get_name()
        self.game_log.append("%s.%d:%s scores." % (
            self.inn_stage, self.inning,
            scoring_runner.get_name()))
        scoring_runner.add_run()
        pitcher.add_pitch_er()

    def get_inning(self):
        return self.inning

    def add_stolen_base(self):
        return None

    def get_stage(self):
        return self.inn_stage

    def update_inning(self):
        if self.inn_stage == 'bot':
            self.game_log.append('End of inning %s.' % self.inning)
            self.inn_stage = 'top'
            self.inning += 1
        else:
            self.inn_stage = 'bot'
        self.outs = 0
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
