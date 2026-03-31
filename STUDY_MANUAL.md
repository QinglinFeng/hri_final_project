# Study Manual: Robot Active Learning (Cakmak et al., 2010 Replication)

**Study title:** Designing Interactions for Robot Active Learners
**Robot:** Pepper (SoftBank Robotics)
**Estimated time per participant:** 60–75 minutes

---

## Table of Contents

1. [Pre-Study Checklist](#1-pre-study-checklist)
2. [Room Setup](#2-room-setup)
3. [Software Startup Procedure](#3-software-startup-procedure)
4. [Participant Welcome Script](#4-participant-welcome-script)
5. [Task Instructions Script](#5-task-instructions-script)
6. [Per-Session Procedure](#6-per-session-procedure)
7. [WoZ Operation Guide](#7-woz-operation-guide)
8. [Between-Session Script](#8-between-session-script)
9. [Debriefing Script](#9-debriefing-script)
10. [Shutdown Procedure](#10-shutdown-procedure)
11. [Troubleshooting](#11-troubleshooting)
12. [Quick Reference Card](#12-quick-reference-card)

---

## 1. Pre-Study Checklist

Complete these the day before and 30 minutes before each session.

### Day Before
- [ ] Charge Pepper fully
- [ ] Confirm participant appointment and subject ID (e.g., `p01`, `p02`, ...)
- [ ] Print consent forms
- [ ] Print the [Quick Reference Card](#12-quick-reference-card) for the WoZ operator

### 30 Minutes Before
- [ ] Power on Pepper and place it at the table
- [ ] Place the black tablecloth on the table in front of Pepper
- [ ] Lay out all 24 paper cutout shapes (4 colors × 3 shapes × 2 sizes) in a tray nearby
- [ ] Connect laptop to the same Wi-Fi network as Pepper
- [ ] Confirm Pepper's IP address: press the chest button once → Pepper says its IP
- [ ] Launch all three software components (see §3)
- [ ] Run a test turn: show any two shapes, press ENTER, type "Pepper, is this a HOUSE?" → confirm Pepper speaks
- [ ] Open WoZ panel and confirm it shows session status

### Shape Inventory (24 pieces total)

| Color  | Square S | Square L | Triangle S | Triangle L | Circle S | Circle L |
|--------|----------|----------|------------|------------|----------|----------|
| Pink   | ✓        | ✓        | ✓          | ✓          | ✓        | ✓        |
| Green  | ✓        | ✓        | ✓          | ✓          | ✓        | ✓        |
| Yellow | ✓        | ✓        | ✓          | ✓          | ✓        | ✓        |
| Orange | ✓        | ✓        | ✓          | ✓          | ✓        | ✓        |

---

## 2. Room Setup

```
                    [ Pepper ]
                        |
          ┌─────────────────────────┐
          │   black paper.          │
          │   [ top shape ]         │
          │   [ bottom shape ]      │
          └─────────────────────────┘
                        |
              [ Participant chair ]

  [ Experimenter table — behind/side ]
  - Laptop with 3 terminals open
  - Shape tray within reach
  - Printed quick reference card
```

**Key positioning notes:**
- Pepper's camera looks down on the chair — the two shapes must be placed flat on the table, clearly visible, one above the other (top = farther from Pepper, bottom = closer to Pepper)
- Experimenter sits where they can see both the participant and the laptop screen, but are not in Pepper's camera view

---

## 3. Software Startup Procedure

Open **three terminal windows** on your laptop.

### Terminal 1 — API Server
```bash
cd /path/to/hri_final_project
source .venv/bin/activate
python -m hri_final_project.api_server --subject <SUBJECT_ID>
```
> Replace `<SUBJECT_ID>` with the participant's ID (e.g., `p01`).
> The terminal will print the session order for this participant.
> ✅ Ready when you see: `[Server] Listening on http://0.0.0.0:5000`

### Terminal 2 — WoZ Panel
```bash
cd /path/to/hri_final_project
source .venv/bin/activate
python woz_panel.py
```
> ✅ Ready when you see the dashboard with concept name and version space size.

### Terminal 3 — ROS + Pepper (Docker)
```bash
cd /path/to/hri_final_project
./docker/start_ros.sh <PEPPER_IP>
```
> ✅ Ready when you see: `naoqi_driver initialized` and `[camera_keepalive] First frame received`

### Terminal 4 — Pepper ROS Node
```bash
cd /path/to/hri_final_project
./docker/start_pepper_node.sh
```
> ✅ Ready when you see: `[Press ENTER when the object is in view]`

---

## 4. Participant Welcome Script

> *Greet the participant at the door and bring them to the room.*

---

**EXPERIMENTER:**

"Hi, welcome! Thanks for coming in today. My name is [name], and I'll be running the study with you.

Before we get started, I'll have you read and sign this consent form. Please take your time — feel free to ask me any questions."

> *Hand over the consent form. Wait for them to sign.*

"Great, thank you. Today you'll be interacting with Pepper, a social robot. Your job is to teach Pepper a concept — kind of like teaching a child what a word means by showing them examples.

The session will take about 60 to 75 minutes. You'll do four short teaching sessions. There are no right or wrong answers — we're studying how people naturally interact with the robot, not testing your performance.

Do you have any questions before we begin?"

> *Answer questions. Then guide them to the participant chair.*

---

## 5. Task Instructions Script

> *Participant is seated at the table. Pepper is on.*

---

**EXPERIMENTER:**

"In front of you, you'll see a black paper. During the study, you'll place two paper shape cutouts on it — one on top and one on the bottom, like this."

> *Demonstrate by placing a pink triangle (top) and a green square (bottom) on the cloth.*

"Each shape has a color, a shape type, and a size — small or large. You'll be teaching Pepper a secret concept using these shapes.

At the start of each session, I'll tell you the **name** of the concept — like 'HOUSE' or 'SNOWMAN' — and whether each example you show is a positive or negative example of that concept. You don't need to know the full definition — just teach the robot by example, the way you naturally would.

You can say things like:

- *'Pepper, this is a HOUSE.'*
- *'Pepper, this is not a HOUSE.'*
- *'Pepper, is this a HOUSE?'*
- *'Pepper, do you have any questions?'*
- *'Pepper, we're done.'*

Pepper will sometimes ask you to change one of the shapes. When it does, please make that change if you can.

I'll be sitting nearby to help if anything goes wrong. Ready to try a quick practice round?"

### Practice Round

> *Tell the participant the practice concept is "BIG PINK SHAPE" (any pink shape is positive).*
> *Do 2–3 turns. Do not log these (they happen before the server starts or you can restart the server after).*
> *After practice:*

"Great! Do you have any questions about what to do?"

> *Answer questions.*

"Now we'll start the real sessions. I'll tell you the concept name at the beginning of each one."

---

## 6. Per-Session Procedure

Repeat this for each of the 4 sessions. The **session order is printed in Terminal 1** when you start the server.

### 6.1 Starting a Session

**EXPERIMENTER:**

"In this session, you'll be teaching Pepper the concept: **[CONCEPT NAME]**.

Please pick any two shapes from the tray, place them on the cloth — one on top, one on the bottom — and begin teaching. Let me know when you're ready to start."

> *Wait for the participant to place shapes.*

> *In Terminal 3: press **ENTER** to trigger perception.*

> *Confirm the perceived object on the WoZ panel is correct. If perception is wrong, say:*
> *"Let me adjust the camera for a second" — reposition shapes if needed and press ENTER again.*

### 6.2 Each Turn

**What you (the WoZ operator) do each turn:**

1. Participant places shapes on the cloth and speaks their utterance
2. In Terminal 3: press **ENTER** → Pepper perceives the shapes
3. Confirm perceived object on WoZ panel
4. Type the participant's utterance at the `Teacher says:` prompt
5. Pepper speaks its response and gestures
6. Monitor the WoZ panel — watch the version space size and F1 score

> **Transcription tip:** Type exactly what the participant said. Claude will handle variations in phrasing. If they said something ambiguous, type your best interpretation.

### 6.3 Ending a Session

The session ends when:
- **The participant says they are done** (e.g., "Pepper, we're done") — type this into Terminal 3
- **Or you judge the session is complete** (VS converged to 1, or ~15–20 turns reached)

If you need to end the session yourself, type: `Pepper, we are done` in Terminal 3.

> *After Pepper says "Thank you for teaching me!":*

**EXPERIMENTER:** "Great, that's the end of this session. Let's take a short break before the next one."

---

## 7. WoZ Operation Guide

### What to Watch on the WoZ Panel

| Field | What it means | When to act |
|---|---|---|
| **VS Size** | Number of hypotheses still consistent | Getting smaller = robot is learning |
| **Convergence bar** | How close to a single answer | Full bar = robot has learned the concept |
| **F1 Score** | Accuracy vs. true concept (0–1) | 1.0 = perfect |
| **Last utterance** | What you typed | Check for typos |
| **Last response** | What Pepper said | Verify it makes sense |

### Handling Unusual Situations

**Participant says something ambiguous (e.g., "Pepper, good job"):**
→ Type it as-is. If Pepper responds with "Sorry, I didn't understand that," say to the participant: "You can try rephrasing that."

**Participant asks Pepper a question it can't answer:**
→ Type it. If Pepper says "Sorry, I didn't understand," you can prompt: "You might want to try asking it differently."

**Pepper asks to replace a piece the participant doesn't have:**
→ Say: "Pepper is asking for [piece]. Do you have that in the tray? If not, you can tell Pepper you don't have it, or choose the closest one you do have."

**Perception gives a clearly wrong result:**
→ Ask the participant to "hold on one moment," reposition the shapes, and press ENTER again before typing the utterance.

**AL Mode — robot queries every turn:**
→ This is expected. The participant may find this frequent. That's part of the study design. Do not intervene unless they are distressed.

**AQ Mode — robot never asks questions unless invited:**
→ Remind the participant: "Remember, you can ask Pepper if he has any questions."

---

## 8. Between-Session Script

> *After each session (except the last), give the participant a 2–3 minute break.*

---

**EXPERIMENTER:**

"Nice work! Take a short break — there's water on the table if you'd like some.

We have [X] more sessions after this. The next concept will be **[NEXT CONCEPT NAME]**. You'll notice Pepper might behave a little differently in each session — that's intentional. Just interact with it naturally."

> *After the break:*

"Ready to continue? Go ahead and place two shapes whenever you like."

---

## 9. Debriefing Script

> *After all 4 sessions, before the participant leaves.*

---

**EXPERIMENTER:**

"That's the end of the study — thank you so much for your time and patience!

Let me tell you a bit more about what we were studying. In each session, Pepper was using a different strategy for how it asks questions.

- In one session (**SL**), Pepper just listened passively and never asked questions.
- In another (**AL**), Pepper asked a question after every single example.
- In the third (**MI**), Pepper asked questions only when your examples weren't giving it new information.
- In the last (**AQ**), Pepper only asked when you explicitly invited it to.

We're studying which of these strategies feels most natural and helpful from a teacher's perspective — your experience matters a lot for that.

Did any of the sessions feel particularly natural or frustrating to you? I'd love to hear your thoughts."

> *Listen and take brief notes. These qualitative observations can complement the quantitative data.*

"Thank you again. Your data will be kept completely confidential. If you have any questions later, here's my contact information."

> *Hand over contact card / debrief sheet.*

---

## 10. Shutdown Procedure

After the participant leaves:

1. **Terminal 1** will print the full experiment summary table with F1 scores. Take a screenshot or note the values.
2. Log file is saved automatically at `logs/<subject_id>_experiment.jsonl`
3. Back up the log file immediately:
   ```bash
   cp logs/<subject_id>_experiment.jsonl ~/backup/
   ```
4. Stop all terminals with `Ctrl+C`
5. Power down Pepper: hold the chest button for 3 seconds

---

## 11. Troubleshooting

| Problem | Fix |
|---|---|
| Pepper doesn't speak | Check naoqi_driver is connected: `rostopic list` should show `/naoqi_driver/speech` |
| Perception returns wrong object | Reposition shapes under better lighting; ensure both shapes are fully visible and not overlapping |
| API server crashes | Restart Terminal 1 with same `--subject` ID; log file will append correctly |
| WoZ panel shows "cannot reach server" | Make sure Terminal 1 is running and no firewall is blocking port 5000 |
| VS size not decreasing | This can happen in SL mode (expected) or if all examples are uninformative; continue normally |
| Pepper says "Sorry, I didn't understand" repeatedly | Rephrase utterances more closely to the example scripts; Claude handles natural variation but very short phrases may fail |
| ROS node crashes | Restart Terminal 3/4; you may need to re-press ENTER once to re-sync |

---

## 12. Quick Reference Card

> *Print this page and keep it at the experimenter table during the study.*

---

### Session Order
Check Terminal 1 output at startup — the order is randomized per subject.

### Participant Utterance Examples

| Situation | What to type |
|---|---|
| Positive example | `Pepper, this is a HOUSE` |
| Negative example | `Pepper, this is not a HOUSE` |
| Test question | `Pepper, is this a HOUSE?` |
| Invite question (AQ mode) | `Pepper, do you have any questions?` |
| End session | `Pepper, we are done` |

### Concept Definitions (DO NOT SHARE WITH PARTICIPANT)

| Concept | Definition |
|---|---|
| HOUSE | Top = pink triangle, Bottom = any square |
| SNOWMAN | Top = small circle, Bottom = any circle |
| ALIEN | Top = green circle, Bottom = green (any shape/size) |
| ICE CREAM | Top = any circle, Bottom = yellow triangle |

### WoZ Turn Checklist (per turn)
1. ⬜ Participant places shapes
2. ⬜ Press **ENTER** in Terminal 3
3. ⬜ Confirm perception on WoZ panel
4. ⬜ Type utterance → press **ENTER**
5. ⬜ Pepper speaks and gestures
6. ⬜ Check WoZ panel for VS size and F1

### Key Terminal Commands
```
# If API server crashes:
python -m hri_final_project.api_server --subject <ID>

# If ROS node crashes:
python pepper_ros_node.py --server http://localhost:5000

# Backup log:
cp logs/<ID>_experiment.jsonl ~/backup/
```
