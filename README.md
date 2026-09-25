# Circular Silo

**Author:** Deepthi Nenavath
**Student ID:** dn24002

---

## 1. Game Concept

*The Circular Silo* is a single-player resource-management and repair game set in an underground Silo where resources are limited and manufactured objects are difficult to replace.

The player joins the Mechanical Department and is responsible for processing objects recovered by scavenging teams. The player must learn to make appropriate decisions about whether an object should be **reused, repaired, have its materials recovered, or be incinerated**.

The game progresses through five levels. Each level introduces a new skill:

1. **Basic Sorting** - deciding what should happen to recovered objects.
2. **Material Recovery** - recovering useful components from objects.
3. **Learning to Repair** - repairing simple objects with guidance from Martha.
4. **Advanced Repair** - repairing more complex objects with limited guidance.
5. **Independent Repair** - repairing objects without Martha's assistance.

The main gameplay is based on decision-making, inspection, resource recovery, and repair rather than simply collecting points.

<img width="336" height="1173" alt="d1_overall" src="https://github.com/user-attachments/assets/0972c590-f0f2-4d73-b7bc-ef0bb09deadc" />


---

## 2. Story / Theme

In the future, a technological war between nations leads to the development of advanced nanotechnology controlled by artificial intelligence. The technology is inexpensive and can be produced on a massive scale, but its uncontrolled use causes catastrophic environmental damage.

The Earth's surface becomes contaminated with toxic substances, making the air unsafe for humans to breathe. The remaining population moves underground into enormous shelters known as **Silos**.

Life inside the Silo depends on limited resources. New products and replacement parts cannot simply be produced whenever something breaks. Objects recovered by scavenging teams are therefore brought to the Mechanical Department, where workers determine what can still be used.

The player joins the Mechanical Department as an inexperienced worker. **Martha Walker**, an experienced mechanic who runs an electronics workshop, becomes the player's mentor. She teaches the player how to inspect objects, identify useful components, recover materials, and eventually repair damaged equipment.

As the player progresses, Martha gradually provides less assistance. By the final level, the player must apply what they learned independently.

The story establishes the setting, but the environmental theme is primarily communicated through the player's decisions and actions.

---

## 3. Social Good Theme

### Real-World Issue

The game addresses **resource waste and unsustainable consumption**. Modern products often require raw materials, energy, manufacturing, transportation, and other resources before they reach consumers. When usable products or components are discarded unnecessarily, these resources are lost.

The game focuses on the idea that an object reaching the end of one use does not necessarily mean that it has become useless.

Players are encouraged to consider whether an object can:

* be reused,
* be repaired,
* have useful materials or components recovered,
* or, only when no other practical option remains, be discarded.

### Related UN Sustainable Development Goal

The main SDG addressed by the game is:

**SDG 12: Responsible Consumption and Production**

The game relates to SDG 12 by focusing on extending the useful life of products, recovering materials, reducing unnecessary disposal, and making more informed decisions about resources.

### Why This Issue Was Chosen

The issue was chosen because resource consumption and waste are directly connected to everyday decisions about products. Repair, reuse, and material recovery provide practical ways of thinking about how products can remain useful for longer instead of immediately becoming waste.

### Who Could Benefit?

The game is primarily intended to help players, particularly students and young people, think about:

* the value of existing products and materials,
* the consequences of unnecessary disposal,
* repair as an alternative to replacement,
* and how individual decisions can affect resource use.

---

## 4. Social Good Integration into Gameplay

The social-good theme is directly integrated into the core game mechanics.

The player does not simply receive information about sustainability. They must **make decisions that determine what happens to every object**.

A recovered object can be directed toward four outcomes:

<img width="640" height="463" alt="image" src="https://github.com/user-attachments/assets/3c480b80-002d-4c4c-8e4c-da3021110f1d" />



The consequences of these decisions are incorporated into the gameplay.

For example, a repairable object sent for incineration results in a score penalty, while correctly identifying it as repairable allows the player to send it to Martha's workshop.

Material recovery also has a gameplay purpose rather than being a separate educational activity. Components recovered in Level 2 can later be used as replacement parts during repair.

This creates a connection between the player's decisions:

**Sorting → Material Recovery → Repair → Reuse**

The player therefore experiences the resource cycle through gameplay rather than only reading about it.

---

## 5. Intended Impact / Message

The main message of the game is:

> **An object being broken does not automatically mean that it has become waste.**

The game is intended to encourage players to think about the possibilities that exist before disposal.

By progressing through the levels, players should experience the difference between:

* identifying an object,
* deciding what should happen to it,
* recovering useful materials,
* repairing damaged objects,
* and eventually making these decisions independently.

The game should communicate that repair and material recovery require decision-making and effort, while unnecessary disposal can result in the loss of useful resources.

The intended message can be evaluated through **player performance and understanding**. For example, the developer can compare players' sorting decisions between the beginning and later parts of the game, observe whether players increasingly identify repairable objects correctly, and optionally ask players a few short questions after gameplay about the choices they made.

---

# 6. Gameplay and Rules

## 6.1 Game Structure

The game is **single-player** and is divided into five levels.

Each level has a score target of **100 points**. The player must reach the required score to progress.

The five levels are:

| Level | Main Skill         | Main Activity                          |
| ----- | ------------------ | -------------------------------------- |
| 1     | Sorting            | Decide what should happen to objects   |
| 2     | Material Recovery  | Recover useful components              |
| 3     | Basic Repair       | Learn repair through Martha's guidance |
| 4     | Advanced Repair    | Repair with limited guidance           |
| 5     | Independent Repair | Repair without Martha's assistance     |

---

## 6.2 Level 1 - Sorting

Objects arrive from the scavenging team.

The player inspects each object and decides what should happen to it:

* **Reuse** - the object can still be used.
* **Repair** - the object is damaged but can be repaired.
* **Recover** - useful materials or components can be recovered.
* **Incinerate** - there is no practical reuse, repair, or material recovery option.

The selected destination determines what happens next.

### Level 1 Scoring

```text
Correct sorting decision       +10 points
Incorrect sorting decision      -5 points
```

The player continues sorting objects until they reach **100 points**.

```text
                  Scavenged Object
                         ↓
                       Inspect
                         ↓
                  Player Decision
                         ↓
        ┌────────┬────────┬──────────┐
        ↓        ↓        ↓          ↓
      Reuse    Repair   Recover   Incinerate
        ↓        ↓        ↓          ↓
    Recycling  Martha's  Level 2   Incineration
    Department Workshop
```

---

## 6.3 Level 2 - Material Recovery

Level 2 uses objects that the player previously classified as **Recover**.

The player must inspect these objects and identify which materials or components can be recovered.

The recovered components are stored and become available later as potential replacement parts in the repair levels.

The player receives points for successfully identifying and recovering useful components.

<img width="640" height="759" alt="d4_level2" src="https://github.com/user-attachments/assets/543c1fc9-59cd-442a-acbb-077aaa0030c0" />



The player continues until reaching **100 points**.

---

## 6.4 Level 3 - Learning to Repair

Level 3 introduces Martha's workshop.

Martha provides step-by-step instructions and acts as a tutorial. The player learns how to inspect components, identify broken parts, and perform basic repair actions.

The player is given several possible actions, but only some are correct.

For example, the player might see:

```text
A. Remove battery
B. Remove speaker
C. Connect wire
D. Replace component
E. Remove antenna
F. Test device
```

Martha's instructions determine which actions are required.

The player must select the appropriate action and perform the repair in the intended sequence.

Correct actions give positive points. Incorrect actions give negative points.

At the end of the repair, the player can select **"Done Fixing"**, after which the game checks whether the required repair was completed correctly.


<img width="640" height="857" alt="d5_level3" src="https://github.com/user-attachments/assets/a74341d3-b3ec-41a0-a971-f6eef4d8ad2c" />


The player must reach **100 points** to progress to Level 4.

---

## 6.5 Level 4 - Advanced Repair

Level 4 reduces Martha's assistance.

Before the repair begins, Martha provides general advice about the object, but she does not tell the player every action individually.

The player must:

1. Inspect the object.
2. Identify the broken components.
3. Determine which actions are necessary.
4. Select the actions from a larger set of possible actions.
5. Perform them in the correct order.
6. Select **"Done Fixing"** when finished.

Martha then reviews the completed repair.

The game compares the player's actions with the required repair sequence and calculates a repair score.

For example:

```text
Required sequence:

A → B → C → D → E

Player sequence:

A → B → D → C → E

Correct actions: 4 / 5
```

The player would receive a score corresponding to the percentage of the repair completed correctly.

An example scoring scale could be:

```text
100% correct       → 50 points
80% correct        → 40 points
60% correct        → 30 points
40% correct        → 20 points
20% correct        → 10 points
0% correct         → 0 points
```

These values can be adjusted during testing.

<img width="640" height="786" alt="d6_level4" src="https://github.com/user-attachments/assets/fb6d7dd6-e955-44fd-9d2a-ec1291f443fc" />


The player continues repairing objects until reaching **100 points**.

---

## 6.6 Level 5 - Independent Repair

Level 5 is the final challenge.

Martha no longer provides repair instructions or reviews the repair before the final result.

The player must independently apply the knowledge gained from Levels 3 and 4.

The player receives a damaged object, inspects it, identifies the problem, chooses the required repair actions, uses available recovered components when necessary, and determines the correct order of actions.

<img width="640" height="776" alt="d7_level5" src="https://github.com/user-attachments/assets/3ee1a99a-5df3-49bc-9d39-83d59d1d82e9" />


The final score is based on the correctness of the player's repair decisions and actions.

---

## 6.7 Scoring and Mistakes

The game uses positive and negative points to show the consequences of player decisions.

### Basic scoring

```text
Correct sorting                  +10
Correct material recovery        +10
Correct repair action             +5
Successful repair                +15
Incorrect sorting                 -5
Incorrect recovery action         -5
Incorrect repair action            -5
```

The exact values can be adjusted during playtesting.

The important rule is that **correct decisions increase the player's progress while mistakes reduce the score**.

### Level Threshold

Each level requires **100 points** to progress.

The game also keeps track of the player's previous level threshold.

If the player's score falls to or below the threshold required for the previous level, the player returns to that level and must earn the required points again.

<img width="640" height="494" alt="d8_dropback" src="https://github.com/user-attachments/assets/8eda5606-1270-4a40-bb12-7b4b16e3727f" />

This creates a risk-and-reward system where careless decisions can cause the player to lose progress.

---

## 6.8 Typical Game Session

A typical session follows the progression below:

```text
Receive Object
      ↓
Inspect Object
      ↓
Make Decision
      ↓
Perform Required Activity
      ↓
Receive Points / Penalty
      ↓
Check Level Score
      ↓
Continue with Next Object
```

The specific activity depends on the level:

```text
Level 1 → Sort
Level 2 → Recover Materials
Level 3 → Follow Repair Instructions
Level 4 → Perform Advanced Repair
Level 5 → Repair Independently
```

---

# 7. Winning / Losing / Game Objectives

## Main Objective

The player's main objective is to successfully progress through all five levels by making appropriate decisions about objects and learning how to recover and repair them.

The ultimate goal is to complete the final independent repair challenge.

## Progression

```text
Level 1 → 100 points → Level 2
Level 2 → 100 points → Level 3
Level 3 → 100 points → Level 4
Level 4 → 100 points → Level 5
Level 5 → Final Repair → Game Complete
```

## Losing / Losing Progress

The player does not have a traditional "game over" screen after a single mistake.

Instead, incorrect decisions reduce the player's score. If the score falls to or below the previous level's threshold, the player returns to that level and must earn the required points again.

This makes mistakes meaningful without immediately ending the game.

---

# 8. Platform and Development Tools

**Platform:** PC

**Programming Language:** Python

**Game Framework:** Pygame

**Version Control:** Git

**Repository:** GitHub 

Pygame will be used to implement the game's interface, object interactions, scoring system, levels, repair activities, and progression system.

Git and GitHub will be used for version control and development of the project.

---

# 9. Originality / Existing Games

Games involving recycling and waste management already exist, including games that teach players to sort waste into different categories. Other games focus on repair, crafting, or resource management.

The proposed project combines these ideas into a single progression-based gameplay system.

The main contribution is the connection between the different activities:

```text
              SORT
                ↓
          RECOVER MATERIALS
                ↓
          STORE COMPONENTS
                ↓
             REPAIR
                ↓
             REUSE
```

Recovered components are not simply collected for points. They become potential resources for later repairs.

The game also uses a learning progression:

```text
Sorting
   ↓
Material Recovery
   ↓
Guided Repair
   ↓
Advanced Repair
   ↓
Independent Repair
```

This means the player's earlier actions directly affect later gameplay.

The Silo setting provides the narrative context for why resources are limited and why repairing and recovering components are important. Martha's workshop provides the game's tutorial and mentorship system, while the gradual removal of her assistance allows the final level to test whether the player can apply the repair process independently.

The project therefore combines **resource sorting, material recovery, repair mechanics, limited resources, and progressive learning** into one game rather than treating sustainability as only a narrative theme.
