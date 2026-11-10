"""Level 5 - Independent Repair (the pygame screen). The rules live in level5_logic.py.

This reuses Level 4's workbench (level4.run_repair_level). What is different: Martha gives no advice, there is
no review of the correct order (only the final result), and the only help is Relic Wisdom hints.
"""
from level1 import BAD, DARK_OLIVE, FADED, GOLD, GOOD, HEIGHT, OLIVE_GREEN, WIDTH, draw_text, wrap_text
from level2 import _wait_for_key
from level4 import run_repair_level
from level5_logic import DROPBACK_BELOW, LEVEL_END, LEVEL_START, Level5, result_text


def result_screen(window, fonts, clock, review):
    """The final result of one repair: whether it holds and the points, but not the right answer."""
    text = result_text(review)
    color = GOOD if review["points"] > 0 else BAD

    def draw():
        draw_text(window, "THE RESULT", fonts["big"], OLIVE_GREEN, (WIDTH // 2, 90), "center")
        draw_text(window, text["title"], fonts["mid"], DARK_OLIVE, (WIDTH // 2, 150), "center")
        draw_text(window, text["holds"], fonts["big"], GOOD if review["success"] else BAD, (WIDTH // 2, 240), "center")
        draw_text(window, text["summary"], fonts["mid"], color, (WIDTH // 2, 330), "center")
        y = 385
        for line in wrap_text(text["breakdown"], fonts["small"], 1000)[:2]:
            draw_text(window, line, fonts["small"], DARK_OLIVE, (WIDTH // 2, y), "center")
            y += 26
        if text["extra"]:
            draw_text(window, text["extra"], fonts["small"], OLIVE_GREEN, (WIDTH // 2, y + 20), "center")
        draw_text(window, "Press SPACE to continue", fonts["tiny"], OLIVE_GREEN, (WIDTH // 2, HEIGHT - 40), "center")

    _wait_for_key(window, clock, draw)


def complete_screen(window, fonts, level, clock):
    """The end of the game: the player reached 500 points."""
    state = level.state
    lines = [
        f"Repairs in this level: {level.jobs_done} ({level.successes} held)",
        f"Recovered parts used: {level.parts_used}",
        f"Relics restored in this level: {level.relics_restored}",
        f"Relics in your collection: {len(state.get('relic_collection', []))} of 8",
        f"Hints used: {level.hints_used}",
    ]

    def draw():
        draw_text(window, "THE CIRCULAR SILO", fonts["big"], OLIVE_GREEN, (WIDTH // 2, 80), "center")
        draw_text(window, "YOU CAN REPAIR ON YOUR OWN", fonts["mid"], GOLD, (WIDTH // 2, 140), "center")
        for i, line in enumerate(lines):
            draw_text(window, line, fonts["mid"], DARK_OLIVE, (WIDTH // 2, 210 + i * 40), "center")
        draw_text(window, "Nothing was thrown away that could be used again.", fonts["small"], OLIVE_GREEN,
                  (WIDTH // 2, 210 + len(lines) * 40 + 25), "center")
        draw_text(window, "Press SPACE to return to the menu", fonts["small"], OLIVE_GREEN, (WIDTH // 2, HEIGHT - 50), "center")

    _wait_for_key(window, clock, draw)
    return "complete"


def dropback_screen(window, fonts, level, clock):
    """Shown when a job ends with the score below 400: the player goes back to Level 4."""
    def draw():
        draw_text(window, "SCORE TOO LOW", fonts["big"], BAD, (WIDTH // 2, 170), "center")
        draw_text(window, f"Your score fell below {DROPBACK_BELOW}.", fonts["mid"], DARK_OLIVE, (WIDTH // 2, 260), "center")
        draw_text(window, "Martha sends you back to advanced repair. Earn the points again to return.", fonts["small"],
                  OLIVE_GREEN, (WIDTH // 2, 320), "center")
        draw_text(window, "Your parts, relics and hints are safe.", fonts["small"], OLIVE_GREEN, (WIDTH // 2, 355), "center")
        draw_text(window, "Press SPACE to continue", fonts["small"], OLIVE_GREEN, (WIDTH // 2, HEIGHT - 60), "center")

    _wait_for_key(window, clock, draw)
    return "dropback"


def run_level_5(window, state):
    """Play Level 5. Returns "complete" at 500 points, "dropback" below 400, or "menu" on ESC."""
    return run_repair_level(window, state, lambda st: Level5(st), "LEVEL 5 - INDEPENDENT REPAIR",
                            result_screen, complete_screen, dropback_screen)