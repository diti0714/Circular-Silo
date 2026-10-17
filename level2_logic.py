"""Level 2 - Material Recovery: the rules only (no pygame, so they can be tested on their own).

The screen code lives in level2.py.

How it works: the objects the player sent to "Recover" in Level 1 arrive one by one.
Each has a few parts. Some are still usable, some are damaged. The player picks the
usable ones; those go into the parts storage for the repair levels.
"""
import random

from level1_logic import ITEMS, RELICS, TARGET

LEVEL_START = TARGET        # Level 2 begins at 100 points ...
LEVEL_END = 2 * TARGET      # ... and is finished at 200 points
DROPBACK_BELOW = TARGET     # falling below 100 sends the player back to Level 1

PART_POINTS = 10            # each usable part recovered
RELIC_PART_POINTS = 5       # parts taken from a relic are worth half (repairing it is better)
WRONG_PICK_POINTS = -5      # picking a part that is damaged
NOTHING_USABLE_POINTS = 10  # correctly saying there is nothing worth recovering
MISSED_ALL_POINTS = -5      # saying "nothing usable" when there were usable parts
RECENT_MEMORY = 3

GOOD_NOTES = [
    "Looks intact",
    "Tests fine",
    "No visible damage",
    "Still in good shape",
    "Works when tested",
]

G, B = True, False


def _p(name, good, note=None):
    """A part. `note` is what inspecting shows; usable parts get a random reassuring note."""
    return {"name": name, "good": good, "note": note}


# Parts for every object that can end up in the Recover pile. Part names are shared
# (Battery, Wiring, Motor, Speaker ...) so the stored parts can be used in the repair levels.
PARTS = {
    # --- Recover: not worth fixing, but some parts are good --------------------------
    "Burnt-out microwave": [_p("Transformer", G), _p("Motor", B, "Fused solid"), _p("Wiring", G),
                            _p("Circuit board", B, "Scorched black"), _p("Switch", G)],
    "Cracked laptop": [_p("Screen", B, "Shattered"), _p("Circuit board", B, "Burnt out"),
                       _p("Battery", G), _p("Keyboard", G), _p("Memory chip", G)],
    "Snapped bicycle": [_p("Frame", B, "Snapped in two"), _p("Gears", G), _p("Chain", G),
                        _p("Wheels", G), _p("Brake cable", B, "Snapped and frayed")],
    "Ruined speaker box": [_p("Speaker", B, "Cone is torn"), _p("Magnet", G), _p("Wiring", G),
                           _p("Cabinet", B, "Warped and split"), _p("Circuit board", G)],
    "Rusted washing drum": [_p("Drum", B, "Rusted through"), _p("Motor", G), _p("Pump", G),
                            _p("Hose", B, "Cracked and brittle"), _p("Switch", G)],

    # --- Reuse-type objects sent here by mistake: everything still works -------------
    "Flashlight": [_p("Battery", G), _p("Bulb", G), _p("Switch", G), _p("Casing", G)],
    "Steel water bottle": [_p("Cap", G), _p("Steel body", G), _p("Seal", G)],
    "Work gloves": [_p("Leather", G), _p("Stitching", G), _p("Lining", G)],
    "Desk lamp": [_p("Bulb", G), _p("Switch", G), _p("Wiring", G), _p("Spring arm", G)],
    "Canvas tool bag": [_p("Canvas", G), _p("Straps", G), _p("Zipper", G)],

    # --- Repair-type objects sent here by mistake: one part is the problem -----------
    "Table fan": [_p("Motor", G), _p("Blades", G), _p("Wiring", B, "One wire loose and cut"),
                  _p("Switch", G), _p("Grille", G)],
    "Kettle": [_p("Heating element", G), _p("Power cord", B, "Frayed near the plug"),
               _p("Switch", G), _p("Body", G)],
    "Desk radio": [_p("Speaker", G), _p("Antenna", G), _p("Circuit board", G),
                   _p("Wiring", B, "Loose and corroded")],
    "Leather boots": [_p("Leather", G), _p("Laces", G), _p("Sole", B, "Peeling and cracked"),
                      _p("Eyelets", G)],
    "Backpack": [_p("Fabric", G), _p("Straps", G), _p("Zipper", B, "Jammed and bent"),
                 _p("Buckles", G)],

    # --- Incinerate-type objects sent here by mistake: nothing is usable -------------
    "Moldy rags": [_p("Cloth", B, "Covered in black mold"), _p("Thread", B, "Rotten through"),
                   _p("Padding", B, "Soaked and moldy")],
    "Soaked packaging": [_p("Cardboard", B, "Soaked in solvent"), _p("Plastic film", B, "Brittle, contaminated"),
                         _p("Foam", B, "Chemical stains")],
    "Leaking battery pack": [_p("Cells", B, "Swollen and leaking"), _p("Terminals", B, "Eaten by acid"),
                             _p("Casing", B, "Cracked, contaminated"), _p("Wiring", B, "Corroded away")],
    "Crumbled insulation": [_p("Foam", B, "Crumbles to dust"), _p("Backing", B, "Soaked, contaminated"),
                            _p("Fibers", B, "Full of grime")],
    "Burnt wire bundle": [_p("Copper", B, "Brittle, snaps easily"), _p("Insulation", B, "Melted away"),
                          _p("Connector", B, "Fused together")],

    # --- Relics: taking them apart is allowed, but worth half the points -------------
    "Pocket watch": [_p("Gears", G), _p("Spring", G), _p("Crystal", B, "Cracked glass"),
                     _p("Winding crown", B, "Stuck and bent"), _p("Case", G)],
    "Music player": [_p("Battery", B, "Corroded"), _p("Circuit board", G), _p("Headphone jack", G),
                     _p("Casing", B, "Cracked"), _p("Wiring", G)],
    "Instant camera": [_p("Lens", G), _p("Shutter", B, "Jammed shut"), _p("Circuit board", G),
                       _p("Flash bulb", G)],
    "Toy robot": [_p("Gears", G), _p("Spring", G), _p("Tin body", B, "Dented and rusty"),
                  _p("Glass eyes", G)],
    "Travel book": [_p("Pages", G), _p("Cover", B, "Torn and stained"), _p("Binding", B, "Thread has rotted"),
                    _p("Map pages", G)],
    "Hand-crank radio": [_p("Crank", G), _p("Speaker", G), _p("Antenna", G),
                         _p("Circuit board", B, "Burnt"), _p("Dial", B, "Cracked")],
    "Data drive": [_p("Memory chip", G), _p("Casing", B, "Cracked open"), _p("Connector", G),
                   _p("Circuit board", G)],
    "Compass": [_p("Needle", G), _p("Glass", B, "Cracked"), _p("Case", G), _p("Hinge", B, "Rusted shut")],
}

_OBJECTS = {o["name"]: o for o in ITEMS + RELICS}


class Level2:
    """Hands out objects to take apart and scores the player's part choices.

    `state` is the shared game state from main.py. This level reads and updates:
      score         - the player's total score
      recover_pile  - objects waiting to be taken apart (filled by Level 1)
      components    - the parts storage, a list of {"name": ..., "from": ...} used by the repair levels
    """

    def __init__(self, state, rng=None):
        self.state = state
        self.state.setdefault("score", 0)
        self.state.setdefault("recover_pile", [])
        self.state.setdefault("components", [])
        self.rng = rng or random.Random()

        self.current = None
        self.selected = set()
        self.awaiting_next = False
        self.complete = False
        self.dropback = False
        self._recent = []

        # stats for the end-of-level screen
        self.objects_done = 0
        self.parts_recovered = 0
        self.wrong_picks = 0
        self.parts_missed = 0

    @property
    def score(self):
        return self.state["score"]

    def next_object(self):
        pile = self.state["recover_pile"]
        if pile:
            name = pile.pop(0)          # the objects the player sent here in Level 1
            from_pile = True
        else:
            # The pile is empty, so the scavenging team brings in more salvage.
            pool = [o["name"] for o in ITEMS if o["answer"] == "Recover"]
            fresh = [n for n in pool if n not in self._recent]
            name = self.rng.choice(fresh or pool)
            from_pile = False
        self._recent = (self._recent + [name])[-RECENT_MEMORY:]

        info = _OBJECTS[name]
        parts = [{"name": p["name"], "good": p["good"],
                  "note": p["note"] or self.rng.choice(GOOD_NOTES)} for p in PARTS[name]]
        self.rng.shuffle(parts)   # so the position of a part never gives the answer away
        self.current = {"name": name, "relic": info["relic"], "should_be": info["answer"],
                        "from_pile": from_pile, "parts": parts}
        self.selected = set()
        self.awaiting_next = False
        return self.current

    def toggle(self, index):
        """Select or unselect a part (before the player confirms)."""
        if self.current is None or self.awaiting_next:
            return
        if 0 <= index < len(self.current["parts"]):
            self.selected.symmetric_difference_update({index})

    def confirm(self, selected=None):
        """Recover the selected parts (or nothing, if `selected` is an empty set)."""
        if self.current is None or self.awaiting_next:
            raise RuntimeError("No object is waiting to be taken apart")

        obj = self.current
        parts = obj["parts"]
        chosen = set(self.selected if selected is None else selected)
        usable = {i for i, p in enumerate(parts) if p["good"]}
        right = sorted(chosen & usable)
        wrong = sorted(chosen - usable)
        missed = sorted(usable - chosen)
        per_part = RELIC_PART_POINTS if obj["relic"] else PART_POINTS

        if not chosen:
            if usable:
                points, headline = MISSED_ALL_POINTS, "PARTS MISSED"
            else:
                points, headline = NOTHING_USABLE_POINTS, "NOTHING USABLE"
        else:
            points = per_part * len(right) + WRONG_PICK_POINTS * len(wrong)
            if not wrong and not missed:
                headline = "PERFECT RECOVERY"
            elif right:
                headline = "PARTLY RECOVERED"
            else:
                headline = "WRONG PICKS"

        self.state["score"] = max(0, self.state["score"] + points)

        for i in right:
            self.state["components"].append({"name": parts[i]["name"], "from": obj["name"]})

        self.objects_done += 1
        self.parts_recovered += len(right)
        self.wrong_picks += len(wrong)
        self.parts_missed += len(missed)

        self.awaiting_next = True
        self.complete = self.state["score"] >= LEVEL_END
        self.dropback = self.state["score"] < DROPBACK_BELOW

        return {
            "name": obj["name"],
            "relic": obj["relic"],
            "chosen": sorted(chosen),
            "right": right,
            "wrong": wrong,
            "missed": missed,
            "points": points,
            "headline": headline,
            "good": points > 0,
            "message": self._message(obj, chosen, right, wrong, missed),
            "complete": self.complete,
            "dropback": self.dropback,
        }

    @staticmethod
    def _message(obj, chosen, right, wrong, missed):
        parts = obj["parts"]
        bits = []
        if not chosen and not any(p["good"] for p in parts):
            bits.append("Everything here was damaged or contaminated, so there was nothing worth recovering.")
        if right:
            bits.append("Recovered: " + ", ".join(parts[i]["name"] for i in right) + ".")
        if wrong:
            bits.append("Damaged parts: " + ", ".join(
                f"{parts[i]['name']} ({parts[i]['note'].lower()})" for i in wrong) + ".")
        if missed:
            bits.append("Missed usable parts: " + ", ".join(parts[i]["name"] for i in missed) + ".")
        if obj["relic"]:
            bits.append("Taking a relic apart earns half points. Repairing it would have been worth more.")
        elif obj["should_be"] != "Recover":
            bits.append(f"This should have been sent to {obj['should_be'].upper()} instead.")
        return " ".join(bits)