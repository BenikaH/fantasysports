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


def calculate_fanduel_hitter_score(sing, doub, trip, walk, hbp, hr, runs,
                                   rbi, sb):
    """Return fanduel hitter score based on stats."""
    return ((3.0 * sing) + (6.0 * doub) + (9.0 * trip) + (3.0 * walk)
            + (3.0 * hbp) + (12.0 * hr) + (3.2 * runs) + (3.5 * rbi) + (6.0 * sb))


def calculate_fanduel_pitcher_score(er, ip, so, win):
    """Return fanduel pitcher score based on stats."""
    return (-3.0 * er) + (6.0 * ip) + (9.0 * so) + (12.0 * win)

# Draftkings SCORING
"""
Hitters
Single = +3 PTs
Double = +5 PTs
Triple = +8 PTs
Home Run = +10 PTs
Run Batted In = +2 PTs
Run = +2 PTs
Base on Balls = +2 PTs
Hit By Pitch = +2 PTs
Stolen Base = +5 PTs

Pitchers
Inning Pitched = +2.25 PTs
Strike Out = +2 PTs
Win = +4 PTs
Earned Run Allowed = -2 PTs
Hit Against = -0.6 PTs
Base on Balls Against = -0.6 PTs
Hit Batsman = -0.6 PTs
Complete Game = +2.5 PTs
Complete Game Shut Out = +2.5 PTs
No Hitter = +5 PTs
"""


def calculate_draftkings_hitter_score(sing, doub, trip, walk, hbp, hr, runs,
                                      rbi, sb):
    return ((3.0 * sing) + (5.0 * doub) + (8.0 * trip) + (2.0 * walk) +
            (2.0 * hbp) + (10.0 * hr) + (2.0 * runs) + (2.0 * rbi) +
            (5.0 * sb))
