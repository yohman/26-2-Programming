"""Game rules without a window; usable on any Python installation."""
def hit(score, seconds_left):
    if seconds_left > 0:
        return score + 1
    return score


def tick_state(seconds_left):
    return max(0, seconds_left - 1)
