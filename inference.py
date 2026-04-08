"""
Inference script for the Smart Water Tank Environment.
Evaluates a model using the OpenAI API client.

Required environment variables:
- API_BASE_URL: API endpoint for the LLM (default: https://api.openai.com/v1)
- MODEL_NAME: Model identifier (default: gpt-4-mini)
- HF_TOKEN: Hugging Face API token (required)
"""

import os
import json
import sys
from openai import OpenAI

# Read environment variables with defaults
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

# Initialize OpenAI client
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

# Import the environment
try:
    from my_first_env.server.my_first_env_environment import MyFirstEnvironment
    from my_first_env.models import MotorAction, WaterTankObservation
except ImportError:
    from server.my_first_env_environment import MyFirstEnvironment
    from models import MotorAction, WaterTankObservation


def parse_action_from_response(response_text: str) -> int:
    """
    Parse the motor action from LLM response.
    Returns 0 (OFF) or 1 (ON).
    """
    response_text = response_text.lower().strip()
    
    if "on" in response_text or "1" in response_text or "turn on" in response_text:
        return 1
    else:
        return 0


def run_task(env: MyFirstEnvironment, task_name: str, difficulty: str, max_steps: int = 50) -> tuple[bool, int, list[float]]:
    """
    Run a single task episode and return success status, steps taken, and rewards.
    
    Returns:
        (success, steps, rewards_list)
    """
    observation = env.reset()
    rewards = []
    error_msg = None
    
    print(f"[START] task={task_name} env=smart_water_tank model={MODEL_NAME}", flush=True)
    
    for step in range(1, max_steps + 1):
        try:
            # Create a prompt for the LLM
            prompt = f"""You are controlling a water tank pump system. 
Current state:
- Water level: {observation.current_water_level:.1f}%
- Demand rate: {observation.current_demand_rate:.1f}
- Inflow rate: {observation.inflow_rate:.1f}
- Overflowing: {observation.is_overflowing}
- Empty: {observation.is_empty}

Your goal: Keep the water level between 40-80% without overflow or running dry.

Should you turn the pump ON or OFF? (Respond with just 'ON' or 'OFF')"""
            
            # Call the LLM
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10
            )
            
            action_value = parse_action_from_response(response.choices[0].message.content)
            action = MotorAction(motor_status=action_value)
            action_str = "turn_pump_on()" if action_value == 1 else "turn_pump_off()"
            
            # Step the environment
            observation, reward, done, info = env.step(action)
            rewards.append(float(reward))
            error_msg = info.get("error", None)
            
            print(f"[STEP] step={step} action={action_str} reward={reward:.2f} done={str(done).lower()} error={error_msg if error_msg else 'null'}", flush=True)
            
            if done:
                break
                
        except Exception as e:
            error_msg = str(e)
            print(f"[STEP] step={step} action=error reward=0.00 done=true error={error_msg}", flush=True)
            break
    
    # Calculate success: no crashes and maintained reasonable water level most of the time
    success = len(rewards) > 0 and sum(1 for r in rewards if r > -0.5) / len(rewards) > 0.5
    
    print(f"[END] success={str(success).lower()} steps={len(rewards)} rewards={','.join(f'{r:.2f}' for r in rewards)}", flush=True)
    
    return success, len(rewards), rewards


def main():
    """
    Run inference on all three tasks.
    """
    tasks = [
        ("water_tank_easy", "easy"),
        ("water_tank_medium", "medium"),
        ("water_tank_hard", "hard"),
    ]
    
    all_successes = []
    all_rewards = []
    
    env = MyFirstEnvironment()
    
    try:
        for task_name, difficulty in tasks:
            success, steps, rewards = run_task(env, task_name, difficulty)
            all_successes.append(success)
            all_rewards.extend(rewards)
            
    finally:
        pass  # Environment cleanup if needed


if __name__ == "__main__":
    main()
