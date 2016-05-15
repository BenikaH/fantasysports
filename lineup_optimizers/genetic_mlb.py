"""Classes for genetic mlb lineup optimization."""
import collections
import conf
import pdb
import random
import math
from operator import add


class GeneticMLB(object):

    def __init__(cls, max_salary):
        cls.max_salary = max_salary
        cls.team = None

    def calculate(self, players):
        best_teams = []
        history = []
        pos_players = {
            "P": [player for player in players if player['pos'] == 'P'],
            "C": [player for player in players if player['pos'] == 'C'],
            "OF": [player for player in players if player['pos'] == 'OF'],
            "SS": [player for player in players if player['pos'] == 'SS'],
            "1B": [player for player in players if player['pos'] == '1B'],
            "2B": [player for player in players if player['pos'] == '2B'],
            "3B": [player for player in players if player['pos'] == '3B']
        }
        pop = self.create_population(conf.population_size, pos_players)
        fitness_history = [self.grade(pop)]
        # 40 iterations of our evolution
        for i in xrange(conf.genetic_generations):
            pop = self.evolve(pop, pos_players)
            fitness_history.append(self.grade(pop))
            valid_teams = [team for team in pop if self.get_team_salary(team) <= self.max_salary]
            valid_teams = sorted(valid_teams, key=self.get_team_point_total, reverse=True)
            if len(valid_teams) > 0:
                best_teams.append(valid_teams[0])
        for datum in fitness_history:
            history.append(datum)

        real_best_teams = []
        for team in best_teams:
            if self._has_duplicate_players(team) or self.get_team_salary(team) > self.max_salary or team in real_best_teams:
                continue
            real_best_teams.append(team)
        if conf.sort_by == 'cost':
            real_best_teams = sorted(real_best_teams, key=lambda x: self.get_team_salary(x), reverse=True)
        elif conf.sort_by == 'points':
            real_best_teams = sorted(real_best_teams, key=lambda x: self.get_team_point_total(x), reverse=True)
        elif conf.sort_by == 'cost-points':
            real_best_teams = sorted(real_best_teams, key=lambda x: (self.get_team_salary(x), self.get_team_point_total(x)), reverse=True)
        elif conf.sort_by == 'cost-fitness':
            real_best_teams = sorted(real_best_teams, key=lambda x: (self.get_team_salary(x), self.fitness(x)), reverse=True)
        elif conf.sort_by == 'fitness':
            real_best_teams = sorted(real_best_teams, key=lambda x: self.fitness(x), reverse=True)
        else:
            raise ValueError('please specify a sorting criteria of cost or points in conf.sort_by')
        return real_best_teams[0:10]

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

    def get_team_point_total(self, team):
        total_points = 0
        for pos, players in team.iteritems():
            for player in players:
                try:
                    total_points += player["value"]
                except:
                    pdb.set_trace()
        return total_points

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

    def evolve(self, pop, sample, retain=conf.retain,
               random_select=conf.random_select, mutate_chance=conf.mutate_chance):
        graded = [(self.fitness(team), team) for team in pop]
        graded = [x[1] for x in sorted(graded, reverse=True)]
        retain_length = int(len(graded) * retain)
        parents = graded[:retain_length]

        # randomly add other individuals to promote genetic diversity
        for individual in graded[retain_length:]:
            if random_select > random.random():
                parents.append(individual)

        # mutate some individuals
        for individual in parents:
            if mutate_chance > random.random():
                individual = self.mutate(individual, sample)

        # crossover parents to create children
        parents_length = len(parents)
        desired_length = len(pop) - parents_length
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
        if self._violates_limits(team):
            return 0
        return self.get_team_point_total(team) -\
            self._get_point_deductions(team) + self._get_point_bonuses(team)

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
            if count > 4:
                return True
        return False

    def _has_duplicate_players(self, team):
        # gives us a set of all the names
        primary_players = set([player for players in [[
            x['name'] for x in team[key]] for key in team]
            for player in players])
        if conf.site == 'fanduel' and len(primary_players) < 9:
            return True
        elif conf.site == 'draftkings' and len(primary_players) < 10:
            return True

    ####################
    # POINT DEDUCTIONS #
    ####################
    def _get_point_deductions(self, team):
        return self._playing_against_self(team)

    def _playing_against_self(self, team):
        'Returns a negative weight for conflicting teams'
        # gets a flattened array of the teams on our team
        primary_teams = set([this_team for t in [[
            x['team'] for x in team[item]] for item in team]
            for this_team in t])
        primary_opponents = set([that_team for t in [[
            x['opp'] for x in team[item]] for item in team]
            for that_team in t])
        conflict_instances = len(primary_teams.intersection(primary_opponents))
        return conflict_instances * conf.self_defeating_weight

    #################
    # POINT BONUSES #
    #################
    def _get_point_bonuses(self, team):
        return self._same_team_bonus(team)

    def _same_team_bonus(self, team):
        primary_teams = [t for teams in [[x['team'] for x in team[item]]
                         for item in team] for t in teams]
        primary_teams.remove(team['P'][0]['team'])
        if conf.site == 'draftkings':
            primary_teams.remove(team['P'][1]['team'])
        team_counts = [count for item, count in collections.Counter(
            primary_teams).items()
            if count > 1]
        stack_bonus = 0
        if 4 in team_counts and team['P'][0]['team'] not in primary_teams:
            stack_bonus += conf.stack_bonus
        primary_teams = [[x['team'] for x in team[item]] for item in team]
        primary_teams = set(
            [this_team for t in primary_teams for this_team in t])
        same_team_bonus = 9 - len(primary_teams)
        # if same_team_bonus > (9 - conf.min_different_teams):
        #     return 0
        return (same_team_bonus * conf.same_team_bonus_weight) + stack_bonus

    def grade(self, pop):
        'Find average fitness for a population.'
        summed = reduce(add, (self.fitness(team) for team in pop))
        return summed / float(len(pop))

    def list_to_team(self, players):
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
