"""Classes for lineup optimization"""
import functools
import conf

class Knapsack:

    def __init__(cls, max_salary):
        cls.max_salary = max_salary


    def set_max_salary(self, max_salary):
        self.max_salary = max_salary

    """
    Solve the knapsack problem by finding the most valuable
    subsequence of `players` that costs no more than `self.max_salary`.

    `players` is a sequence of quadruplets `(proj_points, cost, position, name)`,
    where `proj_points` is a float and `cost` is a non-negative integer.

    Return a pair whose first element is the sum of projected output in the most
    valuable subsequence, and whose second element is the subsequence.

    >>> ks = Knapsack(105000)
    >>> players = [(4.8, 2200, 'C', 'Matt Wieters'),...]
    >>> ks.calculate(players)
    (max_points, [(4.8, 2200, 'C', 'Matt Wieters')...])
    """
    def calculate(self, players):
        # Return the value of the most valuable subsequence of the first i
        # elements in items whose weights sum to no more than j.
        # @memoized
        # def bestvalue(i, max_sal):
        #     if i == 0:
        #         return 0
        #     value, cost = players[i - 1][0:2]
        #     if cost > max_sal:
        #         return bestvalue(i - 1, max_sal)
        #     else:
        #         return max(bestvalue(i - 1, max_sal),
        #                    bestvalue(i - 1, max_sal - cost) + value)

        # j = self.max_salary
        # result = []
        # for i in xrange(len(players), 0, -1):
        #     if bestvalue(i, j) != bestvalue(i - 1, j):
        #         result.append(players[i - 1])
        #         j -= players[i - 1][1]
        # result.reverse()
        # return bestvalue(len(players), self.max_salary), result

        # def points_knapsack(players):
        #     current_team_salary = 0
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
                'P': 1,
                'C': 1,
                'SS': 1,
                '1B': 1,
                '2B': 1,
                '3B': 1,
                'OF': 3
            }
        
        players.sort(key=lambda x: x.value, reverse=True)
        team = []
        
        for player in players:
            name = player[3]
            pos = player[2]
            sal = player[1]
            pts = player[0]
            if counts[pos] < constraints[pos] and current_team_salary + sal <= budget:
                team.append(player)
                counts[pos] = counts[pos] + 1
                current_team_salary += sal
                continue
            if counts['FLEX'] < constraints['FLEX'] and current_team_salary + sal <= budget and pos in ['RB','WR','TE']:
                team.append(player)
                counts['FLEX'] = counts['FLEX'] + 1
                current_team_salary += sal 
        
        players.sort(key=lambda x: x.points, reverse=True)
        for player in players:
            nam = player.name
            pos = player.position
            sal = player.salary
            pts = player.points
            if player not in team:
                pos_players = [ x for x in team if x.position == pos]
                pos_players.sort(key=lambda x: x.points)
                for pos_player in pos_players:
                    if (current_team_salary + sal - pos_player.salary) <= budget and pts > pos_player.points:
                        team[team.index(pos_player)] = player
                        current_team_salary = current_team_salary + sal - pos_player.salary
                        break
        return team