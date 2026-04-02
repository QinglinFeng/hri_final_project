# Setup Guide for New Computers

This guide walks through setting up the HRI experiment software on a new laptop.

---

## Prerequisites

- macOS (Intel or Apple Silicon)
- Wi-Fi connection to the same network as Pepper
- Pepper's IP address (press chest button once — Pepper says its IP)

---

## Step 1: Install Docker Desktop

1. Download Docker Desktop from [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Install and launch it
3. Verify it works:
   ```bash
   docker --version
   ```
   You should see something like `Docker version 29.x.x`

---

## Step 2: Clone the Repository

```bash
git clone <YOUR_REPO_URL>
cd hri_final_project
```

---

## Step 3: Set Up Python Environment

Make sure you have Python 3.11+:
```bash
python3 --version
```

Create and activate the virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[develop]"
```

---

## Step 4: Set Up the Anthropic API Key

1. Get the API key from the project owner
2. Create a `.env` file in the project root:
   ```bash
   echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
   ```

---

## Step 5: Disable AirPlay Receiver (macOS)

Port 5000 conflicts with AirPlay Receiver on macOS. Disable it:

`System Settings → General → AirDrop & Handoff → AirPlay Receiver → Off`

---

## Step 6: Build the Docker Image

This only needs to be done once per computer:

```bash
cd hri_final_project
./docker/start_ros.sh <PEPPER_IP>
```

Replace `<PEPPER_IP>` with Pepper's IP address (e.g. `128.237.235.109`).

The first run will take a few minutes to build the Docker image. Subsequent runs are fast.

---

## Step 7: Verify Everything Works

Run this quick check before a study session:

```bash
# Terminal 1 — API server
source .venv/bin/activate
python3 -m hri_final_project.api_server --subject test01

# Terminal 2 — ROS + Pepper (in a new terminal)
./docker/start_ros.sh <PEPPER_IP>

# Terminal 3 — Pepper node (in a new terminal, after naoqi_driver initializes)
./docker/start_pepper_node.sh
```

Place two shapes on the table, press **ENTER** in Terminal 3, type `Pepper, this is a HOUSE` — Pepper should speak a response.

---

## Running a Study Session

See `STUDY_MANUAL.md` for the full protocol. Here is the quick startup sequence:

### Terminal 1 — API Server
```bash
cd hri_final_project
source .venv/bin/activate
python3 -m hri_final_project.api_server --subject <SUBJECT_ID>
```
Wait for: `[Server] Listening on http://0.0.0.0:5000`

### Terminal 2 — ROS + Pepper
```bash
./docker/start_ros.sh <PEPPER_IP>
```
Wait for: `naoqi_driver initialized` and `[camera_keepalive] First frame received`

### Terminal 3 — Pepper Node
```bash
./docker/start_pepper_node.sh
```
Wait for: `[Press ENTER when the object is in view]`

### Terminal 4 — WoZ Panel (optional but recommended)
```bash
source .venv/bin/activate
python3 woz_panel.py
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `docker: command not found` | Docker Desktop is not running — open it from Applications |
| `Port 5000 already in use` | Disable AirPlay Receiver in System Settings |
| `naoqi_driver` crashes on start | Make sure Pepper is powered on and connected to the same Wi-Fi |
| `Perception failed` | Check that the API server is running and `.env` has the correct API key |
| `No camera image received` | Wait a few seconds after `naoqi_driver initialized` before pressing ENTER |
| Pepper doesn't speak | Make sure Terminal 2 (`start_ros.sh`) is still running |
| Pepper's head moves randomly | Log in to `http://<PEPPER_IP>` (user: `nao`, password: `pepper1001`) and turn off Autonomous Life |

---

## Pepper Physical Setup

1. Power on Pepper (press chest button once)
2. Wait ~2 minutes for boot — Pepper will say its IP address
3. Place Pepper in front of the black tablecloth table
4. Log in to `http://<PEPPER_IP>` → disable **Autonomous Life**
5. Tilt Pepper's head to face the table (run once after connecting):
   ```bash
   docker exec -it hri-ros bash
   source /opt/ros/noetic/setup.bash
   rostopic pub -1 /joint_angles naoqi_bridge_msgs/JointAnglesWithSpeed '{joint_names: [HeadPitch], joint_angles: [-0.3], speed: 0.2, relative: 0}'
   ```
6. Place two shapes on the tablecloth and press ENTER in Terminal 3 to verify perception

---

## Log Files

Experiment logs are saved automatically to:
```
logs/<subject_id>_experiment.jsonl
```

Back them up after each session:
```bash
cp logs/<subject_id>_experiment.jsonl ~/Desktop/
```
