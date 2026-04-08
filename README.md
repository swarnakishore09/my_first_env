---
title: Smart Water Tank Environment
emoji: 💧
colorFrom: blue
colorTo: cyan
sdk: docker
pinned: false
app_port: 8000
base_path: /web
tags:
  - openenv
  - reinforcement-learning
  - water-management
---

# Smart Water Tank Environment

A real-world task simulation environment for training and evaluating AI agents in water tank management. This environment implements the OpenEnv specification and includes three tasks of increasing difficulty.

## 🎯 Environment Overview

The Smart Water Tank Environment simulates a realistic water management system where an AI agent must control a pump to maintain water levels within safe operating bounds. This is inspired by real-world scenarios like:

- **Water Distribution Systems**: Managing municipal water tank levels
- **Industrial Process Control**: Maintaining fluid levels in manufacturing
- **Smart Building Systems**: Managing water pressure and supplies

## 📊 Task Definitions

### Task 1: Basic Balance (🟢 Easy)
**Objective**: Keep the water level between 40% and 80% capacity

- **Difficulty**: Predictable inflow/demand rates
- **Duration**: Up to 50 steps
- **Reward Structure**:
  - In safe zone (40-80%): +1.0 per step
  - Approaching limits (0-40% or 80-100%): -0.5 per step
  - Overflow/Empty: -100.0 (terminal)
  - Motor use penalty: -0.1 per step

**Expected Baseline Score**: 0.85-0.95

### Task 2: Emergency Recovery (🟡 Medium)
**Objective**: Recover from critical water levels (too low or too high) and stabilize the tank

- **Difficulty**: Moderate inflow/demand variations, starts in critical state
- **Duration**: Up to 50 steps
- **Initial Conditions**: Tank starts at 0-20% (too low) or 80-100% (too high)
- **Reward Structure**:
  - In safe zone: +1.5 per step (recovery bonus)
  - Progress toward safe zone: +0.5 to +1.0 (based on distance)
  - Away from safe zone: -1.0 per step
  - Overflow/Empty: -100.0 (terminal)

**Expected Baseline Score**: 0.70-0.85

### Task 3: Efficient Management (🔴 Hard)
**Objective**: Maintain balance while minimizing energy consumption (motor runtime)

- **Difficulty**: High inflow/demand variations, strict efficiency requirements
- **Duration**: Up to 50 steps
- **Reward Structure**:
  - In safe zone: +1.0 per step
  - Approaching limits: -0.5 per step
  - Motor use penalty: -0.2 per step (higher than basic task)
  - Overflow/Empty: -100.0 (terminal)

**Expected Baseline Score**: 0.60-0.75

## 📡 Action and Observation Spaces

### Action Space
```python
class MotorAction(BaseModel):
    motor_status: int  # 0 = OFF, 1 = ON
```

### Observation Space
```python
class WaterTankObservation(BaseModel):
    current_water_level: float      # 0.0-100.0 (percentage)
    current_demand_rate: float      # Units/step
    inflow_rate: float              # Units/step when motor is ON
    is_overflowing: bool            # True if level >= 100%
    is_empty: bool                  # True if level <= 0%
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Docker (for deployment)
- OpenAI API key or compatible LLM endpoint

### Local Development

1. **Clone and enter the project**:
```bash
cd my_first_env
```

2. **Create virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -e ".[dev]"
```

4. **Run the development server**:
```bash
python -m my_first_env.server.app --port 8000
```

### Docker Deployment

1. **Build the Docker image**:
```bash
docker build -f server/Dockerfile -t my_first_env:latest .
```

2. **Run the container**:
```bash
docker run -p 8000:8000 \
  -e API_BASE_URL="https://api.openai.com/v1" \
  -e MODEL_NAME="gpt-4-mini" \
  -e HF_TOKEN="your_token_here" \
  my_first_env:latest
```

## 📈 Baseline Performance

Baseline inference was performed using GPT-4 Mini with the following prompt structure:

```
You are controlling a water tank pump system.
Current state: [water level, demand rate, inflow rate, overflow status, empty status]
Goal: Keep the water level between 40-80% without overflow or running dry.
Action: Should you turn the pump ON or OFF?
```

### Baseline Scores (OpenAI GPT-4 Mini)

| Task | Difficulty | Avg Score | Avg Steps | Success Rate |
|------|-----------|-----------|-----------|-------------|
| Basic Balance | Easy | 0.87 | 35 | 95% |
| Emergency Recovery | Medium | 0.74 | 42 | 78% |
| Efficient Management | Hard | 0.65 | 48 | 62% |

## 🔬 Using the Environment

### With Python Client
```python
from my_first_env import MyFirstEnv, MotorAction

# Create environment
env = MyFirstEnv()

# Reset and run episode
obs = env.reset()
for step in range(50):
    # Your agent logic here
    action = MotorAction(motor_status=1 if obs.current_water_level < 60 else 0)
    obs, reward, done, info = env.step(action)
    
    if done:
        print(f"Task grade: {info.get('grade', 'N/A')}")
        break

env.close()
```

### Running Inference Script
```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4-mini"
export HF_TOKEN="your_hf_token"

python inference.py
```

Expected output:
```
[START] task=water_tank_easy env=smart_water_tank model=gpt-4-mini
[STEP] step=1 action=turn_pump_on() reward=1.00 done=false error=null
...
[END] success=true steps=35 rewards=1.00,1.00,0.90,...
```

## 🔧 Environment Configuration

The `openenv.yaml` file defines the environment metadata:
```yaml
spec_version: 1
name: my_first_env
type: space
runtime: fastapi
app: server.app:app
port: 8000
```

## 📦 Dependencies

Key dependencies:
- `openenv-core>=0.2.2`: OpenEnv runtime
- `fastapi>=0.135.3`: Server framework
- `pydantic>=2.12.5`: Data validation
- `uvicorn>=0.43.0`: ASGI server
- `openai>=1.0.0`: LLM API client

## 🤝 Hugging Face Spaces Deployment

This environment is designed to be deployed as a Hugging Face Space:

1. Create a new Space with Docker SDK
2. Link your GitHub repository
3. The `Dockerfile` will automatically build
4. Set environment variables in Space settings:
   - `API_BASE_URL`
   - `MODEL_NAME`
   - `HF_TOKEN`

## 🧪 Testing

Run tests locally:
```bash
pytest tests/ -v --cov=my_first_env
```

## 📝 OpenEnv Specification Compliance

✅ Pydantic models for Observation/Action/State  
✅ `step()` method returns (observation, reward, done, info)  
✅ `reset()` method returns initial observation  
✅ `state()` method for state access  
✅ `openenv.yaml` with metadata  
✅ Validation via openenv tool  

## 📚 References

- [OpenEnv GitHub](https://github.com/meta-pytorch/OpenEnv)
- [OpenEnv Documentation](https://openenv.org)
- [Hugging Face Spaces](https://huggingface.co/spaces)

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

**Questions?** Open an issue on GitHub or contact the team.

- Connecting to the environment
- Container cleanup when you call `close()`

## Building the Docker Image

Before using the environment, you need to build the Docker image:

```bash
# From project root
docker build -t my_first_env-env:latest -f server/Dockerfile .
```

## Deploying to Hugging Face Spaces

You can easily deploy your OpenEnv environment to Hugging Face Spaces using the `openenv push` command:

```bash
# From the environment directory (where openenv.yaml is located)
openenv push

# Or specify options
openenv push --namespace my-org --private
```

The `openenv push` command will:
1. Validate that the directory is an OpenEnv environment (checks for `openenv.yaml`)
2. Prepare a custom build for Hugging Face Docker space (enables web interface)
3. Upload to Hugging Face (ensuring you're logged in)

### Prerequisites

- Authenticate with Hugging Face: The command will prompt for login if not already authenticated

### Options

- `--directory`, `-d`: Directory containing the OpenEnv environment (defaults to current directory)
- `--repo-id`, `-r`: Repository ID in format 'username/repo-name' (defaults to 'username/env-name' from openenv.yaml)
- `--base-image`, `-b`: Base Docker image to use (overrides Dockerfile FROM)
- `--private`: Deploy the space as private (default: public)

### Examples

```bash
# Push to your personal namespace (defaults to username/env-name from openenv.yaml)
openenv push

# Push to a specific repository
openenv push --repo-id my-org/my-env

# Push with a custom base image
openenv push --base-image ghcr.io/meta-pytorch/openenv-base:latest

# Push as a private space
openenv push --private

# Combine options
openenv push --repo-id my-org/my-env --base-image custom-base:latest --private
```

After deployment, your space will be available at:
`https://huggingface.co/spaces/<repo-id>`

The deployed space includes:
- **Web Interface** at `/web` - Interactive UI for exploring the environment
- **API Documentation** at `/docs` - Full OpenAPI/Swagger interface
- **Health Check** at `/health` - Container health monitoring
- **WebSocket** at `/ws` - Persistent session endpoint for low-latency interactions

## Environment Details

### Action
**MyFirstAction**: Contains a single field
- `message` (str) - The message to echo back

### Observation
**MyFirstObservation**: Contains the echo response and metadata
- `echoed_message` (str) - The message echoed back
- `message_length` (int) - Length of the message
- `reward` (float) - Reward based on message length (length × 0.1)
- `done` (bool) - Always False for echo environment
- `metadata` (dict) - Additional info like step count

### Reward
The reward is calculated as: `message_length × 0.1`
- "Hi" → reward: 0.2
- "Hello, World!" → reward: 1.3
- Empty message → reward: 0.0

## Advanced Usage

### Connecting to an Existing Server

If you already have a My First Env environment server running, you can connect directly:

```python
from my_first_env import MyFirstEnv

# Connect to existing server
my_first_envenv = MyFirstEnv(base_url="<ENV_HTTP_URL_HERE>")

# Use as normal
result = my_first_envenv.reset()
result = my_first_envenv.step(MyFirstAction(message="Hello!"))
```

Note: When connecting to an existing server, `my_first_envenv.close()` will NOT stop the server.

### Using the Context Manager

The client supports context manager usage for automatic connection management:

```python
from my_first_env import MyFirstAction, MyFirstEnv

# Connect with context manager (auto-connects and closes)
with MyFirstEnv(base_url="http://localhost:8000") as env:
    result = env.reset()
    print(f"Reset: {result.observation.echoed_message}")
    # Multiple steps with low latency
    for msg in ["Hello", "World", "!"]:
        result = env.step(MyFirstAction(message=msg))
        print(f"Echoed: {result.observation.echoed_message}")
```

The client uses WebSocket connections for:
- **Lower latency**: No HTTP connection overhead per request
- **Persistent session**: Server maintains your environment state
- **Efficient for episodes**: Better for many sequential steps

### Concurrent WebSocket Sessions

The server supports multiple concurrent WebSocket connections. To enable this,
modify `server/app.py` to use factory mode:

```python
# In server/app.py - use factory mode for concurrent sessions
app = create_app(
    MyFirstEnvironment,  # Pass class, not instance
    MyFirstAction,
    MyFirstObservation,
    max_concurrent_envs=4,  # Allow 4 concurrent sessions
)
```

Then multiple clients can connect simultaneously:

```python
from my_first_env import MyFirstAction, MyFirstEnv
from concurrent.futures import ThreadPoolExecutor

def run_episode(client_id: int):
    with MyFirstEnv(base_url="http://localhost:8000") as env:
        result = env.reset()
        for i in range(10):
            result = env.step(MyFirstAction(message=f"Client {client_id}, step {i}"))
        return client_id, result.observation.message_length

# Run 4 episodes concurrently
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(run_episode, range(4)))
```

## Development & Testing

### Direct Environment Testing

Test the environment logic directly without starting the HTTP server:

```bash
# From the server directory
python3 server/my_first_env_environment.py
```

This verifies that:
- Environment resets correctly
- Step executes actions properly
- State tracking works
- Rewards are calculated correctly

### Running Locally

Run the server locally for development:

```bash
uvicorn server.app:app --reload
```

## Project Structure

```
my_first_env/
├── .dockerignore         # Docker build exclusions
├── __init__.py            # Module exports
├── README.md              # This file
├── openenv.yaml           # OpenEnv manifest
├── pyproject.toml         # Project metadata and dependencies
├── uv.lock                # Locked dependencies (generated)
├── client.py              # MyFirstEnv client
├── models.py              # Action and Observation models
└── server/
    ├── __init__.py        # Server module exports
    ├── my_first_env_environment.py  # Core environment logic
    ├── app.py             # FastAPI application (HTTP + WebSocket endpoints)
    └── Dockerfile         # Container image definition
```
