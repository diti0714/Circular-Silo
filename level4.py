"""Level 4 - Advanced Repair (the pygame screen). The rules live in level4_logic.py."""
import sys

import pygame

from level1 import (BAD, BG_YELLOW, CARD_START_X, DARK_OLIVE, FADED, GOLD, GOOD, HEIGHT, OLIVE_GREEN, PANEL,
                    WIDTH, Btn, draw_text, draw_top_bar, wrap_text)
from level2 import _wait_for_key
from level3 import draw_fit, draw_job_card, draw_parts_box, relic_screen
from level4_logic import CHOICE_LABELS, DROPBACK_BELOW, LEVEL_START, Level4
from settings import get_font

ACTION_KEYS = [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h]
LETTERS = "ABCDEFGH"
MARK_KEYS = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]

MARTHA_BOX = pygame.Rect(295, 95, 860, 78)
FINDINGS_BOX = pygame.Rect(295, 181, 360, 152)
SEQUENCE_BOX = pygame.Rect(45, 392, 780, 78)
PARTS_BOX = pygame.Rect(840, 392, 315, 78)
PANEL_BOX = pygame.Rect(80, 478, 1040, 110)


def chip_rect(i):
    """The four findings sit in a column in the middle."""
    return pygame.Rect(295, 181 + i * 38, 360, 34)


def action_rect(i):
    """The eight actions sit in two columns on the right."""
    return pygame.Rect(670 + (i % 2) * 247, 181 + (i // 2) * 42, 238, 34)


# ---- drawing -------------------------------------------------------------------------------------
def draw_martha(surface, fonts, job, guided=True):
    box = MARTHA_BOX
    pygame.draw.rect(surface, PANEL, box)
    pygame.draw.rect(surface, OLIVE_GREEN, box, width=3)
    draw_text(surface, "MARTHA", fonts["tiny"], OLIVE_GREEN, (box.x + 14, box.y + 8))
    if not guided:
        draw_text(surface, "Martha has stepped back. This repair is yours alone.", fonts["small"], DARK_OLIVE,
                  (box.x + 14, box.y + 28))
        draw_text(surface, "Only your Relic Wisdom can help you now.", fonts["small"], DARK_OLIVE,
                  (box.x + 14, box.y + 52))
        return
    for i, line in enumerate(wrap_text(job["advice"], fonts["small"], box.w - 28)[:2]):
        draw_text(surface, line, fonts["small"], DARK_OLIVE, (box.x + 14, box.y + 28 + i * 24))


def draw_findings(surface, fonts, level):
    if not level.inspected:
        pygame.draw.rect(surface, FADED, FINDINGS_BOX, width=3)
        draw_text(surface, "What is wrong with it?", fonts["small"], DARK_OLIVE, (FINDINGS_BOX.centerx, 230), "center")
        draw_text(surface, "Inspect the object to find out.", fonts["small"], OLIVE_GREEN,
                  (FINDINGS_BOX.centerx, 262), "center")
        draw_text(surface, "[I]", fonts["small"], OLIVE_GREEN, (FINDINGS_BOX.centerx, 292), "center")
        return
    for i, finding in enumerate(level.job["findings"]):
        rect = chip_rect(i)
        marked, revealed = i in level.marks, i in level.revealed_faulty
        border = BAD if revealed else (DARK_OLIVE if marked else OLIVE_GREEN)
        if marked or revealed:
            pygame.draw.rect(surface, PANEL, rect)
        pygame.draw.rect(surface, border, rect, width=5 if marked else 3)
        draw_text(surface, f"{'[!]' if marked else '[ ]'} {i + 1}. {finding['name']}", fonts["tiny"], DARK_OLIVE,
                  (rect.x + 10, rect.y + 3))
        draw_text(surface, finding["note"], fonts["tiny"], DARK_OLIVE, (rect.x + 32, rect.y + 17))
        if revealed:
            draw_text(surface, "FAULTY", fonts["tiny"], BAD, (rect.right - 10, rect.y + 4), "topright")


def draw_action(surface, fonts, rect, letter, label, order, tag, trapped, hover):
    chosen = order is not None
    color = FADED if trapped else (DARK_OLIVE if (chosen or hover) else OLIVE_GREEN)
    if (chosen or hover) and not trapped:
        pygame.draw.rect(surface, PANEL, rect)
    pygame.draw.rect(surface, color, rect, width=5 if chosen else 3)
    draw_fit(surface, f"{letter}. {label}", fonts, color, pygame.Rect(rect.x, rect.y, rect.w - 34, rect.h),
             keys=("tiny",))
    if chosen:
        draw_text(surface, str(order), fonts["tiny"], DARK_OLIVE, (rect.right - 8, rect.y + 3), "topright")
    if tag:
        draw_text(surface, tag, fonts["tiny"], GOLD, (rect.right - 8, rect.bottom - 3), "bottomright")
    if trapped:
        pygame.draw.line(surface, BAD, (rect.x + 4, rect.y + 4), (rect.right - 4, rect.bottom - 4), 3)


def draw_sequence(surface, fonts, level):
    box = SEQUENCE_BOX
    pygame.draw.rect(surface, FADED, box, width=3)
    draw_text(surface, "YOUR REPAIR ORDER", fonts["tiny"], OLIVE_GREEN, (box.x + 12, box.y + 6))
    if not level.sequence:
        draw_text(surface, "Choose your actions in the order you would do them.", fonts["small"], FADED,
                  (box.x + 12, box.y + 32))
        return
    actions = level.job["actions"]
    text = "   ".join(f"{n}. {actions[i]['label']}" for n, i in enumerate(level.sequence, start=1))
    lines = wrap_text(text, fonts["tiny"], box.w - 24)
    if len(lines) > 3:
        lines = lines[:2] + [lines[2].rstrip() + " ..."]
    for i, line in enumerate(lines):
        draw_text(surface, line, fonts["tiny"], DARK_OLIVE, (box.x + 12, box.y + 24 + i * 18))


def draw_panel(surface, fonts, level, notice, aside_btn, mouse):
    panel = PANEL_BOX
    if notice:
        color = GOOD if notice["good"] else BAD
        pygame.draw.rect(surface, PANEL, panel)
        pygame.draw.rect(surface, color, panel, width=3)
        for i, line in enumerate(wrap_text(notice["text"], fonts["small"], panel.w - 40)[:3]):
            draw_text(surface, line, fonts["small"], DARK_OLIVE, (panel.x + 20, panel.y + 18 + i * 26))
        return
    pygame.draw.rect(surface, FADED, panel, width=3)
    draw_text(surface, "Inspect it, work out what is faulty, then choose the repair actions in order.",
              fonts["small"], DARK_OLIVE, (panel.centerx, panel.y + 24), "center")
    draw_text(surface, "[I] inspect   [1-4] mark faulty   [A-H] add or remove an action   [U] undo   [X] clear",
              fonts["tiny"], OLIVE_GREEN, (panel.centerx, panel.y + 54), "center")
    draw_text(surface, "[T] use a hint   [ENTER] done fixing   [ESC] menu", fonts["tiny"], OLIVE_GREEN,
              (panel.centerx, panel.y + 74), "center")
    if level.sent_back:
        draw_text(surface, f"Martha sent back (nothing to repair): {', '.join(level.sent_back[-3:])}", fonts["tiny"],
                  FADED, (panel.x + 20, panel.y + 92))
    if level.can_set_aside():
        aside_btn.draw(surface, fonts, mouse)


# ---- Martha's review -------------------------------------------------------------------------------------
def review_text(r):
    """The lines of text on Martha's review screen (kept separate so they can be tested)."""
    breakdown = [f"Order {r['scale_points']:+d}"]
    if r["wrong_count"]:
        breakdown.append(f"Wrong actions {r['wrong_points']:+d}")
    if r["part"]:
        if r["part"]["stored"]:
            breakdown.append(f"Used your recovered {r['part']['name'].lower()} {r['part_points']:+d}")
        else:
            breakdown.append(f"No {r['part']['name'].lower()} in storage, so a worn spare was used")
    if r["relic_bonus"]:
        breakdown.append(f"Relic bonus {r['relic_bonus']:+d}")

    diagnosis = f"Faulty: {', '.join(r['faults'])}."
    if not r["marked"]:
        diagnosis += " You did not mark any components."
    else:
        if r["found"]:
            diagnosis += f" You found: {', '.join(r['found'])}."
        if r["missed_faults"]:
            diagnosis += f" You missed: {', '.join(r['missed_faults'])}."
        if r["wrong_marks"]:
            diagnosis += f" Wrongly marked: {', '.join(r['wrong_marks'])}."

    why = ""
    if r["why_not"]:
        why = "Not needed: " + " ".join(f"{label} ({reason[0].lower() + reason[1:]})." for label, reason in r["why_not"])

    comment = r["comment"]
    if r["relic_retry"]:
        comment += " The relic is safe, so you can try again later."
    return {"summary": f"Correct: {r['correct']} of {r['total']} ({r['percent']}%)     TOTAL {r['points']:+d}",
            "breakdown": "     ".join(breakdown), "diagnosis": diagnosis, "why": why, "comment": comment}


ROW_STYLE = {"correct": ("OK", GOOD), "order": ("WRONG PLACE", GOLD), "missed": ("MISSED", BAD), "wrong": ("NOT NEEDED", BAD)}


def draw_rows(surface, fonts, x, y, rows, numbered):
    for n, row in enumerate(rows, start=1):
        word, color = ROW_STYLE[row["status"]]
        text = f"{n}. {row['label']}" if numbered else f"{n}. {row['label']}"
        draw_text(surface, text, fonts["small"], color, (x, y + (n - 1) * 24))
        draw_text(surface, word, fonts["tiny"], color, (x + 480, y + 4 + (n - 1) * 24), "topright")


def review_screen(window, fonts, clock, review):
    """Martha reviews the finished repair: the correct order next to the player's order, and the score."""
    text = review_text(review)
    color = GOOD if review["points"] > 0 else BAD

    def draw():
        draw_text(window, "MARTHA'S REVIEW", fonts["big"], OLIVE_GREEN, (WIDTH // 2, 48), "center")
        draw_text(window, review["name"] + (" (relic)" if review["relic"] else ""), fonts["mid"], DARK_OLIVE,
                  (WIDTH // 2, 92), "center")
        draw_text(window, "CORRECT ORDER", fonts["tiny"], OLIVE_GREEN, (70, 124))
        draw_text(window, "YOUR ORDER", fonts["tiny"], OLIVE_GREEN, (640, 124))
        draw_rows(window, fonts, 70, 148, review["required_rows"], True)
        draw_rows(window, fonts, 640, 148, review["player_rows"], True)
        draw_text(window, text["summary"], fonts["mid"], color, (WIDTH // 2, 372), "center")
        y = 402
        for line in wrap_text(text["breakdown"], fonts["small"], 1000)[:2]:
            draw_text(window, line, fonts["small"], DARK_OLIVE, (WIDTH // 2, y), "center")
            y += 22
        y += 6
        for line in wrap_text(text["diagnosis"], fonts["small"], 1000)[:2]:
            draw_text(window, line, fonts["small"], DARK_OLIVE, (WIDTH // 2, y), "center")
            y += 22
        y += 4
        for line in wrap_text(text["why"], fonts["tiny"], 1000)[:3]:
            draw_text(window, line, fonts["tiny"], FADED, (WIDTH // 2, y), "center")
            y += 16
        draw_text(window, text["comment"], fonts["small"], OLIVE_GREEN, (WIDTH // 2, 556), "center")
        draw_text(window, "Press SPACE to continue", fonts["tiny"], OLIVE_GREEN, (WIDTH // 2, 584), "center")

    _wait_for_key(window, clock, draw)


# ---- hints -----------------------------------------------------------------------------------------------------
def choice_screen(window, fonts, level, clock):
    """The Data drive hint lets the player choose what kind of help to get. Returns the choice or None."""
    options = level.usable_choices()
    keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key in keys and keys.index(event.key) < len(options):
                    return options[keys.index(event.key)]
        window.fill(BG_YELLOW)
        draw_text(window, "DATA DRIVE: CHOOSE YOUR HINT", fonts["mid"], GOLD, (WIDTH // 2, 100), "center")
        for i, kind in enumerate(options):
            draw_text(window, f"{i + 1}. {CHOICE_LABELS[kind]}", fonts["mid"], DARK_OLIVE, (WIDTH // 2, 190 + i * 46), "center")
        draw_text(window, "Press a number, or ESC to go back", fonts["small"], OLIVE_GREEN, (WIDTH // 2, HEIGHT - 60), "center")
        pygame.display.flip()
        clock.tick(60)


def hint_screen(window, fonts, level, clock):
    """Pick a Relic Wisdom hint from the pouch. Returns a notice dict for the bottom panel, or None."""
    keys = [pygame.K_1, pygame.K_2, pygame.K_3]
    while True:
        pouch = level.state["hint_pouch"]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_t) or not pouch:
                    return None
                if event.key in keys and keys.index(event.key) < len(pouch):
                    index = keys.index(event.key)
                    choice = None
                    if pouch[index]["type"] == "player_choice" and level.hint_usable("player_choice"):
                        choice = choice_screen(window, fonts, level, clock)
                        if choice is None:
                            continue
                    res = level.use_hint(index, choice)
                    return {"text": res["message"], "good": res["ok"]}
        window.fill(BG_YELLOW)
        draw_text(window, "RELIC WISDOM", fonts["big"], GOLD, (WIDTH // 2, 70), "center")
        if not pouch:
            draw_text(window, "Your hint pouch is empty. Restore relics to earn hints.", fonts["small"], DARK_OLIVE,
                      (WIDTH // 2, 200), "center")
        y = 150
        for i, hint in enumerate(pouch):
            usable = level.hint_usable(hint["type"])
            color = DARK_OLIVE if usable else FADED
            draw_text(window, f"{i + 1}. {hint['relic']}", fonts["mid"], GOLD if usable else FADED, (100, y))
            for line in wrap_text(hint["text"] + ("" if usable else "  (can't help with this repair)"), fonts["small"], 960)[:2]:
                y += 30
                draw_text(window, line, fonts["small"], color, (130, y))
            y += 46
        draw_text(window, "Press a number to use a hint (each can be used once), or ESC to go back", fonts["small"],
                  OLIVE_GREEN, (WIDTH // 2, HEIGHT - 60), "center")
        pygame.display.flip()
        clock.tick(60)


# ---- end screens -----------------------------------------------------------------------------------------------------
def complete_screen(window, fonts, level, clock):
    """Shown when the player reaches 400 points (Level 4)."""
    lines = [
        f"Repairs completed: {level.jobs_done}",
        f"Successful repairs: {level.successes}",
        f"Recovered parts used: {level.parts_used}",
        f"Relics restored: {level.relics_restored}",
        f"Hints used: {level.hints_used}",
    ]

    def draw():
        draw_text(window, "LEVEL 4 COMPLETE", fonts["big"], OLIVE_GREEN, (WIDTH // 2, 110), "center")
        for i, line in enumerate(lines):
            draw_text(window, line, fonts["mid"], DARK_OLIVE, (WIDTH // 2, 200 + i * 40), "center")
        draw_text(window, "You can plan a repair yourself. Next, Martha steps back completely.", fonts["small"],
                  OLIVE_GREEN, (WIDTH // 2, 200 + len(lines) * 40 + 30), "center")
        draw_text(window, "Press SPACE to return to the menu", fonts["small"], OLIVE_GREEN, (WIDTH // 2, HEIGHT - 60), "center")

    _wait_for_key(window, clock, draw)
    return "complete"


def dropback_screen(window, fonts, level, clock):
    """Shown when a job ends with the score below 300: the player goes back to Level 3."""
    def draw():
        draw_text(window, "SCORE TOO LOW", fonts["big"], BAD, (WIDTH // 2, 170), "center")
        draw_text(window, f"Your score fell below {DROPBACK_BELOW}.", fonts["mid"], DARK_OLIVE, (WIDTH // 2, 260), "center")
        draw_text(window, "Martha sends you back to guided repair. Earn the points again to return.", fonts["small"],
                  OLIVE_GREEN, (WIDTH // 2, 320), "center")
        draw_text(window, "Your parts, relics and hints are safe.", fonts["small"], OLIVE_GREEN, (WIDTH // 2, 355), "center")
        draw_text(window, "Press SPACE to continue", fonts["small"], OLIVE_GREEN, (WIDTH // 2, HEIGHT - 60), "center")

    _wait_for_key(window, clock, draw)
    return "dropback"


# ---- the level -----------------------------------------------------------------------------------------------------------
def run_level_4(window, state):
    """Play Level 4. Returns "complete" at 400 points, "dropback" below 300, or "menu" on ESC."""
    return run_repair_level(window, state, lambda st: Level4(st), "LEVEL 4 - ADVANCED REPAIR",
                            review_screen, complete_screen, dropback_screen)


def run_repair_level(window, state, make_level, title, show_review, show_complete, show_dropback):
    """The screen shared by Levels 4 and 5. Level 5 passes its own title, result screen and end screens."""
    clock = pygame.time.Clock()
    fonts = {
        "big": get_font(64),
        "name": get_font(38),
        "mid": get_font(32),
        "small": get_font(24),
        "tiny": get_font(20),
    }

    level = make_level(state)
    job = level.next_job()
    notice = None          # a message from a hint or from DONE FIXING, shown in the bottom panel
    card_x = CARD_START_X
    t = 0

    inspect_btn = Btn((45, 345, 230, 40), "INSPECT [I]")
    undo_btn = Btn((295, 345, 160, 40), "UNDO [U]")
    clear_btn = Btn((465, 345, 150, 40), "CLEAR [X]")
    hint_btn = Btn((625, 345, 200, 40), "HINT [T]")
    done_btn = Btn((915, 345, 240, 40), "DONE FIXING [ENTER]")
    aside_btn = Btn((910, 546, 190, 34), "SET ASIDE [S]")

    while True:
        dt = clock.tick(60)
        t += dt
        mouse = pygame.mouse.get_pos()
        ready = card_x == 0   # the job has arrived on the workbench

        # ---- input ------------------------------------------------------------
        action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_ESCAPE:
                    level.abandon()
                    return "menu"
                if key in ACTION_KEYS:
                    action = ("pick", ACTION_KEYS.index(key))
                elif key in MARK_KEYS:
                    action = ("mark", MARK_KEYS.index(key))
                elif key == pygame.K_i:
                    action = ("inspect",)
                elif key in (pygame.K_u, pygame.K_BACKSPACE):
                    action = ("undo",)
                elif key == pygame.K_x:
                    action = ("clear",)
                elif key == pygame.K_t:
                    action = ("hint",)
                elif key == pygame.K_RETURN:
                    action = ("done",)
                elif key == pygame.K_s:
                    action = ("aside",)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if inspect_btn.hit(pos):
                    action = ("inspect",)
                elif undo_btn.hit(pos):
                    action = ("undo",)
                elif clear_btn.hit(pos):
                    action = ("clear",)
                elif hint_btn.hit(pos):
                    action = ("hint",)
                elif done_btn.hit(pos):
                    action = ("done",)
                elif aside_btn.hit(pos) and level.can_set_aside() and not notice:
                    action = ("aside",)
                else:
                    for i in range(len(job["actions"])):
                        if action_rect(i).collidepoint(pos):
                            action = ("pick", i)
                    if level.inspected:
                        for i in range(len(job["findings"])):
                            if chip_rect(i).collidepoint(pos):
                                action = ("mark", i)

        if action and ready:
            kind = action[0]
            if kind == "pick":
                notice = None
                level.pick(action[1])
            elif kind == "mark":
                notice = None
                level.toggle_mark(action[1])
            elif kind == "inspect":
                notice = None
                level.inspect()
            elif kind == "undo":
                notice = None
                level.undo()
            elif kind == "clear":
                notice = None
                level.clear()
            elif kind == "hint":
                notice = hint_screen(window, fonts, level, clock)
            elif kind == "aside":
                if level.set_aside():
                    job = level.next_job()
                    notice = None
                    card_x = CARD_START_X
            elif kind == "done":
                review = level.done_fixing()
                if not review["ok"]:
                    notice = {"text": review["message"], "good": False}
                else:
                    show_review(window, fonts, clock, review)
                    if review["relic_reward"]:
                        relic_screen(window, fonts, level, clock, review["relic_reward"])
                    if level.complete:
                        return show_complete(window, fonts, level, clock)
                    if level.dropback:
                        return show_dropback(window, fonts, level, clock)
                    job = level.next_job()
                    notice = None
                    card_x = CARD_START_X

        # ---- update -----------------------------------------------------------
        if card_x != 0:
            card_x += (0 - card_x) * min(1.0, dt / 130)
            if abs(card_x) < 1:
                card_x = 0

        # ---- draw -------------------------------------------------------------
        window.fill(BG_YELLOW)
        draw_top_bar(window, fonts, level.score, title, level.START)

        bench = pygame.Rect(40, 318, 240, 14)
        pygame.draw.rect(window, DARK_OLIVE, bench)
        card = pygame.Rect(0, 0, 230, 215)
        card.center = (160 + int(card_x), 202)
        draw_job_card(window, card, job, t, fonts)

        if ready:
            draw_martha(window, fonts, job, level.GUIDED)
            draw_findings(window, fonts, level)
            for i, act in enumerate(job["actions"]):
                rect = action_rect(i)
                order = level.sequence.index(i) + 1 if i in level.sequence else None
                draw_action(window, fonts, rect, LETTERS[i], act["label"], order, level.tags.get(i),
                            i in level.trapped, rect.collidepoint(mouse))

            inspect_btn.draw(window, fonts, mouse, enabled=not level.inspected)
            undo_btn.draw(window, fonts, mouse, enabled=bool(level.sequence))
            clear_btn.draw(window, fonts, mouse, enabled=bool(level.sequence))
            hint_btn.label = f"HINT [T] x{len(level.state['hint_pouch'])}"
            hint_btn.draw(window, fonts, mouse, enabled=bool(level.state["hint_pouch"]))
            done_btn.draw(window, fonts, mouse)

            draw_sequence(window, fonts, level)
            draw_parts_box(window, fonts, level.state["components"], PARTS_BOX)
            draw_panel(window, fonts, level, notice, aside_btn, mouse)

        pygame.display.flip()