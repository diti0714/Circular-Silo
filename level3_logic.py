"""Level 3 - Learning to Repair: the rules only (no pygame, so they can be tested on their own).

The screen code lives in level3.py.

How it works: the objects the player sent to "Repair" in Level 1 arrive at Martha's workshop.
Martha explains the repair one step at a time. The player has six possible actions (A-F):
four are the repair steps and two are wrong. The player picks the action that matches
Martha's current instruction, then presses DONE FIXING when every step is done.
Some steps need a replacement part, which is taken from the parts the player recovered in Level 2.
"""
import random

from level1_logic import ITEMS, RELICS, TARGET

LEVEL_START = 2 * TARGET    # Level 3 begins at 200 points ...
LEVEL_END = 3 * TARGET      # ... and is finished at 300 points
DROPBACK_BELOW = LEVEL_START  # finishing a job below 200 sends the player back to Level 2

ACTION_POINTS = 5           # correct repair action
WRONG_POINTS = -5           # wrong action, or a right action at the wrong time
PART_BONUS = 5              # extra for using a part recovered in Level 2
SUCCESS_POINTS = 15         # successful repair
RELIC_BONUS = 30            # extra for a successful relic repair
HINT_POUCH_MAX = 3
RECENT_MEMORY = 2

AFFIRMATIONS = ["Good.", "That's it.", "Nicely done.", "Exactly right.", "Well done."]


def _s(label, say, part=None):
    """A repair step: the action's label, what Martha says, and the stored part it needs (if any)."""
    return {"label": label, "say": say, "part": part}


def _w(label, why):
    """A wrong action, and why Martha says it is wrong."""
    return {"label": label, "why": why}


# One job per object that is correctly sorted to Repair in Level 1 (5 ordinary objects + 8 relics).
JOBS = {
    # --- ordinary objects -------------------------------------------------------------
    "Table fan": {
        "steps": [
            _s("Unplug the fan", "Safety first. Before you touch anything, cut the power to the fan."),
            _s("Open the motor cover", "Now take the cover off the motor so we can see the wiring."),
            _s("Replace the loose wire", "That wire has worked loose and cut through. Swap it for a good one from storage.", "Wiring"),
            _s("Test the fan", "Close it up, plug it in and see if those blades keep turning."),
        ],
        "wrong": [
            _w("Replace the motor", "The motor is fine. We never waste a good motor."),
            _w("Bend the blades", "The blades are straight. Leave them alone."),
        ],
    },
    "Kettle": {
        "steps": [
            _s("Unplug the kettle", "First make sure it is unplugged and cold."),
            _s("Cut off the frayed cord", "The cord is frayed near the plug. Cut away the damaged part."),
            _s("Attach a new cord", "Fit a good length of wiring from storage as the new cord.", "Wiring"),
            _s("Test the kettle", "Fill it, switch it on and check that it heats."),
        ],
        "wrong": [
            _w("Replace the element", "The heating element is fine. The cord was the problem."),
            _w("Patch the body", "The body has no cracks. There is nothing to patch."),
        ],
    },
    "Desk radio": {
        "steps": [
            _s("Unplug the radio", "Cut the power first. Always."),
            _s("Remove the back panel", "Take off the back panel so we can reach the circuit."),
            _s("Replace the loose wire", "One connection is loose and corroded. Replace that wire with a good one.", "Wiring"),
            _s("Test the sound", "Power it up, turn the dial and listen for a clear sound."),
        ],
        "wrong": [
            _w("Replace the speaker", "The speaker works when tapped. It is fine."),
            _w("Replace the antenna", "The antenna is not the problem."),
        ],
    },
    "Leather boots": {
        "steps": [
            _s("Clean the sole edge", "Scrape the old glue and dirt off the sole and the boot."),
            _s("Apply glue", "Spread a thin, even layer of glue on both surfaces."),
            _s("Press and clamp the sole", "Press the sole on firmly and clamp it while it sets."),
            _s("Check the bond", "Once it has set, flex the boot and check the sole holds."),
        ],
        "wrong": [
            _w("Cut off the sole", "The sole is fine. It just needs sticking back on."),
            _w("Replace the laces", "The laces are fine. Leave them."),
        ],
    },
    "Backpack": {
        "steps": [
            _s("Straighten the teeth", "The zipper teeth are bent. Straighten them gently with pliers."),
            _s("Rub wax on the zipper", "A little wax along the teeth helps the slider glide."),
            _s("Work the slider free", "Now ease the slider back and forth until it moves."),
            _s("Test the zipper", "Open and close it a few times to be sure."),
        ],
        "wrong": [
            _w("Cut the fabric", "The fabric is fine. Never cut a good bag."),
            _w("Replace the straps", "The straps are strong. Leave them."),
        ],
    },

    # --- relics --------------------------------------------------------------------------
    "Pocket watch": {
        "steps": [
            _s("Open the case back", "Be gentle. Open the back of the case to reach the movement."),
            _s("Clean the gears", "Old oil has gummed it up. Clean the gears with a soft brush."),
            _s("Free the winding stem", "The winding stem is stuck. Ease it loose with a drop of oil."),
            _s("Wind and test the watch", "Close the case, wind it and see if it keeps time."),
        ],
        "wrong": [
            _w("Replace all the gears", "The gears are intact. Never throw away old brass."),
            _w("Force the stem", "Never force old metal. It will snap."),
        ],
    },
    "Music player": {
        "steps": [
            _s("Remove the old battery", "The battery is corroded. Take it out carefully."),
            _s("Clean the contacts", "Scrub the corrosion off the metal contacts."),
            _s("Fit a new battery", "Fit a good battery from our storage.", "Battery"),
            _s("Play a test track", "Put it together and press play. Let us hear it."),
        ],
        "wrong": [
            _w("Replace the circuit board", "The circuit board is fine."),
            _w("Remove the headphone jack", "That is not what is broken."),
        ],
    },
    "Instant camera": {
        "steps": [
            _s("Open the camera body", "Open the body carefully. The shutter mechanism is inside."),
            _s("Clean the shutter", "Dust is jamming it. Clean the shutter mechanism."),
            _s("Replace the switch", "The button's switch is worn out. Fit a good one from storage.", "Switch"),
            _s("Test the shutter", "Close it up and click the shutter a few times."),
        ],
        "wrong": [
            _w("Replace the lens", "The lens is clear. Leave it."),
            _w("Remove the flash", "The flash is not the problem."),
        ],
    },
    "Toy robot": {
        "steps": [
            _s("Inspect the arm socket", "Look at the empty socket first. We need to know what fits there."),
            _s("Shape a new tin arm", "Cut and bend a new arm from scrap tin. Match the other one."),
            _s("Fit gears in the joint", "Fit gears from our storage into the arm joint so it can move.", "Gears"),
            _s("Wind up and test", "Wind it up and watch it move."),
        ],
        "wrong": [
            _w("Repaint the robot", "The paint is still bright. Do not touch it."),
            _w("Remove the other arm", "Never take apart the good side."),
        ],
    },
    "Travel book": {
        "steps": [
            _s("Flatten the pages", "Press the pages flat so they sit evenly."),
            _s("Glue the spine", "Brush a thin, even layer of glue along the torn spine."),
            _s("Bind with cloth tape", "Lay cloth tape over the spine for strength."),
            _s("Press and dry", "Press it under a weight until it is dry."),
        ],
        "wrong": [
            _w("Trim the pages", "The pages are fine. Cutting them would lose words."),
            _w("Remove the cover", "The cover stays. It is part of the book."),
        ],
    },
    "Hand-crank radio": {
        "steps": [
            _s("Oil the crank", "The crank is stiff. A drop of oil on the joint will free it."),
            _s("Open the speaker panel", "Open it up. The crackle comes from the speaker wiring."),
            _s("Replace the speaker wire", "Replace the damaged speaker wiring with a good one.", "Wiring"),
            _s("Crank and test", "Crank it up and listen for a clear sound."),
        ],
        "wrong": [
            _w("Replace the crank", "The crank is only stiff. It works."),
            _w("Remove the antenna", "The antenna is fine."),
        ],
    },
    "Data drive": {
        "steps": [
            _s("Open the cracked case", "Open what is left of the casing. Careful with the chip inside."),
            _s("Lift out the chip", "Lift the chip out gently. Do not touch its pins."),
            _s("Mount it on a new board", "Mount the chip on a good circuit board from storage.", "Circuit board"),
            _s("Test the connection", "Connect it and check that it powers up."),
        ],
        "wrong": [
            _w("Wipe the chip", "Never scrub a chip. You would destroy the data."),
            _w("Smash the old case", "Gently, please. Never smash it."),
        ],
    },
    "Compass": {
        "steps": [
            _s("Remove the glass cover", "Lift off the cracked glass cover carefully."),
            _s("Clean the pivot", "Wipe the pivot point clean and dry."),
            _s("Free the needle", "The needle is stuck, not broken. Free it gently."),
            _s("Test the compass", "Hold it level and see if it points north."),
        ],
        "wrong": [
            _w("Replace the needle", "The needle is fine. It is only stuck."),
            _w("Magnetize the case", "That would throw off the reading."),
        ],
    },
}

# What a restored relic gives: a story fragment from the Before Times, and Relic Wisdom (a one-use hint).
RELIC_INFO = {
    "Pocket watch": {
        "story": "Scratched inside the case: 'For Anna, so you are never late.' People once carried the time in their pockets, and gave it away as a gift.",
        "hint_type": "step_order",
        "hint": "Shows the correct order of the first 2 steps in the next repair",
    },
    "Music player": {
        "story": "The last recording on it is a child laughing, then a voice saying, 'Again!' Someone once kept their favourite sounds in their pocket.",
        "hint_type": "recoverable_parts",
        "hint": "Shows which of the next 3 objects has the most recoverable parts",
    },
    "Instant camera": {
        "story": "One photo is still stuck inside: a crowd under a wide blue sky, all squinting at the sun. Nobody in the Silo has seen a sky that colour.",
        "hint_type": "hidden_defect",
        "hint": "Reveals one hidden defect on the next object you inspect",
    },
    "Toy robot": {
        "story": "A name is painted on its foot: 'Max.' It was loved so much that the paint wore off its hands. Some things are made only to be loved.",
        "hint_type": "free_part",
        "hint": "Adds a free spare part to your recovered-components storage",
    },
    "Travel book": {
        "story": "Its pages show beaches, forests and rivers, with notes in the margins: 'Go in spring!' People once planned journeys to places that were still there.",
        "hint_type": "trap_action",
        "hint": "Reveals which action in the list is a trap (wrong) action",
    },
    "Hand-crank radio": {
        "story": "It was built to work with no power at all, for storms and emergencies. The people before knew that one day the lights might go out.",
        "hint_type": "martha_step",
        "hint": "Restores Martha's guidance for one step, even in Level 5",
    },
    "Data drive": {
        "story": "Its label reads 'Family photos and recipes.' A tiny drive that holds a whole family's memories. Martha locks it away somewhere safe.",
        "hint_type": "player_choice",
        "hint": "Gives a hint of your choice (the rare, flexible one)",
    },
    "Compass": {
        "story": "Engraved on the lid: 'Always find your way home.' Even if the surface can't be walked any more, Martha says, a good compass still points true.",
        "hint_type": "sort_hint",
        "hint": "Highlights the correct sorting destination for one object in Level 1",
    },
}

def grant_relic_reward(state, name):
    """Story fragment, collection entry and Relic Wisdom hint for a restored relic (used by Levels 3 and 4)."""
    info = RELIC_INFO[name]
    collection = state.setdefault("relic_collection", [])
    if name not in collection:
        collection.append(name)

    pouch = state.setdefault("hint_pouch", [])
    replaced = None
    if len(pouch) >= HINT_POUCH_MAX:
        replaced = pouch.pop(0)["relic"]      # the oldest hint fades to make room
    pouch.append({"relic": name, "type": info["hint_type"], "text": info["hint"]})

    return {"name": name, "story": info["story"], "hint": info["hint"], "hint_type": info["hint_type"],
            "replaced": replaced, "collection_count": len(collection), "collection_total": len(RELIC_INFO)}


_ORDINARY_JOBS = [name for name in JOBS if name not in RELIC_INFO]
_RELIC_NAMES = {o["name"] for o in RELICS}


class Level3:
    """Hands out repair jobs and scores the player's actions.

    `state` is the shared game state from main.py. This level reads and updates:
      score            - the player's total score
      workshop_queue   - objects sent to Martha's workshop in Level 1 (entries: {"name", "relic"})
      components       - the parts storage filled in Level 2; replacement parts are taken from it
      relic_collection - names of the relics the player has restored
      hint_pouch       - Relic Wisdom hints earned (max 3), for use in later levels
    """

    def __init__(self, state, rng=None):
        self.state = state
        self.state.setdefault("score", 0)
        self.state.setdefault("workshop_queue", [])
        self.state.setdefault("components", [])
        self.state.setdefault("relic_collection", [])
        self.state.setdefault("hint_pouch", [])
        self.rng = rng or random.Random()

        self.job = None
        self.step = 0                 # index of the step Martha is explaining now
        self.done = set()             # indexes (in job["actions"]) of the actions already done
        self.actions_taken = 0
        self.finished = False         # the job was completed with DONE FIXING
        self.complete = False
        self.dropback = False
        self.sent_back = []           # objects that were sent here but have nothing to repair
        self._skipped = set()         # relic jobs the player set aside this session (by id)
        self._recent = []
        self._entry = None
        self._start_score = 0
        self._used_parts = []

        # stats for the end-of-level screen
        self.jobs_done = 0
        self.mistakes = 0
        self.parts_used = 0
        self.relics_restored = 0

    # ---- reading the current state ----------------------------------------------------------
    @property
    def score(self):
        return self.state["score"]

    @property
    def current_step(self):
        """The step Martha is explaining now, or None when every step is done."""
        if self.job is None or self.step >= len(self.job["steps"]):
            return None
        return self.job["steps"][self.step]

    @property
    def all_steps_done(self):
        return self.job is not None and self.step >= len(self.job["steps"])

    def parts_in_storage(self, name):
        return sum(1 for c in self.state["components"] if c["name"] == name)

    def can_set_aside(self):
        return self.job is not None and self.job["relic"] and self.actions_taken == 0 and not self.finished

    # ---- getting the next job ---------------------------------------------------------------
    def _take_from_queue(self):
        queue = self.state["workshop_queue"]
        for i, entry in enumerate(queue):
            if id(entry) in self._skipped:
                continue
            queue.pop(i)
            if entry["name"] in JOBS:
                return entry
            self.sent_back.append(entry["name"])     # nothing to repair: Martha sends it back
            return self._take_from_queue()
        return None

    def next_job(self):
        entry = self._take_from_queue()
        if entry is not None:
            name, from_queue = entry["name"], True
        else:
            # The queue is empty, so the scavenging team brings in more broken objects.
            fresh = [n for n in _ORDINARY_JOBS if n not in self._recent]
            name, from_queue = self.rng.choice(fresh or _ORDINARY_JOBS), False
        self._recent = (self._recent + [name])[-RECENT_MEMORY:]

        data = JOBS[name]
        steps = [dict(s) for s in data["steps"]]
        actions = [{"label": s["label"], "step": i, "why": None} for i, s in enumerate(steps)]
        actions += [{"label": w["label"], "step": None, "why": w["why"]} for w in data["wrong"]]
        # shuffle, but never leave the steps in the order they must be done
        while True:
            self.rng.shuffle(actions)
            order = [a["step"] for a in actions if a["step"] is not None]
            if order != sorted(order):
                break

        self.job = {"name": name, "relic": name in _RELIC_NAMES, "from_queue": from_queue,
                    "steps": steps, "actions": actions}
        self._entry = entry
        self.step = 0
        self.done = set()
        self.actions_taken = 0
        self.finished = False
        self._start_score = self.state["score"]
        self._used_parts = []
        return self.job

    def set_aside(self):
        """Put a relic job to the back of the queue for later (only before starting it)."""
        if not self.can_set_aside() or self._entry is None:
            return False
        self._skipped.add(id(self._entry))
        self.state["workshop_queue"].append(self._entry)
        self.job = None
        self._entry = None
        return True

    def abandon(self):
        """The player leaves mid-job: undo the job's points, return its parts, and re-queue it."""
        if self.job is not None and not self.finished:
            self.state["score"] = self._start_score
            self.state["components"].extend(self._used_parts)
            if self._entry is not None:
                self.state["workshop_queue"].insert(0, self._entry)
        self.job = None
        self._entry = None
        self._used_parts = []
        self.step = 0
        self.done = set()

    # ---- the player's actions -----------------------------------------------------------------
    def choose(self, index):
        """The player picks action `index`. Returns a result dict (kind: correct / wrong / early / ignored)."""
        if self.job is None or self.finished:
            raise RuntimeError("No repair is in progress")
        actions = self.job["actions"]
        if not 0 <= index < len(actions) or index in self.done:
            return {"kind": "ignored", "points": 0, "headline": "", "message": "", "good": False}
        if self.all_steps_done:
            return {"kind": "ignored", "points": 0, "headline": "", "message": "", "good": False}

        action = actions[index]
        self.actions_taken += 1

        if action["step"] == self.step:
            step = self.job["steps"][self.step]
            points = ACTION_POINTS
            message = self.rng.choice(AFFIRMATIONS)
            if step["part"]:
                for i, comp in enumerate(self.state["components"]):
                    if comp["name"] == step["part"]:
                        self._used_parts.append(self.state["components"].pop(i))
                        self.parts_used += 1
                        points += PART_BONUS
                        message += f" You used the {step['part'].lower()} you recovered ({PART_BONUS:+d})."
                        break
                else:
                    message += f" We have no {step['part'].lower()} in storage, so I'll use a worn spare from my shelf."
            self.done.add(index)
            self.step += 1
            kind, headline, good = "correct", "STEP DONE", True
            if self.all_steps_done:
                message += " That's every step. Press DONE FIXING and we'll check it over."
        elif action["step"] is None:
            kind, headline, good, points = "wrong", "WRONG ACTION", False, WRONG_POINTS
            message = action["why"]
            self.mistakes += 1
        else:
            kind, headline, good, points = "early", "WRONG ORDER", False, WRONG_POINTS
            message = "Right idea, but not yet. Follow my instructions in order."
            self.mistakes += 1

        self.state["score"] = max(0, self.state["score"] + points)
        return {"kind": kind, "points": points, "headline": headline, "message": message, "good": good}

    def done_fixing(self):
        """The player presses DONE FIXING. Finishes the job if every step is done."""
        if self.job is None or self.finished:
            raise RuntimeError("No repair is in progress")
        if not self.all_steps_done:
            left = len(self.job["steps"]) - self.step
            return {"ok": False, "kind": "notdone", "points": 0, "headline": "NOT FINISHED YET", "good": False,
                    "message": f"We're not done. {left} step{'s' if left != 1 else ''} still to do. Follow my instructions.",
                    "relic_reward": None, "complete": False, "dropback": False}

        points = SUCCESS_POINTS
        headline, message = "REPAIR COMPLETE", f"The {self.job['name'].lower()} works again."
        reward = None
        if self.job["relic"]:
            points += RELIC_BONUS
            headline = "RELIC RESTORED"
            message = f"The {self.job['name'].lower()} is saved. Relic bonus {RELIC_BONUS:+d}."
            reward = self._relic_reward(self.job["name"])
            self.relics_restored += 1

        self.state["score"] = max(0, self.state["score"] + points)
        self.finished = True
        self.jobs_done += 1
        self.complete = self.state["score"] >= LEVEL_END
        self.dropback = self.state["score"] < DROPBACK_BELOW
        return {"ok": True, "kind": "done", "points": points, "headline": headline, "message": message,
                "good": True, "relic_reward": reward, "complete": self.complete, "dropback": self.dropback}

    def _relic_reward(self, name):
        return grant_relic_reward(self.state, name)