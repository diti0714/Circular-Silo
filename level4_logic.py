"""Level 4 - Advanced Repair: the rules only (no pygame, so they can be tested on their own).

The screen code lives in level4.py.

How it works: Martha gives only general advice. The player must
  1. inspect the object,
  2. work out which components are faulty (and may mark them),
  3. choose the actions the repair needs from a list of eight (five are needed, three are wrong),
  4. put them in the right order, and
  5. press DONE FIXING. Martha then reviews the repair and scores it.

Scoring follows the README: the score is the share of the required sequence the player got right
(the longest run of required actions in the right order), 10 points per required action out of 5,
minus 5 for every wrong action chosen.
"""
import random

from level1_logic import RELICS, TARGET
from level3_logic import HINT_POUCH_MAX, RELIC_INFO, grant_relic_reward

LEVEL_START = 3 * TARGET    # Level 4 begins at 300 points ...
LEVEL_END = 4 * TARGET      # ... and is finished at 400 points
DROPBACK_BELOW = LEVEL_START  # finishing a job below 300 sends the player back to Level 3

SCALE_MAX = 50              # 100% correct = 50 points (README scale: 80% = 40, 60% = 30 ...)
WRONG_POINTS = -5           # for every wrong action chosen
PART_BONUS = 5              # extra for using a part recovered in Level 2
RELIC_BONUS = 30            # extra for a successful relic repair
SUCCESS_FRACTION = 0.8      # at least 80% correct counts as a successful repair
RECENT_MEMORY = 2

_RELIC_NAMES = {o["name"] for o in RELICS}


def _f(name, note, faulty):
    """What inspecting shows for one component. `faulty` is never shown: the player works it out."""
    return {"name": name, "note": note, "faulty": faulty}


def _s(label, part=None):
    """A required repair action. `part` is the stored part it uses, if any."""
    return {"label": label, "part": part}


def _w(label, why):
    """A wrong action, and the reason it is wrong (shown in Martha's review)."""
    return {"label": label, "why": why}


# One job per object that is correctly sorted to Repair in Level 1. These are different faults from the
# Level 3 versions, so the player can't just remember the answers. Each has 4 findings, 5 required
# actions (in order) and 3 wrong actions.
JOBS = {
    # --- ordinary objects -------------------------------------------------------------
    "Table fan": {
        "advice": "This fan won't start at all. Check the power path before you open anything, and find the fault first.",
        "findings": [_f("Power cord", "Plug and cord undamaged", False), _f("Switch", "Clicks, but nothing happens", True),
                     _f("Motor", "Turns freely by hand", False), _f("Blades", "Straight, spin freely", False)],
        "steps": [_s("Unplug the fan"), _s("Open the base housing"), _s("Remove the old switch"),
                  _s("Fit a new switch", "Switch"), _s("Test the fan")],
        "wrong": [_w("Replace the motor", "The motor turned freely"), _w("Replace the power cord", "The cord was undamaged"),
                  _w("Hit it with a hammer", "Never strike a machine to fix it")],
    },
    "Kettle": {
        "advice": "This kettle leaks from the bottom. Empty it and let it cool before you look at anything.",
        "findings": [_f("Rubber seal", "Cracked, water seeps through", True), _f("Heating element", "Clean, no scale", False),
                     _f("Power cord", "Cord and plug undamaged", False), _f("Lid", "Closes tightly", False)],
        "steps": [_s("Unplug and empty it"), _s("Remove the base plate"), _s("Remove the cracked seal"),
                  _s("Fit a new seal"), _s("Refill and test")],
        "wrong": [_w("Replace the element", "The element was clean"), _w("Replace the power cord", "The cord was undamaged"),
                  _w("Wrap it in tape", "Tape won't hold hot water")],
    },
    "Desk radio": {
        "advice": "No sound, but the dial and lights work. Follow the signal from the aerial to the speaker.",
        "findings": [_f("Speaker", "Cone intact, magnet strong", False), _f("Circuit board", "Burn mark by the amplifier", True),
                     _f("Wiring", "Connections tight and clean", False), _f("Antenna", "Extends and connects fine", False)],
        "steps": [_s("Unplug the radio"), _s("Remove the back panel"), _s("Remove the burnt board"),
                  _s("Fit a good circuit board", "Circuit board"), _s("Test the sound")],
        "wrong": [_w("Replace the speaker", "The speaker was intact"), _w("Replace the wiring", "The wiring was clean"),
                  _w("Spray it with water", "Never wet live electronics")],
    },
    "Leather boots": {
        "advice": "These boots let water in. Look closely at how the leather is held together.",
        "findings": [_f("Stitching", "Seam split along the toe", True), _f("Sole", "Firmly attached, good tread", False),
                     _f("Leather", "Supple, no cracks", False), _f("Laces", "Strong, no fraying", False)],
        "steps": [_s("Clean the seam area"), _s("Trim the loose threads"), _s("Re-stitch the seam"),
                  _s("Apply waterproof wax"), _s("Check the seam holds")],
        "wrong": [_w("Replace the sole", "The sole was firmly attached"), _w("Replace the laces", "The laces were strong"),
                  _w("Cut away the toe", "Never cut away good leather")],
    },
    "Backpack": {
        "advice": "The strap tears away when the bag is loaded. Empty it, then look at where the strap is joined.",
        "findings": [_f("Strap seam", "Torn loose at the top corner", True), _f("Zipper", "Runs smoothly", False),
                     _f("Fabric", "No holes or tears", False), _f("Buckle", "Clips firmly", False)],
        "steps": [_s("Empty the backpack"), _s("Unpick the loose stitching"), _s("Reposition the strap"),
                  _s("Stitch with strong thread"), _s("Load-test the strap")],
        "wrong": [_w("Replace the zipper", "The zipper ran smoothly"), _w("Patch the fabric", "The fabric had no tears"),
                  _w("Cut the strap off", "Never cut off a good strap")],
    },

    # --- relics --------------------------------------------------------------------------
    "Pocket watch": {
        "advice": "The watch has stopped. Handle it gently, because old brass does not forgive force.",
        "findings": [_f("Mainspring", "Wound, still holds tension", False), _f("Gear train", "One gear chipped, rest fine", True),
                     _f("Crystal", "Cracked, but sealed", False), _f("Crown", "Turns smoothly", False)],
        "steps": [_s("Open the case back"), _s("Lift out the movement"), _s("Replace the chipped gear", "Gears"),
                  _s("Oil the pivots"), _s("Close up and test")],
        "wrong": [_w("Replace the mainspring", "The spring held tension"), _w("Replace the crystal", "The crack was cosmetic"),
                  _w("Force the crown", "Never force old metal")],
    },
    "Music player": {
        "advice": "It is completely dead. Old batteries leak, so look at where the power comes in.",
        "findings": [_f("Battery", "Leaked and swollen", True), _f("Contacts", "Covered in green corrosion", True),
                     _f("Circuit board", "No damage, tests fine", False), _f("Headphone jack", "Clean, plug fits snugly", False)],
        "steps": [_s("Remove the old battery"), _s("Clean corroded contacts"), _s("Fit a new battery", "Battery"),
                  _s("Close the battery door"), _s("Play a test track")],
        "wrong": [_w("Replace the circuit board", "The board tested fine"), _w("Replace the headphone jack", "The jack was clean"),
                  _w("Pry it with a knife", "A knife could short the battery")],
    },
    "Instant camera": {
        "advice": "The shutter button does nothing. Dust and worn parts are both likely, so look before you swap.",
        "findings": [_f("Shutter switch", "Worn, contacts won't meet", True), _f("Lens", "Clear, no scratches", False),
                     _f("Flash", "Charges and fires", False), _f("Film door", "Seals light tight", False)],
        "steps": [_s("Open the camera body"), _s("Brush out the dust"), _s("Replace the shutter switch", "Switch"),
                  _s("Close the camera body"), _s("Test the shutter")],
        "wrong": [_w("Replace the lens", "The lens was clear"), _w("Replace the flash", "The flash worked fine"),
                  _w("Soak it in oil", "Oil ruins a camera inside")],
    },
    "Toy robot": {
        "advice": "The robot has lost an arm and its walk has gone stiff. Fix the joint before you fit anything.",
        "findings": [_f("Arm socket", "Empty, joint is bent", True), _f("Gearbox", "Gears worn, one missing", True),
                     _f("Paint", "Bright, no flaking", False), _f("Wind-up key", "Turns, holds tension", False)],
        "steps": [_s("Inspect the joint"), _s("Shape a new tin arm"), _s("Fit gears in the gearbox", "Gears"),
                  _s("Attach the new arm"), _s("Wind up and test")],
        "wrong": [_w("Repaint the robot", "The paint was still bright"), _w("Replace the key", "The key held tension"),
                  _w("Bend it by force", "Never force old tin")],
    },
    "Travel book": {
        "advice": "The spine has torn and pages are coming loose. Work gently, because paper can't be replaced.",
        "findings": [_f("Binding thread", "Rotten, snaps easily", True), _f("Spine", "Torn along its length", True),
                     _f("Pages", "Readable, not torn", False), _f("Cover", "Stiff and intact", False)],
        "steps": [_s("Gather the loose pages"), _s("Remove the old thread"), _s("Re-sew the binding"),
                  _s("Glue the spine"), _s("Press and dry")],
        "wrong": [_w("Trim the pages", "The pages were undamaged"), _w("Replace the cover", "The cover was intact"),
                  _w("Tape across the pages", "Tape damages old paper")],
    },
    "Hand-crank radio": {
        "advice": "Cranking gives only a weak crackle. Think about how the power gets from the crank to the speaker.",
        "findings": [_f("Crank gearbox", "Gears slip under load", True), _f("Speaker wire", "Frayed near the speaker", True),
                     _f("Antenna", "Extends and connects fine", False), _f("Dial", "Turns, tunes normally", False)],
        "steps": [_s("Open the radio casing"), _s("Reseat the crank gears"), _s("Replace the speaker wire", "Wiring"),
                  _s("Close the casing"), _s("Crank and test")],
        "wrong": [_w("Replace the antenna", "The antenna was fine"), _w("Replace the dial", "The dial tuned normally"),
                  _w("Wet the gearbox", "Water would rust the gears")],
    },
    "Data drive": {
        "advice": "The drive isn't recognised. Protect the chip, because the data matters more than the case.",
        "findings": [_f("Connector", "Bent, makes no contact", True), _f("Memory chip", "Undamaged, pins clean", False),
                     _f("Circuit board", "Hairline crack in a trace", True), _f("Casing", "Cracked but holds together", False)],
        "steps": [_s("Open the cracked case"), _s("Lift out the chip"), _s("Move chip to a new board", "Circuit board"),
                  _s("Straighten the connector"), _s("Test the connection")],
        "wrong": [_w("Replace the memory chip", "The chip was undamaged"), _w("Replace the casing", "The case still held"),
                  _w("Scrub the chip pins", "Scrubbing could erase the data")],
    },
    "Compass": {
        "advice": "The needle won't settle on north. The glass is cracked, but think about what is really wrong.",
        "findings": [_f("Pivot", "Gummed up with old oil", True), _f("Needle", "Straight, still magnetic", False),
                     _f("Glass cover", "Cracked, still seals", False), _f("Case", "Solid, no dents", False)],
        "steps": [_s("Lift off the glass"), _s("Polish the pivot point"), _s("Unstick the needle"),
                  _s("Refit the glass cover"), _s("Check it points north")],
        "wrong": [_w("Replace the needle", "The needle was still magnetic"), _w("Replace the case", "The case was solid"),
                  _w("Magnetize the case", "That would ruin the reading")],
    },
}

_ORDINARY_JOBS = [name for name in JOBS if name not in RELIC_INFO]

# What Relic Wisdom does in this level. Hint types not listed here belong to other levels.
HINTS_HERE = ["step_order", "hidden_defect", "trap_action", "martha_step", "free_part"]
CHOICE_LABELS = {
    "step_order": "Show the first 2 steps",
    "hidden_defect": "Reveal a faulty component",
    "trap_action": "Mark a trap action",
    "martha_step": "Martha tells you a step",
    "free_part": "Get the spare part you need",
}

COMMENTS = [
    (100, "Perfect. That is exactly how it's done."),
    (80, "Nearly there. Mind the order next time."),
    (60, "Good effort, but you missed some things."),
    (40, "Look harder at what the inspection tells you."),
    (0, "That won't hold. Inspect first, then decide."),
]


def required_order_score(sequence):
    """Which positions of `sequence` count as correct.

    `sequence` is the player's actions, each given as its required-step number (0, 1, 2 ...) or None
    for a wrong action. The correct ones are the longest run of required actions that are in the right
    order. For the README example, required A B C D E and chosen A B D C E give 4 of 5.
    """
    items = [(pos, step) for pos, step in enumerate(sequence) if step is not None]
    if not items:
        return set()
    best = [1] * len(items)
    prev = [-1] * len(items)
    for i in range(len(items)):
        for j in range(i):
            if items[j][1] < items[i][1] and best[j] + 1 > best[i]:
                best[i], prev[i] = best[j] + 1, j
    end = max(range(len(items)), key=lambda k: best[k])
    correct = set()
    while end != -1:
        correct.add(items[end][0])
        end = prev[end]
    return correct


class Level4:
    """Hands out advanced repair jobs and scores the player's repair order.

    `state` is the shared game state from main.py. This level reads and updates:
      score            - the player's total score
      workshop_queue   - objects sent to Martha's workshop in Level 1
      components       - the parts storage filled in Level 2
      relic_collection - relics restored so far
      hint_pouch       - Relic Wisdom hints; this level lets the player use them
    """

    # Level 5 changes these (see level5_logic.py)
    NUMBER = 4
    START = LEVEL_START
    END = LEVEL_END
    DROP = DROPBACK_BELOW
    GUIDED = True      # Martha gives advice and reviews the repair

    def __init__(self, state, rng=None):
        self.state = state
        self.state.setdefault("score", 0)
        self.state.setdefault("workshop_queue", [])
        self.state.setdefault("components", [])
        self.state.setdefault("relic_collection", [])
        self.state.setdefault("hint_pouch", [])
        self.rng = rng or random.Random()

        self.job = None
        self.inspected = False
        self.marks = set()            # findings the player marked as faulty
        self.sequence = []            # indexes into job["actions"], in the order the player chose
        self.tags = {}                # action index -> hint tag ("1st", "2nd", "TIP")
        self.trapped = set()          # action indexes revealed as traps
        self.revealed_faulty = set()  # finding indexes revealed as faulty by a hint
        self.finished = False
        self.complete = False
        self.dropback = False
        self.sent_back = []
        self._skipped = set()
        self._recent = []
        self._entry = None
        self._hint_log = []           # hints used on the current job, so leaving can give them back
        self._free_part_given = False

        # stats for the end-of-level screen
        self.jobs_done = 0
        self.successes = 0
        self.parts_used = 0
        self.relics_restored = 0
        self.hints_used = 0

    # ---- reading the current state ----------------------------------------------------------
    @property
    def score(self):
        return self.state["score"]

    def parts_in_storage(self, name):
        return sum(1 for c in self.state["components"] if c["name"] == name)

    def can_set_aside(self):
        return (self.job is not None and self.job["relic"] and not self.finished
                and not self.inspected and not self.sequence)

    @property
    def part_step(self):
        """The required step that uses a stored part, or None."""
        if self.job is None:
            return None
        return next((s for s in self.job["steps"] if s["part"]), None)

    # ---- getting the next job ---------------------------------------------------------------
    def _take_from_queue(self):
        queue = self.state["workshop_queue"]
        for i, entry in enumerate(queue):
            if id(entry) in self._skipped:
                continue
            queue.pop(i)
            if entry["name"] in JOBS:
                return entry
            self.sent_back.append(entry["name"])
            return self._take_from_queue()
        return None

    def next_job(self):
        entry = self._take_from_queue()
        if entry is not None:
            name, from_queue = entry["name"], True
        else:
            fresh = [n for n in _ORDINARY_JOBS if n not in self._recent]
            name, from_queue = self.rng.choice(fresh or _ORDINARY_JOBS), False
        self._recent = (self._recent + [name])[-RECENT_MEMORY:]

        data = JOBS[name]
        actions = [{"label": s["label"], "step": i, "why": None} for i, s in enumerate(data["steps"])]
        actions += [{"label": w["label"], "step": None, "why": w["why"]} for w in data["wrong"]]
        while True:       # shuffle, but never leave the required actions in the order they must be done
            self.rng.shuffle(actions)
            order = [a["step"] for a in actions if a["step"] is not None]
            if order != sorted(order):
                break

        self.job = {"name": name, "relic": name in _RELIC_NAMES, "from_queue": from_queue,
                    "advice": data["advice"], "findings": [dict(f) for f in data["findings"]],
                    "steps": [dict(s) for s in data["steps"]], "actions": actions}
        self._entry = entry
        self.inspected = False
        self.marks = set()
        self.sequence = []
        self.tags = {}
        self.trapped = set()
        self.revealed_faulty = set()
        self.finished = False
        self._hint_log = []
        self._free_part_given = False
        return self.job

    def set_aside(self):
        if not self.can_set_aside() or self._entry is None:
            return False
        self._skipped.add(id(self._entry))
        self.state["workshop_queue"].append(self._entry)
        self.job = None
        self._entry = None
        return True

    def abandon(self):
        """The player leaves mid-job: nothing has been scored yet, so the job goes back to the queue
        and any hints used on it are given back."""
        if self.job is not None and not self.finished:
            for pos, hint, added in reversed(self._hint_log):
                if added is not None and added in self.state["components"]:
                    self.state["components"].remove(added)
                if len(self.state["hint_pouch"]) < HINT_POUCH_MAX:
                    self.state["hint_pouch"].insert(min(pos, len(self.state["hint_pouch"])), hint)
            if self._entry is not None:
                self.state["workshop_queue"].insert(0, self._entry)
        self.job = None
        self._entry = None
        self.sequence = []
        self.marks = set()
        self._hint_log = []

    # ---- the player's moves ----------------------------------------------------------------
    def inspect(self):
        if self.job is None or self.finished:
            return False
        self.inspected = True
        return True

    def toggle_mark(self, index):
        """Mark (or unmark) a component as faulty. Only possible after inspecting."""
        if self.job is None or self.finished or not self.inspected or not 0 <= index < len(self.job["findings"]):
            return False
        self.marks.symmetric_difference_update({index})
        return True

    def pick(self, index):
        """Add an action to the repair order, or take it out again if it is already there."""
        if self.job is None or self.finished or not 0 <= index < len(self.job["actions"]):
            return False
        if index in self.sequence:
            self.sequence.remove(index)
        else:
            self.sequence.append(index)
        return True

    def undo(self):
        if self.job is None or self.finished or not self.sequence:
            return False
        self.sequence.pop()
        return True

    def clear(self):
        if self.job is None or self.finished or not self.sequence:
            return False
        self.sequence = []
        return True

    # ---- Relic Wisdom ---------------------------------------------------------------------------
    def hint_usable(self, hint_type):
        """Can a hint of this type help with the current job right now?"""
        if self.job is None or self.finished:
            return False
        actions = self.job["actions"]
        if hint_type == "step_order":
            firsts = [self._action_for_step(0), self._action_for_step(1)]
            return any(self.tags.get(i) is None for i in firsts)
        if hint_type == "hidden_defect":
            return any(f["faulty"] and i not in self.revealed_faulty for i, f in enumerate(self.job["findings"]))
        if hint_type == "trap_action":
            return any(a["step"] is None and i not in self.trapped for i, a in enumerate(actions))
        if hint_type == "martha_step":
            return self._martha_target() is not None
        if hint_type == "free_part":
            return self.part_step is not None and not self._free_part_given
        if hint_type == "player_choice":
            return any(self.hint_usable(t) for t in HINTS_HERE)
        return False

    def _action_for_step(self, step):
        return next(i for i, a in enumerate(self.job["actions"]) if a["step"] == step)

    def _martha_target(self):
        """The earliest required action the player hasn't chosen yet (and that isn't already tagged)."""
        for step in range(len(self.job["steps"])):
            i = self._action_for_step(step)
            if i not in self.sequence and i not in self.tags:
                return i
        return None

    def usable_choices(self):
        """For the Data drive hint: which hints it can turn into right now."""
        return [t for t in HINTS_HERE if self.hint_usable(t)]

    def use_hint(self, pouch_index, choice=None):
        """Use the hint at `pouch_index` in the pouch. Returns {"ok", "message"}; a used hint is removed.

        For the Data drive hint (player_choice), `choice` must be one of usable_choices().
        """
        pouch = self.state["hint_pouch"]
        if self.job is None or self.finished or not 0 <= pouch_index < len(pouch):
            return {"ok": False, "message": "There is no hint to use."}
        hint = pouch[pouch_index]
        kind = hint["type"]
        if kind == "player_choice":
            if choice not in self.usable_choices():
                return {"ok": False, "message": "Choose a hint that can help with this repair."}
            kind = choice
        if not self.hint_usable(kind):
            return {"ok": False, "message": f"The {hint['relic']} hint can't help with this repair."}

        added = None
        if kind == "step_order":
            self.tags[self._action_for_step(0)] = "1st"
            self.tags[self._action_for_step(1)] = "2nd"
            message = "The first two required actions are tagged 1st and 2nd."
        elif kind == "hidden_defect":
            i = next(i for i, f in enumerate(self.job["findings"]) if f["faulty"] and i not in self.revealed_faulty)
            self.revealed_faulty.add(i)
            message = f"The {self.job['findings'][i]['name'].lower()} is faulty."
        elif kind == "trap_action":
            i = next(i for i, a in enumerate(self.job["actions"]) if a["step"] is None and i not in self.trapped)
            self.trapped.add(i)
            message = f"'{self.job['actions'][i]['label']}' is a trap. It is crossed out."
        elif kind == "martha_step":
            i = self._martha_target()
            self.tags[i] = "TIP"
            message = f"Martha says you need '{self.job['actions'][i]['label']}'. It is tagged TIP."
        else:   # free_part
            added = {"name": self.part_step["part"], "from": "Relic Wisdom"}
            self.state["components"].append(added)
            self._free_part_given = True
            message = f"A spare {added['name'].lower()} was added to your parts storage."

        pouch.pop(pouch_index)
        self._hint_log.append((pouch_index, hint, added))
        self.hints_used += 1
        return {"ok": True, "message": f"{hint['relic']} wisdom: {message}"}

    # ---- Martha's review -------------------------------------------------------------------------------
    def done_fixing(self):
        """The player presses DONE FIXING. Martha reviews the repair, scores it, and the job ends."""
        if self.job is None or self.finished:
            raise RuntimeError("No repair is in progress")
        if not self.sequence:
            return {"ok": False, "message": "You haven't done anything yet. Inspect it, then choose your actions in order."}

        job = self.job
        steps, actions = job["steps"], job["actions"]
        total = len(steps)
        chosen_steps = [actions[i]["step"] for i in self.sequence]
        correct_positions = required_order_score(chosen_steps)
        correct = len(correct_positions)
        fraction = correct / total
        scale = round(correct * SCALE_MAX / total / 10) * 10

        player_rows, wrong_labels, why_not = [], 0, []
        placed_steps = set()
        for pos, i in enumerate(self.sequence):
            act = actions[i]
            if act["step"] is None:
                status = "wrong"
                wrong_labels += 1
                why_not.append((act["label"], act["why"]))
            elif pos in correct_positions:
                status = "correct"
                placed_steps.add(act["step"])
            else:
                status = "order"
            player_rows.append({"label": act["label"], "status": status})
        chosen_set = {s for s in chosen_steps if s is not None}
        required_rows = [{"label": s["label"], "status": "correct" if n in placed_steps
                          else ("order" if n in chosen_set else "missed")} for n, s in enumerate(steps)]

        wrong_points = WRONG_POINTS * wrong_labels

        # a stored part is used when the player chose the repair action that fits it
        part = None
        part_points = 0
        part_step_n = next((n for n, s in enumerate(steps) if s["part"]), None)
        if part_step_n is not None and part_step_n in chosen_set:
            name = steps[part_step_n]["part"]
            for i, comp in enumerate(self.state["components"]):
                if comp["name"] == name:
                    self.state["components"].pop(i)
                    part, part_points = {"name": name, "stored": True}, PART_BONUS
                    self.parts_used += 1
                    break
            else:
                part = {"name": name, "stored": False}

        success = fraction >= SUCCESS_FRACTION
        relic_bonus = RELIC_BONUS if (job["relic"] and success) else 0
        points = scale + wrong_points + part_points + relic_bonus

        reward = None
        retry = False
        if job["relic"]:
            if success:
                reward = grant_relic_reward(self.state, job["name"])
                self.relics_restored += 1
            elif self._entry is not None:
                self.state["workshop_queue"].append(self._entry)     # not lost: it can be tried again
                self._skipped.add(id(self._entry))
                retry = True

        self.state["score"] = max(0, self.state["score"] + points)
        self.finished = True
        self.jobs_done += 1
        self.successes += success
        self.complete = self.state["score"] >= self.END
        self.dropback = self.state["score"] < self.DROP

        faults = [f["name"] for f in job["findings"] if f["faulty"]]
        marked = [job["findings"][i]["name"] for i in sorted(self.marks)]
        percent = round(100 * fraction)
        return {
            "ok": True, "name": job["name"], "relic": job["relic"],
            "required_rows": required_rows, "player_rows": player_rows,
            "correct": correct, "total": total, "percent": percent,
            "scale_points": scale, "wrong_count": wrong_labels, "wrong_points": wrong_points,
            "part": part, "part_points": part_points, "relic_bonus": relic_bonus,
            "points": points, "success": success,
            "faults": faults, "marked": marked,
            "found": [n for n in faults if n in marked],
            "missed_faults": [n for n in faults if n not in marked],
            "wrong_marks": [n for n in marked if n not in faults],
            "why_not": why_not,
            "comment": next(text for floor, text in COMMENTS if percent >= floor),
            "relic_reward": reward, "relic_retry": retry,
            "complete": self.complete, "dropback": self.dropback,
        }