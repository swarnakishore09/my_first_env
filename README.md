---
title: My First Env
emoji: 💧
colorFrom: blue
colorTo: red
sdk: docker
app_port: 8000
pinned: false
---
#💧Smart Water Tank Environment

Welcome to the **Smart Water Tank** environment! This is an industrial simulation designed for AI agents to learn water resource management through the OpenEnv framework.

##🎯The Mission
The objective is to maintain the water level within the **Safe Zone (40% to 80%)**.

* **Safe Zone:** $Reward = 1.0$
* **Warning Zone:** $Reward = 0.2$
* **Disaster:** $Reward = 0.0$ (Episode Ends)

---

##🚀How to Use

###1.Fork this Environment
Run this in your terminal to create your own version:

```bash
openenv fork swarnakishore/my_first_env --repo-id swarnakishore/my_first_env
2. Connect via Python
Python
from openenv.client import BaseEnv as EnvClient

env = EnvClient(url="[https://swarnakishore-my-first-env.hf.space](https://swarnakishore-my-first-env.hf.space)")
observation = env.reset(task_type="basic_balance")
print(f"Current Level: {observation.current_water_level}%")
📝 Available Tasks
basic_balance: Easy

emergency_recovery: Medium

efficient_management: Hard

📂 Project Structure
Plaintext
my_first_env/
├── README.md               # Configuration and Documentation
├── openenv.yaml            # Environment Manifest
├── models.py               # Action/Observation Models
└── server/
    ├── my_first_env_environment.py  # Core Logic
    ├── app.py              # API Server
    └── Dockerfile          # Container Setup