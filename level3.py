"""Level 3 - Learning to Repair (the pygame screen). The rules live in level3_logic.py."""
import math
import sys
from collections import Counter

import pygame

from level1 import (BAD, BG_YELLOW, CARD_START_X, DARK_OLIVE, FADED, GOLD, GOOD, HEIGHT, LIGHT_GOLD,
                    OLIVE_GREEN, PANEL, WIDTH, Btn, draw_gear, draw_text, draw_top_bar, fit_font, item_image,
                    wrap_text)
from level2 import _wait_for_key
from level3_logic import (DROPBACK_BELOW, HINT_POUCH_MAX, LEVEL_START, RELIC_BONUS, Level3)
from settings import get_font

ACTION_KEYS = [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f]
LETTERS = "ABCDEF"

MARTHA_BOX = pygame.Rect(420, 100, 720, 104)


def action_rect(i):
    """The six action buttons sit in two rows of three under Martha's box."""
    return pygame.Rect(420 + (i % 3) * 245, 212 + (i // 3) * 64, 230, 56)


def draw_fit(surface, text, fonts, color, rect, keys=("small", "tiny")):
    """Draw text centred in `rect`: the biggest font that fits on one line, else two wrapped lines."""
    width = rect.w - 20
    for key in keys:
        if fonts[key].size(text)[0] <= width:
            draw_text(surface, text, fonts[key], color, rect.center, "center")
            return
    font = fonts[keys[-1]]
    lines = wrap_text(text, font, width)[:2]
    line_h = font.size("A")[1] + 2
    top = rect.centery - (line_h * len(lines)) // 2
    for i, line in enumerate(lines):
        draw_text(surface, line, font, color, (rect.centerx, top + i * line_h), "midtop")


def draw_job_card(surface, rect, job, t, fonts):
    pygame.draw.rect(surface, PANEL, rect)
    accent = OLIVE_GREEN
    if job["relic"]:
        pulse = (math.sin(t / 250) + 1) / 2
        accent = tuple(int(GOLD[i] + (LIGHT_GOLD[i] - GOLD[i]) * pulse) for i in range(3))
        pygame.draw.rect(surface, accent, rect.inflate(12, 12), width=3)
        pygame.draw.rect(surface, accent, rect, width=4)
        badge = (rect.right - 34, rect.top + 80)   # beside the picture, clear of the name
        pygame.draw.circle(surface, GOLD, badge, 17)
        draw_text(surface, "?", fonts["mid"], DARK_OLIVE, badge, "center")
    else:
        pygame.draw.rect(surface, OLIVE_GREEN, rect, width=4)

    name_font = fit_font(fonts, ("name", "mid", "small"), job["name"], rect.w - 24)
    draw_text(surface, job["name"], name_font, DARK_OLIVE, (rect.centerx, rect.top + 30), "center")
    picture = item_image(job["name"])
    center = (rect.centerx, rect.top + 115)
    if picture:
        surface.blit(picture, picture.get_rect(center=center))
    else:
        draw_gear(surface, center, 30, accent)

    if job["relic"]:
        label = "RELIC JOB"
    elif job["from_queue"]:
        label = "Sent to Martha's workshop"
    else:
        label = "New job for the workshop"
    draw_text(surface, label, fonts["small"], GOLD if job["relic"] else OLIVE_GREEN,
              (rect.centerx, rect.bottom - 26), "center")


def draw_martha(surface, fonts, level):
    box = MARTHA_BOX
    pygame.draw.rect(surface, PANEL, box)
    pygame.draw.rect(surface, OLIVE_GREEN, box, width=3)
    draw_text(surface, "MARTHA", fonts["tiny"], OLIVE_GREEN, (box.x + 14, box.y + 9))

    total = len(level.job["steps"])
    if level.finished:
        text = "Good work. That one is fixed."
    elif level.all_steps_done:
        text = "That's everything. Press DONE FIXING and we'll check it over."
    else:
        text = level.current_step["say"]
        draw_text(surface, f"STEP {level.step + 1} OF {total}", fonts["tiny"], OLIVE_GREEN,
                  (box.right - 14, box.y + 9), "topright")

    for i, line in enumerate(wrap_text(text, fonts["small"], box.w - 28)[:3]):
        draw_text(surface, line, fonts["small"], DARK_OLIVE, (box.x + 14, box.y + 32 + i * 22))


def draw_action(surface, fonts, rect, letter, label, state, hover):
    """state: "open", "done", "wrong" or "off"."""
    if state == "done":
        color = GOOD
    elif state == "wrong":
        color = BAD
    elif state == "off":
        color = FADED
    else:
        color = DARK_OLIVE if hover else OLIVE_GREEN
    if hover and state == "open":
        pygame.draw.rect(surface, PANEL, rect)
    pygame.draw.rect(surface, color, rect, width=3)
    draw_fit(surface, f"{letter}. {label}", fonts, color, rect)


def draw_parts_box(surface, fonts, components, box):
    pygame.draw.rect(surface, FADED, box, width=3)
    draw_text(surface, "PARTS STORAGE", fonts["tiny"], OLIVE_GREEN, (box.x + 12, box.y + 8))
    if components:
        counts = Counter(c["name"] for c in components)
        text = "   ".join(f"{name} x{n}" for name, n in sorted(counts.items()))
    else:
        text = "Empty. Recover parts in Level 2 to use them here."
    lines = wrap_text(text, fonts["small"], box.w - 24)
    if len(lines) > 2:
        lines = [lines[0], lines[1].rstrip() + " ..."]
    for i, line in enumerate(lines):
        draw_text(surface, line, fonts["small"], DARK_OLIVE, (box.x + 12, box.y + 30 + i * 22))


def draw_hint_box(surface, fonts, hints, box):
    pygame.draw.rect(surface, FADED, box, width=3)
    draw_text(surface, f"HINT POUCH  {len(hints)}/{HINT_POUCH_MAX}", fonts["tiny"], OLIVE_GREEN, (box.x + 12, box.y + 8))
    text = ", ".join(h["relic"] for h in hints) if hints else "Restore relics to earn hints."
    for i, line in enumerate(wrap_text(text, fonts["small"], box.w - 24)[:2]):
        draw_text(surface, line, fonts["small"], DARK_OLIVE, (box.x + 12, box.y + 30 + i * 22))


def draw_step_info(surface, fonts, level, rect):
    """Between the two buttons: which step we are on, or which stored part this step needs."""
    if level.finished:
        return
    step = level.current_step
    if step is None:
        return
    if step["part"]:
        have = level.parts_in_storage(step["part"])
        text = f"Needs: {step['part']} ({'in storage x' + str(have) if have else 'none, worn spare'})"
        color = GOOD if have else FADED
    else:
        text = f"Step {level.step + 1} of {len(level.job['steps'])}"
        color = OLIVE_GREEN
    draw_fit(surface, text, fonts, color, rect, keys=("tiny",))


def draw_panel(surface, fonts, level, last, job_result, next_btn, mouse):
    panel = pygame.Rect(80, 478, 1040, 110)
    if job_result is None and last is None:
        pygame.draw.rect(surface, FADED, panel, width=3)
        if level.job["relic"] and level.can_set_aside():
            first = f"A relic job: +{RELIC_BONUS} bonus, a story fragment and a hint. Take it on, or set it aside."
            keys = "[A-F] choose     [ENTER] done fixing     [S] set aside     [ESC] menu"
        else:
            first = "Follow Martha's instructions, one step at a time."
            keys = "[A-F] choose an action     [ENTER] done fixing     [ESC] menu"
        draw_text(surface, first, fonts["small"], DARK_OLIVE, (panel.centerx, panel.y + 28), "center")
        draw_text(surface, keys, fonts["small"], OLIVE_GREEN, (panel.centerx, panel.y + 58), "center")
        if level.sent_back:
            names = ", ".join(level.sent_back[-3:])
            draw_text(surface, f"Martha sent back (nothing to repair): {names}", fonts["tiny"], FADED,
                      (panel.centerx, panel.y + 88), "center")
        return

    res = job_result or last
    color = GOOD if res["good"] else BAD
    pygame.draw.rect(surface, PANEL, panel)
    pygame.draw.rect(surface, color, panel, width=3)
    points = f"  {res['points']:+d}" if res["points"] else ""
    draw_text(surface, f"{res['headline']}{points}", fonts["mid"], color, (panel.x + 20, panel.y + 10))
    for i, line in enumerate(wrap_text(res["message"], fonts["small"], panel.w - 40)[:3]):
        draw_text(surface, line, fonts["small"], DARK_OLIVE, (panel.x + 20, panel.y + 46 + i * 21))
    if job_result is not None:
        next_btn.draw(surface, fonts, mouse)


def relic_screen(window, fonts, level, clock, reward):
    """Story fragment and Relic Wisdom shown after a relic is restored."""
    story_lines = wrap_text(reward["story"], fonts["small"], 900)
    hint_lines = wrap_text("Relic Wisdom: " + reward["hint"], fonts["small"], 900)

    def draw():
        draw_text(window, "RELIC RESTORED", fonts["big"], GOLD, (WIDTH // 2, 80), "center")
        draw_text(window, reward["name"], fonts["name"], DARK_OLIVE, (WIDTH // 2, 140), "center")
        y = 195
        for line in story_lines:
            draw_text(window, line, fonts["small"], DARK_OLIVE, (WIDTH // 2, y), "center")
            y += 26
        y += 22
        for line in hint_lines:
            draw_text(window, line, fonts["small"], GOLD, (WIDTH // 2, y), "center")
            y += 26
        if reward["replaced"]:
            draw_text(window, f"Your hint pouch was full, so the {reward['replaced']} hint faded away.",
                      fonts["tiny"], FADED, (WIDTH // 2, y + 8), "center")
            y += 26
        draw_text(window, f"Relic Collection: {reward['collection_count']} of {reward['collection_total']}",
                  fonts["small"], OLIVE_GREEN, (WIDTH // 2, y + 24), "center")
        draw_text(window, "Press SPACE to continue", fonts["small"], OLIVE_GREEN, (WIDTH // 2, HEIGHT - 50), "center")

    _wait_for_key(window, clock, draw)


def complete_screen(window, fonts, level, clock):
    """Shown when the player reaches 300 points."""
    lines = [
        f"Repairs completed: {level.jobs_done}",
        f"Mistakes made: {level.mistakes}",
        f"Recovered parts used: {level.parts_used}",
        f"Relics restored: {level.relics_restored}",
    ]

    def draw():
        draw_text(window, "LEVEL 3 COMPLETE", fonts["big"], OLIVE_GREEN, (WIDTH // 2, 110), "center")
        for i, line in enumerate(lines):
            draw_text(window, line, fonts["mid"], DARK_OLIVE, (WIDTH // 2, 200 + i * 40), "center")
        draw_text(window, "You can repair with Martha's guidance. Next, she gives you less help.", fonts["small"],
                  OLIVE_GREEN, (WIDTH // 2, 200 + len(lines) * 40 + 30), "center")
        draw_text(window, "Press SPACE to return to the menu", fonts["small"], OLIVE_GREEN,
                  (WIDTH // 2, HEIGHT - 60), "center")

    _wait_for_key(window, clock, draw)
    return "complete"


def dropback_screen(window, fonts, level, clock):
    """Shown when a job ends with the score below 200: the player goes back to Level 2."""
    def draw():
        draw_text(window, "SCORE TOO LOW", fonts["big"], BAD, (WIDTH // 2, 170), "center")
        draw_text(window, f"Your score fell below {DROPBACK_BELOW}.", fonts["mid"], DARK_OLIVE,
                  (WIDTH // 2, 260), "center")
        draw_text(window, "Martha sends you back to material recovery. Earn the points again to return.",
                  fonts["small"], OLIVE_GREEN, (WIDTH // 2, 320), "center")
        draw_text(window, "Your parts and relics are safe.", fonts["small"], OLIVE_GREEN, (WIDTH // 2, 355), "center")
        draw_text(window, "Press SPACE to continue", fonts["small"], OLIVE_GREEN, (WIDTH // 2, HEIGHT - 60), "center")

    _wait_for_key(window, clock, draw)
    return "dropback"


def run_level_3(window, state):
    """Play Level 3. Returns "complete" at 300 points, "dropback" below 200, or "menu" on ESC."""
    clock = pygame.time.Clock()
    fonts = {
        "big": get_font(64),
        "name": get_font(38),
        "mid": get_font(32),
        "small": get_font(24),
        "tiny": get_font(20),
    }

    level = Level3(state)
    job = level.next_job()
    last = None            # result of the latest action, shown in the bottom panel
    wrong_index = None     # the action the player just got wrong (drawn red)
    job_result = None      # set when DONE FIXING succeeds
    card_x = CARD_START_X
    t = 0

    aside_btn = Btn((420, 345, 200, 40), "SET ASIDE [S]")
    done_btn = Btn((900, 345, 240, 40), "DONE FIXING [ENTER]")
    next_btn = Btn((910, 484, 190, 34), "NEXT [SPACE]")
    info_rect = pygame.Rect(630, 345, 260, 40)

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
                if event.key == pygame.K_ESCAPE:
                    level.abandon()
                    return "menu"
                if job_result is None:
                    if event.key in ACTION_KEYS:
                        action = ("choose", ACTION_KEYS.index(event.key))
                    elif event.key == pygame.K_RETURN:
                        action = ("done",)
                    elif event.key == pygame.K_s:
                        action = ("aside",)
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    action = ("next",)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if job_result is None:
                    if done_btn.hit(event.pos):
                        action = ("done",)
                    elif aside_btn.hit(event.pos) and job["relic"]:
                        action = ("aside",)
                    for i in range(len(job["actions"])):
                        if action_rect(i).collidepoint(event.pos):
                            action = ("choose", i)
                elif next_btn.hit(event.pos):
                    action = ("next",)

        if action and ready:
            kind = action[0]
            if job_result is None:
                if kind == "choose":
                    res = level.choose(action[1])
                    if res["kind"] != "ignored":
                        last = res
                        wrong_index = action[1] if res["kind"] in ("wrong", "early") else None
                elif kind == "done":
                    res = level.done_fixing()
                    if res["ok"]:
                        job_result = res
                        wrong_index = None
                    else:
                        last = res
                elif kind == "aside":
                    if level.set_aside():
                        job = level.next_job()
                        last, wrong_index = None, None
                        card_x = CARD_START_X
            elif kind == "next":
                if job_result["relic_reward"]:
                    relic_screen(window, fonts, level, clock, job_result["relic_reward"])
                if level.complete:
                    return complete_screen(window, fonts, level, clock)
                if level.dropback:
                    return dropback_screen(window, fonts, level, clock)
                job = level.next_job()
                last, wrong_index, job_result = None, None, None
                card_x = CARD_START_X

        # ---- update -----------------------------------------------------------
        if card_x != 0:
            card_x += (0 - card_x) * min(1.0, dt / 130)
            if abs(card_x) < 1:
                card_x = 0

        # ---- draw -------------------------------------------------------------
        window.fill(BG_YELLOW)
        draw_top_bar(window, fonts, level.score, "LEVEL 3 - LEARNING TO REPAIR", LEVEL_START)

        bench = pygame.Rect(40, 330, 340, 14)
        pygame.draw.rect(window, DARK_OLIVE, bench)
        card = pygame.Rect(0, 0, 300, 235)
        card.center = (210 + int(card_x), 212)
        draw_job_card(window, card, job, t, fonts)

        active = job_result is None and ready
        if ready:
            draw_martha(window, fonts, level)
            for i, act in enumerate(job["actions"]):
                rect = action_rect(i)
                if i in level.done:
                    state_name = "done"
                elif i == wrong_index:
                    state_name = "wrong"
                elif not active or level.all_steps_done:
                    state_name = "off"
                else:
                    state_name = "open"
                draw_action(window, fonts, rect, LETTERS[i], act["label"], state_name,
                            active and rect.collidepoint(mouse))
            draw_step_info(window, fonts, level, info_rect)
            if job["relic"] and level.can_set_aside():
                aside_btn.draw(window, fonts, mouse, enabled=active)
            done_btn.draw(window, fonts, mouse, enabled=active)

        draw_parts_box(window, fonts, level.state["components"], pygame.Rect(45, 392, 780, 76))
        draw_hint_box(window, fonts, level.state["hint_pouch"], pygame.Rect(840, 392, 315, 76))

        if ready:
            draw_panel(window, fonts, level, last, job_result, next_btn, mouse)

        pygame.display.flip()