"""Level 2 - Material Recovery (the pygame screen). The rules live in level2_logic.py."""
import math
import sys
from collections import Counter

import pygame

from level1 import (BAD, BG_YELLOW, CARD_START_X, DARK_OLIVE, FADED, GOLD, GOOD, HEIGHT, LIGHT_GOLD,
                    OLIVE_GREEN, PANEL, WIDTH, Btn, draw_gear, draw_text, draw_top_bar, item_image,
                    wrap_text)
from level2_logic import DROPBACK_BELOW, LEVEL_START, Level2
from settings import get_font

KEYS = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]
CHIP_W, CHIP_H = 350, 62


def chip_rect(i):
    """Part buttons sit in two columns to the right of the object."""
    return pygame.Rect(420 + (i % 2) * 370, 105 + (i // 2) * 76, CHIP_W, CHIP_H)


def draw_object(surface, rect, obj, t, fonts):
    pygame.draw.rect(surface, PANEL, rect)
    accent = OLIVE_GREEN
    if obj["relic"]:
        pulse = (math.sin(t / 250) + 1) / 2
        accent = tuple(int(GOLD[i] + (LIGHT_GOLD[i] - GOLD[i]) * pulse) for i in range(3))
        pygame.draw.rect(surface, accent, rect.inflate(12, 12), width=3)
        pygame.draw.rect(surface, accent, rect, width=4)
        badge = (rect.right - 30, rect.top + 30)
        pygame.draw.circle(surface, GOLD, badge, 17)
        draw_text(surface, "?", fonts["mid"], DARK_OLIVE, badge, "center")
    else:
        pygame.draw.rect(surface, OLIVE_GREEN, rect, width=4)

    draw_text(surface, obj["name"], fonts["name"], DARK_OLIVE, (rect.centerx, rect.top + 30), "center")

    picture = item_image(obj["name"])
    center = (rect.centerx, rect.top + 115)
    if picture:
        surface.blit(picture, picture.get_rect(center=center))
    else:
        draw_gear(surface, center, 30, accent)

    source = "From your Recover pile" if obj["from_pile"] else "New shipment from the scavengers"
    draw_text(surface, source, fonts["small"], OLIVE_GREEN, (rect.centerx, rect.bottom - 26), "center")


def draw_chip(surface, fonts, rect, number, part, selected, show_note, revealed, hover):
    """One part of the object. Click it (or press its number) to select it for recovery."""
    if revealed:
        border = GOOD if part["good"] else BAD
    elif selected or hover:
        border = DARK_OLIVE
    else:
        border = OLIVE_GREEN
    pygame.draw.rect(surface, PANEL if (selected or revealed) else BG_YELLOW, rect)
    pygame.draw.rect(surface, border, rect, width=5 if selected else 3)

    mark = "[X]" if selected else "[ ]"
    draw_text(surface, f"{mark} {number}. {part['name']}", fonts["mid"], DARK_OLIVE, (rect.x + 12, rect.y + 7))
    if show_note:
        draw_text(surface, part["note"], fonts["small"], DARK_OLIVE, (rect.x + 14, rect.y + 37))
    else:
        draw_text(surface, "Inspect to see its condition", fonts["small"], FADED, (rect.x + 14, rect.y + 37))
    if revealed:
        label = "USABLE" if part["good"] else "DAMAGED"
        draw_text(surface, label, fonts["tiny"], border, (rect.right - 10, rect.y + 9), "topright")


def draw_storage(surface, fonts, components):
    """The parts storage: what the player has recovered so far (used in the repair levels)."""
    box = pygame.Rect(45, 392, 1110, 76)
    pygame.draw.rect(surface, FADED, box, width=3)
    draw_text(surface, "PARTS STORAGE", fonts["tiny"], OLIVE_GREEN, (box.x + 12, box.y + 8))
    if components:
        counts = Counter(c["name"] for c in components)
        text = "   ".join(f"{name} x{n}" for name, n in sorted(counts.items()))
    else:
        text = "Empty. Recovered parts are kept here for the repair levels."
    lines = wrap_text(text, fonts["small"], box.w - 24)
    if len(lines) > 2:
        lines = [lines[0], lines[1].rstrip() + " ..."]
    for i, line in enumerate(lines):
        draw_text(surface, line, fonts["small"], DARK_OLIVE, (box.x + 12, box.y + 30 + i * 22))


def draw_feedback(surface, fonts, result, next_btn, mouse):
    panel = pygame.Rect(80, 478, 1040, 110)
    color = GOOD if result["good"] else BAD
    pygame.draw.rect(surface, PANEL, panel)
    pygame.draw.rect(surface, color, panel, width=3)

    draw_text(surface, f"{result['headline']}  {result['points']:+d}", fonts["mid"], color, (panel.x + 20, panel.y + 10))
    next_btn.draw(surface, fonts, mouse)

    lines = wrap_text(result["message"], fonts["small"], panel.w - 40)
    for i, line in enumerate(lines[:3]):
        draw_text(surface, line, fonts["small"], DARK_OLIVE, (panel.x + 20, panel.y + 46 + i * 21))


def draw_hint(surface, fonts):
    panel = pygame.Rect(80, 478, 1040, 110)
    pygame.draw.rect(surface, FADED, panel, width=3)
    draw_text(surface, "Select the parts that can still be used, then recover them.", fonts["small"], DARK_OLIVE,
              (panel.centerx, panel.y + 36), "center")
    draw_text(surface, "[1-5] select     [I] inspect     [ENTER] recover     [N] nothing usable     [ESC] menu",
              fonts["small"], OLIVE_GREEN, (panel.centerx, panel.y + 70), "center")


def _wait_for_key(window, clock, draw):
    """Show a full-screen message until the player presses SPACE, ENTER or ESC (or clicks)."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return
        window.fill(BG_YELLOW)
        draw()
        pygame.display.flip()
        clock.tick(60)


def complete_screen(window, fonts, level, clock):
    """Shown when the player reaches 200 points."""
    stored = len(level.state["components"])
    lines = [
        f"Objects taken apart: {level.objects_done}",
        f"Parts recovered: {level.parts_recovered}",
        f"Damaged parts picked by mistake: {level.wrong_picks}",
        f"Usable parts missed: {level.parts_missed}",
        f"Parts now in storage: {stored}",
    ]

    def draw():
        draw_text(window, "LEVEL 2 COMPLETE", fonts["big"], OLIVE_GREEN, (WIDTH // 2, 110), "center")
        for i, line in enumerate(lines):
            draw_text(window, line, fonts["mid"], DARK_OLIVE, (WIDTH // 2, 200 + i * 40), "center")
        draw_text(window, "Martha's shelves are stocked. Now it's time to learn to repair.", fonts["small"],
                  OLIVE_GREEN, (WIDTH // 2, 200 + len(lines) * 40 + 30), "center")
        draw_text(window, "Press SPACE to return to the menu", fonts["small"], OLIVE_GREEN,
                  (WIDTH // 2, HEIGHT - 60), "center")

    _wait_for_key(window, clock, draw)
    return "complete"


def dropback_screen(window, fonts, level, clock):
    """Shown when the score falls below 100: the player goes back to Level 1."""
    def draw():
        draw_text(window, "SCORE TOO LOW", fonts["big"], BAD, (WIDTH // 2, 170), "center")
        draw_text(window, f"Your score fell below {DROPBACK_BELOW}.", fonts["mid"], DARK_OLIVE,
                  (WIDTH // 2, 260), "center")
        draw_text(window, "Martha sends you back to sorting. Earn the points again to return.", fonts["small"],
                  OLIVE_GREEN, (WIDTH // 2, 320), "center")
        draw_text(window, "The parts you recovered are still in storage.", fonts["small"], OLIVE_GREEN,
                  (WIDTH // 2, 355), "center")
        draw_text(window, "Press SPACE to continue", fonts["small"], OLIVE_GREEN, (WIDTH // 2, HEIGHT - 60), "center")

    _wait_for_key(window, clock, draw)
    return "dropback"


def run_level_2(window, state):
    """Play Level 2. Returns "complete" at 200 points, "dropback" below 100, or "menu" on ESC."""
    clock = pygame.time.Clock()
    fonts = {
        "big": get_font(64),
        "name": get_font(38),
        "mid": get_font(32),
        "small": get_font(24),
        "tiny": get_font(20),
    }

    level = Level2(state)
    obj = level.next_object()
    inspected = False
    result = None
    card_x = CARD_START_X
    t = 0

    inspect_btn = Btn((420, 345, 200, 40), "INSPECT [I]")
    recover_btn = Btn((640, 345, 240, 40), "RECOVER [ENTER]")
    nothing_btn = Btn((900, 345, 240, 40), "NOTHING USABLE [N]")
    next_btn = Btn((910, 484, 190, 34), "NEXT [SPACE]")

    while True:
        dt = clock.tick(60)
        t += dt
        mouse = pygame.mouse.get_pos()
        ready = card_x == 0   # the object has arrived on the workbench

        # ---- input ------------------------------------------------------------
        action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if result is None:
                    if event.key == pygame.K_i:
                        action = ("inspect",)
                    elif event.key in KEYS:
                        action = ("toggle", KEYS.index(event.key))
                    elif event.key == pygame.K_RETURN:
                        action = ("confirm",)
                    elif event.key == pygame.K_n:
                        action = ("nothing",)
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    action = ("next",)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if result is None:
                    if inspect_btn.hit(event.pos):
                        action = ("inspect",)
                    elif recover_btn.hit(event.pos):
                        action = ("confirm",)
                    elif nothing_btn.hit(event.pos):
                        action = ("nothing",)
                    for i in range(len(obj["parts"])):
                        if chip_rect(i).collidepoint(event.pos):
                            action = ("toggle", i)
                elif next_btn.hit(event.pos):
                    action = ("next",)

        if action and ready:
            kind = action[0]
            if result is None:
                if kind == "inspect":
                    inspected = True
                elif kind == "toggle":
                    level.toggle(action[1])
                elif kind == "confirm":
                    result = level.confirm()
                    inspected = True
                elif kind == "nothing":
                    result = level.confirm(set())
                    inspected = True
            elif kind == "next":
                if level.complete:
                    return complete_screen(window, fonts, level, clock)
                if level.dropback:
                    return dropback_screen(window, fonts, level, clock)
                obj = level.next_object()
                inspected = False
                result = None
                card_x = CARD_START_X

        # ---- update -----------------------------------------------------------
        if card_x != 0:
            card_x += (0 - card_x) * min(1.0, dt / 130)
            if abs(card_x) < 1:
                card_x = 0

        # ---- draw -------------------------------------------------------------
        window.fill(BG_YELLOW)
        draw_top_bar(window, fonts, level.score, "LEVEL 2 - MATERIAL RECOVERY", LEVEL_START)

        bench = pygame.Rect(40, 330, 340, 14)
        pygame.draw.rect(window, DARK_OLIVE, bench)
        card = pygame.Rect(0, 0, 300, 235)
        card.center = (210 + int(card_x), 212)
        draw_object(window, card, obj, t, fonts)

        if ready:
            revealed = result is not None
            for i, part in enumerate(obj["parts"]):
                rect = chip_rect(i)
                draw_chip(window, fonts, rect, i + 1, part, i in level.selected,
                          inspected or revealed, revealed, (not revealed) and rect.collidepoint(mouse))

        active = result is None and ready
        inspect_btn.draw(window, fonts, mouse, enabled=active)
        recover_btn.draw(window, fonts, mouse, enabled=active)
        nothing_btn.draw(window, fonts, mouse, enabled=active)

        draw_storage(window, fonts, level.state["components"])

        if result is None:
            draw_hint(window, fonts)
        else:
            draw_feedback(window, fonts, result, next_btn, mouse)

        pygame.display.flip()