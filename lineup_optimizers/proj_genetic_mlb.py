"""Classes for genetic mlb lineup optimization."""
import collections
import conf
import pdb
import random
import numpy as np
import hashlib
from operator import add


class GeneticMLB(object):

    def __init__(cls, max_salary):
        cls.max_salary = max_salary
        cls.team = None
        cls.computed_lineups = {}

    ###############
    # MAIN RUNNER #
    ###############
    def calculate_random_sample(self, proj):
        """Find best teams based on points in randomly_selected outputs."""
        return None

    def calculate(self, proj):
        """Find best teams using fitness based on profitability percent."""
        best_teams = []
        history = []
        players = proj.index
        pos_players = {
            "C": [proj.loc[player] for player in players if 'C' in proj.at[
                player, 'pos']],
            "OF": [proj.loc[player] for player in players if 'OF' in proj.at[
                player, 'pos']],
            "SS": [proj.loc[player] for player in players if 'SS' in proj.at[
                player, 'pos']],
            "1B": [proj.loc[player] for player in players if '1B' in proj.at[
                player, 'pos']],
            "2B": [proj.loc[player] for player in players if '2B' in proj.at[
                player, 'pos']],
            "3B": [proj.loc[player] for player in players if '3B' in proj.at[
                player, 'pos']]
        }
        if conf.site == 'fanduel':
            pos_players["P"] = [proj.loc[player] for player in players if 'P'
                                in proj.at[player, 'pos']]
        else:
            pos_players["P"] = [proj.loc[player] for player in players if 'SP'
                                in proj.at[player, 'pos']]
        print "\nGENETIC LINEUP OPTIMIZER\n"
        pop = self.create_population(conf.population_size, pos_players)
        # fitness_history = [self.grade(pop)]
        # 40 iterations of our evolution
        for i in xrange(conf.genetic_generations):
            print "Computing generation %d of %d" % (i + 1, conf.genetic_generations)
            graded = [(self.fitness(team), team) for team in pop]
            graded = [x[1] for x in sorted(graded, key=lambda x: x[0], reverse=True)]
            pop = self.evolve(graded, pos_players)
            # fitness_history.append(self.grade(pop))
            valid_teams = [team for team in graded if not
                           self._violates_limits(team)]
            valid_teams = sorted(valid_teams, key=lambda x: self.fitness(x), reverse=True)
            if len(valid_teams) > 0:
                best_teams.append(valid_teams[0])
        # for datum in fitness_history:
            # history.append(datum)
        best_teams += pop
        real_best_teams = []
        added_teams = []
        for team in best_teams:
            primary_players = frozenset([player for players in [[x.name for x in team[key]] for key in team] for player in players])
            key = hash(primary_players)
            if self._violates_limits(team) or key in added_teams:
                continue
            real_best_teams.append(team)
            added_teams.append(key)
        if conf.sort_by == 'cost':
            real_best_teams = sorted(real_best_teams, key=lambda x: self.get_team_salary(x), reverse=True)
        elif conf.sort_by == 'cost-points':
            real_best_teams = sorted(real_best_teams, key=lambda x: (
                self.get_team_salary(x), self._get_team_point_total(x)),
                reverse=True)
        elif conf.sort_by == 'cost-fitness':
            real_best_teams = sorted(real_best_teams, key=lambda x: (self.get_team_salary(x), self.fitness(x)), reverse=True)
        elif conf.sort_by == 'fitness':
            real_best_teams = sorted(real_best_teams, key=lambda x: self.fitness(x), reverse=True)
        else:
            raise ValueError('please specify a sorting criteria of cost or points in conf.sort_by')
        return real_best_teams

    def set_max_salary(self, max_salary):
        self.max_salary = max_salary

    def create_population(self, count, sample):
        return [self._create_random_team(sample) for i in range(0, count)]

    def _create_random_team(self, pos_players):
        team = {
            'C': random.sample(pos_players['C'], 1),
            'SS': random.sample(pos_players['SS'], 1),
            '1B': random.sample(pos_players['1B'], 1),
            '2B': random.sample(pos_players['2B'], 1),
            '3B': random.sample(pos_players['3B'], 1),
            'OF': random.sample(pos_players['OF'], 3),
        }
        if conf.site == 'fanduel':
            team['P'] = random.sample(pos_players['P'], 1)
        elif conf.site == 'draftkings':
            team['P'] = random.sample(pos_players['P'], 2)
        return team

    def get_team_salary(self, team):
        total_salary = 0
        for pos, players in team.iteritems():
            for player in players:
                total_salary += player["cost"]
        return total_salary

    def print_team(self, team):
        print team['P'][0]
        if conf.site == 'draftkings':
            print team['P'][1]
        print team['C'][0]
        print team['SS'][0]
        print team['1B'][0]
        print team['2B'][0]
        print team['3B'][0]
        print team['OF'][0]
        print team['OF'][1]
        print team['OF'][2]

    def evolve(self, pop_graded, sample, retain=conf.retain,
               random_select=conf.random_select, mutate_chance=conf.mutate_chance):
        retain_length = int(len(pop_graded) * retain)
        parents = pop_graded[:retain_length]

        # randomly add other individuals to promote genetic diversity
        for individual in pop_graded[retain_length:]:
            if random_select > random.random():
                parents.append(individual)

        # mutate some individuals
        for individual in parents:
            if mutate_chance > random.random():
                individual = self.mutate(individual, sample)

        # crossover parents to create children
        parents_length = len(parents)
        desired_length = len(pop_graded) - parents_length
        children = []
        while len(children) < desired_length:
            male = random.randint(0, parents_length - 1)
            female = random.randint(0, parents_length - 1)
            if male != female:
                male = parents[male]
                female = parents[female]
                babies = self.breed(male, female)
                for baby in babies:
                    children.append(baby)
        parents.extend(children)
        return parents

    def fitness(self, team):
        primary_players = frozenset([player for players in [[x.name for x in team[key]] for key in team] for player in players])
        key = hash(primary_players)
        # hashlib.sha256(str(team)).hexdigest()
        # cache precomputed results locally
        if key in self.computed_lineups:
            return self.computed_lineups[key]
        else:
            if conf.genetic_approach == 'profitability':
                if self._violates_limits(team):
                    return 0
                prof_val = self._get_lineup_profitability_count(team)
                self.computed_lineups[key] = prof_val
                return prof_val
            elif conf.genetic_approach == 'mean':
                points = self.get_team_mean_point_total(team)
                salary = self.get_team_salary(team)
                if salary > self.max_salary or self._has_duplicate_players(team):
                    return 0
                return points - self._playing_against_self(team)
            else:
                raise ValueError('Please specify "profitability" or "mean"')

    def _get_lineup_profitability_count(self, team, profitability_cutoff=conf.profitable_cutoff):
        count = 0
        for i in range(conf.simulated_game_count):
            if self._get_team_point_total(team, i) > profitability_cutoff:
                count += 1
        return count

    def _playing_against_self(self, team):
        'Returns a negative weight for conflicting teams'
        # gets a flattened set of the teams on our team
        primary_teams = set([this_team for t in [[
            x['team'] for x in team[item]] for item in team]
            for this_team in t])
        primary_opponents = set([that_team for t in [[
            x['opp_team'] for x in team[item]] for item in team]
            for that_team in t])
        conflict_instances = len(primary_teams.intersection(primary_opponents))
        return conflict_instances * conf.self_defeating_weight

    def _get_team_point_total(self, team, simulation_idx):
        total_points = 0
        for pos, players in team.iteritems():
            for player in players:
                total_points += player[simulation_idx]
        return total_points

    def get_team_mean_point_total(self, team):
        total_points = 0
        for pos, players in team.iteritems():
            for player in players:
                total_points += player['mean']
        return total_points

    ####################
    # LIMIT VIOLATIONS #
    ####################
    def _violates_limits(self, team):
        if self.get_team_salary(team) > self.max_salary or\
                self._has_duplicate_players(team)\
                or self._exceeds_max_team_count(team):
            return True
        else:
            return False

    def _exceeds_max_team_count(self, team):
        primary_teams = [[x['team'] for x in team[item]] for item in team]
        team_counts = [count for item, count in collections.Counter(
            [t for teams in primary_teams for t in teams]).items()
            if count > 1]
        for count in team_counts:
            if count > conf.max_team_repetition:
                return True
        return False

    def _has_duplicate_players(self, team):
        # gives us a set of all the names
        primary_players = frozenset(
            [player for players in [[x.name for x in team[key]] for key in team] for player in players])
        if conf.site == 'fanduel' and len(primary_players) < 9:
            return True
        elif conf.site == 'draftkings' and len(primary_players) < 10:
            return True

    def grade(self, pop):
        """Find average fitness for a population."""
        summed = reduce(add, (self.fitness(team) for team in pop))
        return summed / float(len(pop))

    def list_to_team(self, players):
        """Return teams as a list."""
        if conf.site == 'fanduel':
            return {
                'P': [players[0]],
                'C': [players[1]],
                'SS': [players[2]],
                '1B': [players[3]],
                '2B': [players[4]],
                '3B': [players[5]],
                'OF': players[6:9]
            }
        elif conf.site == 'draftkings':
            return {
                'P': players[0:2],
                'C': [players[2]],
                'SS': [players[3]],
                '1B': [players[4]],
                '2B': [players[5]],
                '3B': [players[6]],
                'OF': players[7:10]
            }

    def breed(self, mother, father):
        """Breed together two teams by swapping at a random index."""
        mother_list = [mother['P'] + mother['C'] + mother['SS'] +
                       mother['1B'] + mother['2B'] + mother['3B'] +
                       mother['OF']]
        mother_list = [player for players in mother_list for player in players]
        father_list = [father['P'] + father['C'] + father['SS'] +
                       father['1B'] + father['2B'] + father['3B'] +
                       father['OF']]
        father_list = [player for players in father_list for player in players]
        if conf.site == 'fanduel':
            index = random.choice([1, 2, 3, 4, 5, 6, 7, 8])
        elif conf.site == 'draftkings':
            index = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9])
        child1 = self.list_to_team(mother_list[0:index] + father_list[index:])
        child2 = self.list_to_team(father_list[0:index] + mother_list[index:])
        return[child1, child2]

    def mutate(self, team, sample):
        """Mutate the team by randomly subbing one position."""
        positions = ['P', 'C', 'SS', '1B', '2B', '3B', 'OF']
        random_pos = random.choice(positions)
        if random_pos == 'P' and conf.site == 'fanduel':
            team['P'][0] = random.choice(sample['P'])
        elif random_pos == 'P' and conf.site == 'draftkings':
            team['P'] = random.sample(sample['P'], 2)
        elif random_pos == 'C':
            team['C'][0] = random.choice(sample['C'])
        elif random_pos == 'SS':
            team['SS'][0] = random.choice(sample['SS'])
        elif random_pos == '1B':
            team['1B'][0] = random.choice(sample['1B'])
        elif random_pos == '2B':
            team['2B'][0] = random.choice(sample['2B'])
        elif random_pos == '3B':
            team['3B'][0] = random.choice(sample['3B'])
        elif random_pos == 'OF':
            team['OF'] = random.sample(sample['OF'], 3)
        return team
