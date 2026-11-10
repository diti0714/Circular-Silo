"""Level 5 - Independent Repair: the rules only (no pygame).

Martha no longer gives advice and no longer reviews the repair. The player gets a damaged object,
inspects it, works out what is wrong, chooses the repair actions, uses recovered parts and puts the
actions in the right order. The scoring is the same as in Level 4 (percentage of the required order
that is right, -5 for each wrong action, +5 for a recovered part, +30 for a restored relic) but the
player only sees the final result, never the correct answer. The only help is Relic Wisdom hints
from the Hint Pouch.

Level 5 covers 400 to 500 points. Reaching 500 finishes the game; falling below 400 returns the
player to Level 4. The jobs are the same objects as in Level 4: this level tests what the player
learned there and in Level 3.
"""
from level1_logic import TARGET
from level4_logic import Level4


class Level5(Level4):
    NUMBER = 5
    START = 4 * TARGET
    END = 5 * TARGET
    DROP = START
    GUIDED = False


LEVEL_START = Level5.START
LEVEL_END = Level5.END
DROPBACK_BELOW = Level5.DROP


def result_text(r):
    """What the player is told when the repair is finished: the result, never the right answer."""
    holds = "The repair holds." if r["success"] else "The repair does not hold."
    parts = [f"Order {r['scale_points']:+d}"]
    if r["wrong_count"]:
        parts.append(f"Wrong actions {r['wrong_points']:+d}")
    if r["part"] and r["part"]["stored"]:
        parts.append(f"Recovered {r['part']['name'].lower()} {r['part_points']:+d}")
    if r["relic_bonus"]:
        parts.append(f"Relic bonus {r['relic_bonus']:+d}")
    extra = ""
    if r["relic_retry"]:
        extra = "The relic is safe, so you can try again later."
    return {"title": r["name"] + (" (relic)" if r["relic"] else ""),
            "summary": f"Correct: {r['correct']} of {r['total']} ({r['percent']}%)     TOTAL {r['points']:+d}",
            "holds": holds, "breakdown": "     ".join(parts), "extra": extra}