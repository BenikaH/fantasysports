"""Utility File"""

def is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        return False