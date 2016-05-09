"""Classes for genetic mlb lineup optimization."""
import collections
import conf
import pdb
import random
import math
from operator import add


class GeneticNBA(object):

    def __init__(cls, max_salary):
        cls.max_salary = max_salary
        cls.team = None

    def calculate(self, players):
        best_teams = []
        history = []
        pos_players = {
            "PG": [player for player in players if player['pos'] == 'PG'],
            "SG": [player for player in players if player['pos'] == 'SG'],
            "SF": [player for player in players if player['pos'] == 'SF'],
            "PF": [player for player in players if player['pos'] == 'PF'],
            "C": [player for player in players if player['pos'] == 'C']
        }
        pop = self.create_population(conf.population_size, pos_players)
        fitness_history = [self.grade(pop)]
        # conf.genetnic_generation iterations of our evolution
        for i in xrange(conf.genetic_generations):
            pop = self.evolve(pop, pos_players)
            fitness_history.append(self.grade(pop))
            valid_teams = [team for team in pop if self.get_team_salary(team) <= self.max_salary]
            valid_teams = sorted(valid_teams, key=self.get_team_point_total, reverse=True)
            if len(valid_teams) > 0:
                best_teams.append(valid_teams[0])
        for datum in fitness_history:
            history.append(datum)

        best_teams = sorted(best_teams, key=self.get_team_salary, reverse=True)
        return best_teams[0:10]

    def set_max_salary(self, max_salary):
        self.max_salary = max_salary

    def create_population(self, count, sample):
        return [self._create_random_team(sample) for i in range(0, count)]

    def _create_random_team(self, pos_players):
        team = {
            "PG": random.sample(pos_players['PG'], 2),
            "SG": random.sample(pos_players['SG'], 2),
            "SF": random.sample(pos_players['SF'], 2),
            "PF": random.sample(pos_players['PF'], 2),
            "C": random.sample(pos_players['C'], 1)
        }
        return team

    def get_team_point_total(self, team):
        total_points = 0
        for pos, players in team.iteritems():
            for player in players:
                total_points += player["value"]
        return total_points

    def get_team_salary(self, team):
        total_salary = 0
        for pos, players in team.iteritems():
            for player in players:
                total_salary += player["cost"]
        return total_salary

    def print_team(self, team):
        print team['PG'][0]
        print team['PG'][1]
        print team['SG'][0]
        print team['SG'][1]
        print team['SF'][0]
        print team['SF'][1]
        print team['PF'][0]
        print team['PF'][1]
        print team['C'][0]

    def evolve(self, pop, sample, retain=0.35, random_select=0.05, mutate_chance=0.005):
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
        points = self.get_team_point_total(team)
        salary = self.get_team_salary(team)
        if salary > self.max_salary or self._has_duplicate_players(team)\
                or self._exceeds_max_team_count(team):
            return 0
        if conf.limit_conflicting_teams:
            points -= self._playing_against_self(team)
        if conf.same_team_bonus:
            points += self._same_team_bonus(team)
        return points

    def _playing_against_self(self, team):
        'Returns a negative weight for conflicting teams'
        # gets a flattened array of the teams on our team
        primary_teams = [[x['team'] for x in team[item]] for item in team]
        primary_teams = set([this_team for t in primary_teams for this_team in t])
        primary_opponents = [[x['opp'] for x in team[item]] for item in team]
        primary_opponents = set([that_team for t in primary_opponents for that_team in t])
        conflict_instances = len(primary_teams.intersection(primary_opponents))
        return conflict_instances * conf.self_defeating_weight

    def _exceeds_max_team_count(self, team):
        primary_teams = [[x['team'] for x in team[item]] for item in team]
        team_counts = [count for item, count in collections.Counter(
            [t for teams in primary_teams for t in teams]).items() if count > 1]
        for count in team_counts:
            if count > 4:
                return True
        return False

    def _same_team_bonus(self, team):
        primary_teams = [[x['team'] for x in team[item]] for item in team]
        team_counts = [count for item, count in collections.Counter(
            [t for teams in primary_teams for t in teams]).items() if count > 1]
        stack_bonus = 0
        if 4 in team_counts:
            stack_bonus += conf.stack_bonus
        primary_teams = set([this_team for t in primary_teams for this_team in t])
        same_team_bonus = 9 - len(primary_teams)
        return (same_team_bonus * conf.same_team_weight) + stack_bonus

    def _has_duplicate_players(self, team):
        primary_players = set([x['name'] for x in team['OF']])
        if len(primary_players) < 3:
            return True

    def grade(self, pop):
        'Find average fitness for a population.'
        summed = reduce(add, (self.fitness(team) for team in pop))
        return summed / float(len(pop))

    def list_to_team(self, players):
        return {
            'PG': players[0:1],
            'SG': players[2:3],
            'SF': players[4:5],
            'PF': players[6:7],
            'C': [players[8]]
        }

    def breed(self, mother, father):
        mother_list = [mother['PG'] + mother['SG'] + mother['SF'] + mother['PF'] + mother['C']]
        mother_list = [player for players in mother_list for player in players]
        father_list = [father['PG'] + father['SG'] + father['SF'] + father['PF'] + father['C']]
        father_list = [player for players in father_list for player in players]

        index = random.choice([1, 2, 3, 4, 5, 6, 7])
        child1 = self.list_to_team(mother_list[0:index] + father_list[index:])
        child2 = self.list_to_team(father_list[0:index] + mother_list[index:])
        return[child1, child2]

    def mutate(self, team, sample):
        positions = ['PG', 'SG', 'SF', 'PF', 'C']
        random_pos = random.choice(positions)
        if random_pos == 'PG':
            team['PG'] = random.sample(sample['PG'], 2)
        elif random_pos == 'SG':
            team['SG'] = random.sample(sample['SG'], 2)
        elif random_pos == 'SF':
            team['SF'] = random.sample(sample['SF'], 2)
        elif random_pos == 'PF':
            team['PF'] = random.sample(sample['PF'], 2)
        elif random_pos == 'C':
            team['C'][0] = random.choice(sample['C'])
        return team
