"""Look-and-feel settings in one place: the font and the folder for object pictures."""
import os

import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---- Pictures --------------------------------------------------------------------
# Put one PNG per object in this folder. See assets/items/FILENAMES.txt for the names.
# Any object without a picture shows the small gear drawing instead.
ITEM_IMAGE_DIR = os.path.join(BASE_DIR, "assets", "items")

# ---- Font ------------------------------------------------------------------------
# None = pygame's built-in font. To use your own, put the .ttf file in assets/fonts/
# and point FONT_PATH at it, for example:
#   FONT_PATH = os.path.join(BASE_DIR, "assets", "fonts", "PressStart2P-Regular.ttf")
FONT_PATH = None

# Pixel fonts are usually wider than the default font. If text overflows its box,
# lower this (try 0.6 to 0.8). It scales every size in the game at once.
FONT_SIZE_SCALE = 1.0


def get_font(size):
    """Return a font at the given size, using FONT_PATH if it is set and the file exists."""
    path = FONT_PATH
    if path and not os.path.exists(path):
        print(f"[settings] Font file not found: {path} - using the default font instead.")
        path = None
    return pygame.font.Font(path, max(8, round(size * FONT_SIZE_SCALE)))