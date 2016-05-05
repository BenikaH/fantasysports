"""Calculates FanDuel and DraftKings Predicted Scores Based on Projections."""


# FANDUEL SCORING
"""
Hitters
Singles (1B) 3
Doubles (2B) 6
Triples (3B) 9
Walks (BB) 3
Hit By Pitches (HBP) 3
Home Runs (HR) 12
Runs (R) 3.2
Runs Batted In (RBI) 3.5
Stolen Bases (SB) 6

Pitchers
Earned Runs Allowed (ER) -3
Innings Pitched (IP) 3
Strike Outs Thrown (SO) 3
Winning Pitcher (W) 12
"""
def calculate_fanduel_hitter_score(sing, doub, trip, walk, hbp, hr, runs, rbi, sb):
    return ((3.0 * sing) + (6.0 * doub) + (9.0 * trip) + (3.0 * walk)
        + (3.0 * hbp) + (12.0 * hr) + (3.2 * runs) + (3.5 * rbi) + (6.0 * sb))

def calculate_fanduel_pitcher_score(er, ip, so, win):
    return (3.0 * er) + (6.0 * ip) + (9.0 * so) + (3.0 * win)