"""
Greedy Knapsack approach to choosing a team.  Weighted toward big-hitters
that score a lot of points and value players otherwise.

ks = Knapsack(conf.max_salary)
print ks.calculate(players)
"""
class Knapsack(object):

    def __init__(cls, max_salary):
        cls.max_salary = max_salary

    def set_max_salary(self, max_salary):
        self.max_salary = max_salary

    """
    Solve the knapsack problem by finding the most valuable
    subsequence of `players based on 1. value and 2. potential
    """
    def calculate(self, players):
        if conf.sport_type == 'nfl':
            constraints = {
                'QB': 1,
                'RB': 2,
                'WR': 3,
                'TE': 1,
                'DST': 1,
                'FLEX': 1
            }
            
            counts = {
                'QB': 0,
                'RB': 0,
                'WR': 0,
                'TE': 0,
                'DST': 0,
                'FLEX': 0
            }
        elif conf.sport_type == 'mlb':
            constraints = {
                'P': 1,
                'C': 1,
                'SS': 1,
                '1B': 1,
                '2B': 1,
                '3B': 1,
                'OF': 3
            }
            counts = {
                'P': 0,
                'C': 0,
                'SS': 0,
                '1B': 0,
                '2B': 0,
                '3B': 0,
                'OF': 0
            }

        players.sort(key=lambda x: float(x['value']) / float(x['cost']), reverse=True)
        current_team_salary = 0
        team = []
        for player in players:
            nam = player['name']
            pos = player['pos']
            sal = player['cost']
            pts = player['value']
            if counts[pos] < constraints[pos] and current_team_salary + sal <=\
                    self.max_salary:
                team.append(player)
                counts[pos] += 1
                current_team_salary += sal
                continue
        players.sort(key=lambda x: x['value'], reverse=True)
        for player in players:
            nam = player['name']
            pos = player['pos']
            sal = player['cost']
            pts = player['value']
            if player not in team:
                position_players = [x for x in team if x['pos'] == pos]
                position_players.sort(key=lambda x: x['value'])
                # compare our current player to the players in the existing position
                for pos_player in position_players:
                    # if we can still stay under the cap and sub out
                    # the player for a better performer, do it
                    if (current_team_salary + sal - pos_player['cost']) <=\
                            self.max_salary and pts > pos_player['value']:
                        team[team.index(pos_player)] = player
                        current_team_salary = current_team_salary + sal -\
                            pos_player['cost']
                        break
        self.team = team
        return team

