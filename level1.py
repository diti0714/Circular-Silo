"""Level 1 - Sorting (the pygame screen). The rules live in level1_logic.py."""
import math
import os
import sys

import pygame

from level1_logic import DECISIONS, DESTINATIONS, TARGET, Level1, image_filename
from settings import ITEM_IMAGE_DIR, get_font

WIDTH, HEIGHT = 1200, 600

# Same palette as the main menu, plus a few feedback colours
OLIVE_GREEN = (107, 114, 60)
DARK_OLIVE = (70, 75, 40)
BG_YELLOW = (226, 219, 149)
PANEL = (238, 233, 176)
FADED = (165, 165, 115)
GOOD = (60, 120, 60)
BAD = (160, 60, 50)
GOLD = (196, 150, 30)
LIGHT_GOLD = (240, 205, 90)

KEYS = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]

CARD_START_X = -700.0   # the card slides in from the left along the conveyor belt

IMAGE_BOX = 80          # object pictures are fitted inside an 80 x 80 area on the card
_image_cache = {}


def item_image(name):
    """The pixel picture for an object, or None if there isn't one (the gear is drawn instead)."""
    if name not in _image_cache:
        image = None
        path = os.path.join(ITEM_IMAGE_DIR, image_filename(name))
        if os.path.exists(path):
            try:
                image = pygame.image.load(path).convert_alpha()
                w, h = image.get_size()
                longest = max(w, h)
                if longest <= IMAGE_BOX:
                    zoom = IMAGE_BOX // longest   # whole-number zoom keeps the pixels sharp
                    image = pygame.transform.scale(image, (w * zoom, h * zoom))
                else:
                    ratio = IMAGE_BOX / longest
                    image = pygame.transform.scale(image, (round(w * ratio), round(h * ratio)))
            except pygame.error:
                image = None
        _image_cache[name] = image
    return _image_cache[name]


def draw_text(surface, text, font, color, pos, anchor="topleft"):
    image = font.render(text, False, color)
    rect = image.get_rect(**{anchor: pos})
    surface.blit(image, rect)
    return rect


def wrap_text(text, font, max_width):
    lines, line = [], ""
    for word in text.split():
        test = word if not line else line + " " + word
        if line and font.size(test)[0] > max_width:
            lines.append(line)
            line = word
        else:
            line = test
    if line:
        lines.append(line)
    return lines


class Btn:
    """A pixel-style button in the same look as the main menu."""

    def __init__(self, rect, label, sub=""):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.sub = sub

    def hit(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surface, fonts, mouse, enabled=True):
        hover = enabled and self.rect.collidepoint(mouse)
        color = DARK_OLIVE if hover else (OLIVE_GREEN if enabled else FADED)
        if hover:
            pygame.draw.rect(surface, PANEL, self.rect)
        pygame.draw.rect(surface, color, self.rect, width=3)
        cx, cy = self.rect.center
        if self.sub:
            draw_text(surface, self.label, fonts["mid"], color, (cx, cy - 11), "center")
            draw_text(surface, self.sub, fonts["tiny"], color, (cx, cy + 16), "center")
        else:
            draw_text(surface, self.label, fonts["mid"], color, (cx, cy), "center")


def draw_gear(surface, center, radius, color):
    cx, cy = center
    for i in range(8):
        angle = math.radians(i * 45)
        tooth = (int(cx + math.cos(angle) * radius), int(cy + math.sin(angle) * radius))
        pygame.draw.circle(surface, color, tooth, radius // 4)
    pygame.draw.circle(surface, color, (cx, cy), int(radius * 0.8))
    pygame.draw.circle(surface, PANEL, (cx, cy), radius // 3)


def draw_card(surface, rect, obj, inspected, t, fonts):
    pygame.draw.rect(surface, PANEL, rect)
    accent = OLIVE_GREEN

    if obj["relic"]:
        # relics glow: the gold border pulses
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
    picture_center = (rect.centerx, rect.top + 90)
    if picture:
        surface.blit(picture, picture.get_rect(center=picture_center))
    else:
        draw_gear(surface, picture_center, 26, accent)

    if inspected:
        for i, clue in enumerate(obj["clues"]):
            color = GOLD if (obj["relic"] and i == 0) else DARK_OLIVE
            draw_text(surface, clue, fonts["small"], color, (rect.centerx, rect.top + 140 + i * 22), "center")
    else:
        draw_text(surface, "Not inspected yet", fonts["small"], FADED, (rect.centerx, rect.top + 150), "center")


def draw_top_bar(surface, fonts, score, title="LEVEL 1 - SORTING", base=0):
    """`base` is the score where this level starts, so the bar shows progress through the level."""
    gained = max(0, score - base)
    draw_text(surface, title, fonts["mid"], OLIVE_GREEN, (30, 24))
    bar = pygame.Rect(420, 22, 360, 26)
    pygame.draw.rect(surface, OLIVE_GREEN, bar, width=3)
    fraction = max(0.0, min(1.0, gained / TARGET))
    fill = pygame.Rect(bar.x + 5, bar.y + 5, int((bar.w - 10) * fraction), bar.h - 10)
    if fill.w > 0:
        pygame.draw.rect(surface, OLIVE_GREEN, fill)
    draw_text(surface, f"{gained} / {TARGET}", fonts["tiny"], OLIVE_GREEN, (bar.centerx, bar.bottom + 4), "midtop")
    draw_text(surface, f"SCORE: {score}", fonts["mid"], OLIVE_GREEN, (WIDTH - 30, 24), "topright")


def draw_feedback(surface, fonts, result, next_btn, mouse):
    panel = pygame.Rect(80, 488, 1040, 94)
    color = GOOD if result["correct"] else BAD
    pygame.draw.rect(surface, PANEL, panel)
    pygame.draw.rect(surface, color, panel, width=3)

    headline = f"{result['headline']}  {result['points']:+d}"
    head_rect = draw_text(surface, headline, fonts["mid"], color, (panel.x + 20, panel.y + 10))
    draw_text(surface, f"Sent to {result['destination']}", fonts["small"], DARK_OLIVE,
              (head_rect.right + 24, panel.y + 15))
    next_btn.draw(surface, fonts, mouse)

    lines = wrap_text(result["message"], fonts["small"], panel.w - 40)
    for i, line in enumerate(lines[:2]):
        draw_text(surface, line, fonts["small"], DARK_OLIVE, (panel.x + 20, panel.y + 46 + i * 22))


def draw_hint(surface, fonts):
    panel = pygame.Rect(80, 488, 1040, 94)
    pygame.draw.rect(surface, FADED, panel, width=3)
    draw_text(surface, "Inspect the object, then choose where it goes.", fonts["small"], DARK_OLIVE,
              (panel.centerx, panel.y + 30), "center")
    draw_text(surface, "[I] inspect     [1-4] choose     [ESC] back to menu", fonts["small"], OLIVE_GREEN,
              (panel.centerx, panel.y + 60), "center")


def complete_screen(window, fonts, level, clock):
    """Shown when the player reaches 100 points."""
    lines = [
        f"Objects sorted: {level.sorted}",
        f"Correct decisions: {level.correct_count}  ({level.accuracy}%)",
        f"Sent to Martha's workshop: {len(level.state['workshop_queue'])}",
        f"Waiting for material recovery: {len(level.state['recover_pile'])}",
    ]
    if level.relics_seen:
        lines.append(f"Relics found: {level.relics_seen}   saved: {level.relics_saved}   lost: {level.relics_lost}")

    if level.relics_lost:
        closing = "Some relics were lost. Look closely before you decide."
    elif level.relics_seen:
        closing = "Every relic you found is safe. Martha will be pleased."
    else:
        closing = "Martha is waiting for you in the workshop."

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                return "complete"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return "complete"

        window.fill(BG_YELLOW)
        draw_text(window, "LEVEL 1 COMPLETE", fonts["big"], OLIVE_GREEN, (WIDTH // 2, 120), "center")
        for i, line in enumerate(lines):
            draw_text(window, line, fonts["mid"], DARK_OLIVE, (WIDTH // 2, 210 + i * 40), "center")
        draw_text(window, closing, fonts["small"], OLIVE_GREEN, (WIDTH // 2, 210 + len(lines) * 40 + 30), "center")
        draw_text(window, "Press SPACE to return to the menu", fonts["small"], OLIVE_GREEN,
                  (WIDTH // 2, HEIGHT - 60), "center")
        pygame.display.flip()
        clock.tick(60)


def run_level_1(window, state):
    """Play Level 1. Returns "complete" when 100 points are reached, or "menu" on ESC."""
    clock = pygame.time.Clock()
    fonts = {
        "big": get_font(64),
        "name": get_font(38),
        "mid": get_font(32),
        "small": get_font(24),
        "tiny": get_font(20),
    }

    level = Level1(state)
    obj = level.next_object()
    inspected = False
    result = None
    card_x = CARD_START_X
    belt_pos = 0.0
    t = 0

    inspect_btn = Btn((520, 337, 160, 36), "INSPECT [I]")
    next_btn = Btn((910, 494, 190, 34), "NEXT [SPACE]")
    decision_buttons = []
    for i, name in enumerate(DECISIONS):
        decision_buttons.append(Btn((45 + i * 285, 408, 255, 64), f"[{i + 1}] {name.upper()}", DESTINATIONS[name]))

    while True:
        dt = clock.tick(60)
        t += dt
        mouse = pygame.mouse.get_pos()
        ready = card_x == 0   # the card has arrived on the belt

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
                        action = ("choose", KEYS.index(event.key))
                elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    action = ("next",)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if result is None:
                    if inspect_btn.hit(event.pos):
                        action = ("inspect",)
                    for i, button in enumerate(decision_buttons):
                        if button.hit(event.pos):
                            action = ("choose", i)
                elif next_btn.hit(event.pos):
                    action = ("next",)

        if action and ready:
            if action[0] == "inspect" and result is None:
                inspected = True
            elif action[0] == "choose" and result is None:
                result = level.decide(DECISIONS[action[1]])
                inspected = True   # show the clues afterwards so the player can learn from them
            elif action[0] == "next" and result is not None:
                if level.complete:
                    return complete_screen(window, fonts, level, clock)
                obj = level.next_object()
                inspected = False
                result = None
                card_x = CARD_START_X

        # ---- update -----------------------------------------------------------
        if card_x != 0:
            card_x += (0 - card_x) * min(1.0, dt / 130)
            belt_pos += dt * 0.35
            if abs(card_x) < 1:
                card_x = 0

        # ---- draw -------------------------------------------------------------
        window.fill(BG_YELLOW)
        draw_top_bar(window, fonts, level.score)

        belt = pygame.Rect(0, 305, WIDTH, 18)
        pygame.draw.rect(window, DARK_OLIVE, belt)
        for x in range(-40, WIDTH, 40):
            tick_x = x + int(belt_pos) % 40
            pygame.draw.line(window, OLIVE_GREEN, (tick_x, belt.top), (tick_x, belt.bottom - 2), 3)

        card = pygame.Rect(0, 0, 360, 200)
        card.center = (WIDTH // 2 + int(card_x), 205)
        draw_card(window, card, obj, inspected, t, fonts)

        inspect_btn.draw(window, fonts, mouse, enabled=(result is None and ready))
        for button in decision_buttons:
            button.draw(window, fonts, mouse, enabled=(result is None and ready))

        if result is None:
            draw_hint(window, fonts)
        else:
            draw_feedback(window, fonts, result, next_btn, mouse)

        pygame.display.flip()