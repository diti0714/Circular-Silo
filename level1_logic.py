"""Level 1 - Sorting: the rules only (no pygame in here, so they can be tested on their own).

The screen code lives in level1.py.
"""
import random
import re

DECISIONS = ["Reuse", "Repair", "Recover", "Incinerate"]

DESTINATIONS = {
    "Reuse": "Recycling Department",
    "Repair": "Martha's Workshop",
    "Recover": "Level 2 Material Recovery",
    "Incinerate": "Incineration",
}

TARGET = 100            # points needed to finish the level
CORRECT_POINTS = 10
WRONG_POINTS = -5
RELIC_LOST_POINTS = -15  # incinerating a relic costs more than a normal mistake
RELIC_CHANCE = 1 / 8     # about 1 in 8 objects is a relic
RECENT_MEMORY = 4        # an object will not come back until 4 others have passed


def _item(name, answer, clues, why, relic=False):
    return {"name": name, "answer": answer, "clues": clues, "why": why, "relic": relic}


def image_filename(name):
    """The picture file for an object, e.g. "Hand-crank radio" -> "hand_crank_radio.jpg"."""
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") + ".jpg"


# Ordinary objects from the scavenging team --------------------------------------
ITEMS = [
    # Reuse: still works as it is
    _item("Flashlight", "Reuse",
          ["Casing scuffed but solid", "Bulb lights up when tested", "Battery holds a charge"],
          "It still works as it is, so no repair or recovery is needed."),
    _item("Steel water bottle", "Reuse",
          ["Dented but sealed tight", "No leaks when filled", "Lid screws on fine"],
          "A dent does not matter. It holds water, so reuse it."),
    _item("Work gloves", "Reuse",
          ["Stitching is intact", "Palms a little worn", "No holes or tears"],
          "Still good for another shift of work."),
    _item("Desk lamp", "Reuse",
          ["Switch clicks, bulb glows", "Arm holds its position", "Cord is in good shape"],
          "Fully working. Replacing it would waste materials."),
    _item("Canvas tool bag", "Reuse",
          ["Straps firmly attached", "Zip runs smoothly", "Only dirt on the outside"],
          "Dirt is not damage. Clean it and reuse it."),

    # Repair: damaged, but fixable
    _item("Table fan", "Repair",
          ["Blades spin, then stop", "Loose wire at the motor", "Housing is undamaged"],
          "One loose wire is a simple fix. Martha can repair it."),
    _item("Kettle", "Repair",
          ["Heating element is fine", "Power cord frayed at plug", "Body has no cracks"],
          "Only the cord is damaged, so it is worth repairing."),
    _item("Desk radio", "Repair",
          ["Speaker works when tapped", "Dial knob is missing", "One connection is loose"],
          "Small faults on a working radio. Repair it."),
    _item("Leather boots", "Repair",
          ["Sole is peeling away", "Leather is still sound", "Laces are fine"],
          "Re-attaching the sole saves a good pair of boots."),
    _item("Backpack", "Repair",
          ["Zipper is jammed", "Fabric has no tears", "Straps are strong"],
          "A jammed zipper is an easy fix."),

    # Recover: not worth fixing, but the parts are good
    _item("Burnt-out microwave", "Recover",
          ["Motor is fused solid", "Transformer looks intact", "Casing is cracked"],
          "Too damaged to fix, but the transformer and wiring are worth recovering."),
    _item("Cracked laptop", "Recover",
          ["Screen shattered, board fried", "Battery and RAM look fine", "Keyboard still works"],
          "It can't be fixed, but its good components can be recovered."),
    _item("Snapped bicycle", "Recover",
          ["Frame is snapped in two", "Gears and chain are good", "Wheels spin freely"],
          "The frame is beyond repair, but the gears, chain and wheels can be recovered."),
    _item("Ruined speaker box", "Recover",
          ["Speaker cone is torn", "Magnet and wiring are good", "Cabinet is warped"],
          "The cone is ruined, but the magnet and wiring are reusable parts."),
    _item("Rusted washing drum", "Recover",
          ["Drum rusted through", "Motor still turns", "Pump looks usable"],
          "The drum is gone, but the motor and pump can be recovered."),

    # Incinerate: nothing practical left
    _item("Moldy rags", "Incinerate",
          ["Covered in black mold", "Fibers fall apart", "Smells of rot"],
          "Contaminated and falling apart. Nothing safe can be reused or recovered."),
    _item("Soaked packaging", "Incinerate",
          ["Soaked in harsh solvent", "Material is brittle", "Nothing to salvage"],
          "Contaminated and unsafe, with no practical use left."),
    _item("Leaking battery pack", "Incinerate",
          ["Cells are swollen", "Acid is leaking out", "Terminals eaten away"],
          "Too dangerous to handle or recover. Incineration is the safe choice."),
    _item("Crumbled insulation", "Incinerate",
          ["Crumbles when touched", "Full of dust and grime", "No intact pieces"],
          "Nothing is left that can be reused, repaired or recovered."),
    _item("Burnt wire bundle", "Incinerate",
          ["Insulation has melted", "Copper is brittle", "Strands snap when bent"],
          "Burnt through, so nothing useful can be recovered."),
]

# Relics from the Before Times: the best decision is always Repair --------------
_RELIC_TAG = "RELIC: from the Before Times"

RELICS = [
    _item("Pocket watch", "Repair", [_RELIC_TAG, "Winding stem is stuck", "Gears look intact"],
          "A watch like this has lasted generations. Repairing it keeps that going.", relic=True),
    _item("Music player", "Repair", [_RELIC_TAG, "Battery door is cracked", "Circuit board looks fine"],
          "It holds the sound of another time. Repair it, don't strip it.", relic=True),
    _item("Instant camera", "Repair", [_RELIC_TAG, "Shutter button jams", "Lens is clear"],
          "Cameras hold pictures of the old world. Worth restoring.", relic=True),
    _item("Toy robot", "Repair", [_RELIC_TAG, "One arm is missing", "Tin paint is still bright"],
          "A child once loved this. Repairing it saves a memory.", relic=True),
    _item("Travel book", "Repair", [_RELIC_TAG, "Spine is torn loose", "Pages are readable"],
          "A book from the surface is nearly priceless. Mend it.", relic=True),
    _item("Hand-crank radio", "Repair", [_RELIC_TAG, "Crank is stiff", "Speaker still crackles"],
          "It needs no power grid, just a hand. A clever design worth saving.", relic=True),
    _item("Data drive", "Repair", [_RELIC_TAG, "Casing is cracked open", "Chip looks undamaged"],
          "It may hold knowledge from before. Never destroy it.", relic=True),
    _item("Compass", "Repair", [_RELIC_TAG, "Needle sticks in place", "Glass cover is cracked"],
          "A tool for a world we can no longer walk. Keep it working.", relic=True),
]


class Level1:
    """Hands out objects and scores the player's sorting decisions.

    `state` is the shared game state from main.py. This level reads and updates:
      score           - the player's total score
      recover_pile    - names of objects sent to Level 2 (Recover)
      workshop_queue  - objects sent to Martha's workshop (Repair), with a relic flag
      relics_destroyed - how many relics have been incinerated
    """

    def __init__(self, state, rng=None):
        self.state = state
        self.state.setdefault("score", 0)
        self.state.setdefault("recover_pile", [])
        self.state.setdefault("workshop_queue", [])
        self.state.setdefault("relics_destroyed", 0)
        self.rng = rng or random.Random()

        self.current = None
        self.awaiting_next = False   # True between a decision and the next object
        self.complete = False
        self._recent = []

        # stats for the end-of-level screen
        self.sorted = 0
        self.correct_count = 0
        self.relics_seen = 0
        self.relics_saved = 0
        self.relics_lost = 0

    @property
    def score(self):
        return self.state["score"]

    @property
    def accuracy(self):
        return round(100 * self.correct_count / self.sorted) if self.sorted else 0

    def next_object(self):
        pool = RELICS if self.rng.random() < RELIC_CHANCE else ITEMS
        fresh = [o for o in pool if o["name"] not in self._recent]
        self.current = self.rng.choice(fresh or pool)
        self._recent.append(self.current["name"])
        self._recent = self._recent[-RECENT_MEMORY:]
        self.awaiting_next = False
        if self.current["relic"]:
            self.relics_seen += 1
        return self.current

    def decide(self, choice):
        """Apply the player's decision to the current object and return the result."""
        if choice not in DECISIONS:
            raise ValueError(f"Unknown decision: {choice}")
        if self.current is None or self.awaiting_next:
            raise RuntimeError("No object is waiting for a decision")

        obj = self.current
        answer = obj["answer"]
        correct = choice == answer

        if correct:
            points, headline, message = CORRECT_POINTS, "CORRECT", obj["why"]
        elif obj["relic"] and choice == "Incinerate":
            points, headline = RELIC_LOST_POINTS, "RELIC LOST"
            message = f"A relic is gone for good. Best choice was REPAIR. {obj['why']}"
        else:
            points, headline = WRONG_POINTS, "WRONG"
            message = f"Best choice was {answer.upper()}. {obj['why']}"

        self.state["score"] = max(0, self.state["score"] + points)

        # The object goes where the player sent it, right or wrong.
        if choice == "Repair":
            self.state["workshop_queue"].append({"name": obj["name"], "relic": obj["relic"]})
        elif choice == "Recover":
            self.state["recover_pile"].append(obj["name"])
        elif choice == "Incinerate" and obj["relic"]:
            self.state["relics_destroyed"] += 1

        self.sorted += 1
        if correct:
            self.correct_count += 1
        if obj["relic"]:
            if choice == "Repair":
                self.relics_saved += 1
            elif choice == "Incinerate":
                self.relics_lost += 1

        self.awaiting_next = True
        self.complete = self.state["score"] >= TARGET

        return {
            "name": obj["name"],
            "relic": obj["relic"],
            "choice": choice,
            "answer": answer,
            "correct": correct,
            "points": points,
            "headline": headline,
            "message": message,
            "destination": DESTINATIONS[choice],
            "complete": self.complete,
        }