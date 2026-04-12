---
title: My First Env
emoji: 💧
colorFrom: blue
colorTo: red
sdk: docker
app_port: 8000
pinned: false
---

# 💧 Smart Water Tank Environment

Welcome to the **Smart Water Tank** environment! This is an industrial simulation designed for AI agents to learn water resource management through the OpenEnv framework.

## 🎯 The Mission

The objective is to maintain the water level within the **Safe Zone (40% to 80%)**.

| Condition | Reward |
|-----------|--------|
| Safe Zone (40-80%) | 1.0 |
| Warning Zone | 0.2 |
| Disaster (Overflow/Empty) | 0.0 (Episode Ends) |

---

## 🚀 Setup and How to Use

### 1. Fork this Environment

Run this in your terminal to create your own version:

```bash
openenv fork swarnakishore/my_first_env --repo-id swarnakishore/my_first_env
```

### 2. Connect via Python

```python
from openenv.client import BaseEnv as EnvClient

env = EnvClient(url="https://swarnakishore-my-first-env.hf.space")
observation = env.reset(task_type="basic_balance")
print(f"Current Level: {observation.current_water_level}%")
```

### 3. Run with Docker

```bash
docker build -t smart-water-tank -f server/Dockerfile .
docker run -p 8000:8000 smart-water-tank
```

The environment server will be available at `http://localhost:8000`.

---

## 📝 Available Tasks

| Task | Difficulty | Description |
|------|-----------|-------------|
| `basic_balance` | Easy | Keep water level in the safe zone (40-80%) |
| `emergency_recovery` | Medium | Recover from critical levels and stabilize |
| `efficient_management` | Hard | Maintain balance while minimizing energy use |

---

## 📊 Baseline Scores (GPT-4o-mini)

| Task | Avg Score | Best | Worst |
|------|-----------|------|-------|
| Basic Balance | 0.87 | 0.96 | 0.52 |
| Emergency Recovery | 0.74 | 0.92 | 0.31 |
| Efficient Management | 0.65 | 0.88 | 0.18 |

---

## 🔍 Water Quality Monitoring

The environment includes **real-time water quality monitoring** based on turbidity levels. The system automatically evaluates water quality and provides actionable recommendations:

| Quality Status | Condition | Recommendation |
|---------------|-----------|----------------|
| ✅ **GOOD** | Turbidity ≤ 5 NTU | Water quality is good. No action needed. |
| ❌ **BAD** | Turbidity > 5 NTU | Turbidity high — clean the tank. |

- Water turbidity **increases naturally over time** as the tank operates
- Resetting the environment simulates **cleaning/changing the water** (turbidity resets to clean levels)
- Quality status and recommendation are included in every observation and API response

---

## 📱 Remote Pump Control — Access From Anywhere

Control the water pump from **any device, anywhere in the world** using the deployed API:

```bash
# Deployed URL (accessible from any mobile phone or computer)
https://swarnakishore-my-first-env.hf.space
```

### Turn Pump ON from your phone:
```bash
curl -X POST https://swarnakishore-my-first-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"motor_status": 1}'
```

### Turn Pump OFF:
```bash
curl -X POST https://swarnakishore-my-first-env.hf.space/step \
  -H "Content-Type: application/json" \
  -d '{"motor_status": 0}'
```

### Check current status (water level + quality):
```bash
curl https://swarnakishore-my-first-env.hf.space/state
```

The response includes `quality_status` (`GOOD` / `BAD`) and `recommendation` so you always know if the tank needs cleaning or water change.

> **💡 Tip:** You can use any HTTP client app on your phone (like **HTTP Shortcuts** on Android or **Shortcuts** on iOS) to create one-tap buttons for pump ON/OFF control.

---

## 🔧 Action and Observation Space

**Action:** `MotorAction` — Set `motor_status` to `1` (ON) or `0` (OFF).

**Observation:** `WaterTankObservation` — Returns current water level, demand rate, inflow rate, overflow/empty status, `quality_status`, and `recommendation`.

---

## 📂 Project Structure

```
my_first_env/
├── README.md                            # Configuration and Documentation
├── openenv.yaml                         # Environment Manifest
├── pyproject.toml                       # Project configuration
├── uv.lock                             # UV lock file for dependencies
├── models.py                           # Action/Observation/State Models & Graders
├── client.py                           # OpenEnv Client
├── inference.py                        # Inference script for evaluation
├── examples.py                         # Usage examples
├── GRADERS.md                          # Grading documentation
├── Dockerfile                          # Docker container setup
└── server/
    ├── my_first_env_environment.py      # Core Environment Logic
    ├── app.py                          # FastAPI API Server
    ├── Dockerfile                      # Container setup
    └── requirements.txt                # Server dependencies
```

---

## 📄 Grading

Each task has a programmatic grader that returns a score between **0.0** and **1.0**. See [GRADERS.md](GRADERS.md) for full details on the grading formula and reward functions.