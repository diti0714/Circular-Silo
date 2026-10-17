import sys
import pygame

from level1 import run_level_1
from level2 import run_level_2
from settings import get_font

pygame.init()


WIDTH, HEIGHT = 1200, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SILO")

# Colors
OLIVE_GREEN = (107, 114, 60)
DARK_OLIVE = (70, 75, 40)
BG_YELLOW = (226, 219, 149)


# The font is chosen in settings.py (FONT_PATH)
level_font = get_font(20)
button_font = get_font(32)

# Progress shared between the menu and the levels.
# Levels read and update this (score, recovered parts, workshop queue, relics).
game_state = {"score": 0}


class PixelButton:
    def __init__(self, text, x, y, width, height, font):
        self.text = text
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        # Choose colors based on mouse hover state
        border_color = DARK_OLIVE if self.is_hovered else OLIVE_GREEN
        text_color = DARK_OLIVE if self.is_hovered else OLIVE_GREEN


        pygame.draw.rect(surface, border_color, self.rect, width=3)


        text_surface = self.font.render(self.text, False, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(mouse_pos)
        return False


def set_level(score):
    # Each level needs 100 points, so reaching 100 moves the player up.
    if score < 100:
        return 1
    elif score < 200:
        return 2
    elif score < 300:
        return 3
    elif score < 400:
        return 4
    else:
        return 5


def coming_soon(level_number):
    """Placeholder for levels that are not built yet."""
    clock = pygame.time.Clock()

    while True:
        window.fill(BG_YELLOW)

        title = button_font.render(f"LEVEL {level_number} - COMING SOON", False, OLIVE_GREEN)
        window.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 30))
        hint = level_font.render("Press ESC to go back", False, OLIVE_GREEN)
        window.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        pygame.display.flip()
        clock.tick(60)


def play_current_level():
    """ Game loop when Play is selected """
    level = set_level(game_state["score"])
    if level == 1:
        run_level_1(window, game_state)
    elif level == 2:
        run_level_2(window, game_state)
    else:
        coming_soon(level)


def main_menu():
    try:
        bg_img = pygame.image.load("bg.jpg")
        bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
    except (pygame.error, FileNotFoundError):
        bg_img = None

    play_button = PixelButton("PLAY", x=WIDTH // 2, y=465, width=140, height=45, font=button_font)
    quit_button = PixelButton("QUIT", x=WIDTH // 2, y=525, width=140, height=45, font=button_font)

    clock = pygame.time.Clock()

    while True:
        mouse_pos = pygame.mouse.get_pos()

        # Score and level are re-drawn every frame so they update after playing
        current_score = game_state["score"]
        current_level = set_level(current_score)
        score_surface = button_font.render(f"SCORE: {current_score}", False, OLIVE_GREEN)
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 362))
        level_text_surface = level_font.render(f"LEVEL {current_level}", False, OLIVE_GREEN)
        level_rect = level_text_surface.get_rect(center=(WIDTH // 2, 410))

        # Render Background
        if bg_img:
            window.blit(bg_img, (0, 0))
        else:
            window.fill(BG_YELLOW)

        window.blit(score_surface, score_rect)
        window.blit(level_text_surface, level_rect)

        # Update and Draw Buttons
        play_button.check_hover(mouse_pos)
        quit_button.check_hover(mouse_pos)

        play_button.draw(window)
        quit_button.draw(window)

        # Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if play_button.is_clicked(mouse_pos, event):
                play_current_level()

            if quit_button.is_clicked(mouse_pos, event):
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main_menu()