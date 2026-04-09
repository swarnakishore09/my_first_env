import os
import sys
import asyncio
from openai import OpenAI

# 1. Mandatory Environment Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    print("Error: HF_TOKEN is missing.")
    sys.exit(1)

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

# 2. Import the client
try:
    from client import MyFirstEnv
    from models import MotorAction
except ImportError:
    from my_first_env.client import MyFirstEnv
    from my_first_env.models import MotorAction

async def run_task(env, task_id):
    obs = await env.reset(task_type=task_id)
    rewards = []
    
    # [START] MANDATORY FORMAT
    print(f"[START] task={task_id} env=smart_water_tank model={MODEL_NAME}", flush=True)

    for step in range(1, 51):
        try:
            prompt = f"Water Level: {obs.current_water_level:.1f}%. Action (ON/OFF)?"
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5
            )
            
            res_text = response.choices[0].message.content.lower()
            act_val = 1 if "on" in res_text or "1" in res_text else 0
            
            obs, reward, done, info = await env.step(MotorAction(motor_status=act_val))
            rewards.append(float(reward))
            
            act_str = "turn_pump_on()" if act_val == 1 else "turn_pump_off()"
            
            # [STEP] MANDATORY FORMAT
            print(f"[STEP] step={step} action={act_str} reward={reward:.2f} done={str(done).lower()} error=null", flush=True)
            
            if done: break
            
        except Exception as e:
            print(f"[STEP] step={step} action=error reward=0.00 done=true error={str(e)}", flush=True)
            break

    # Calculate success and a normalized score [0.0, 1.0] for the end log
    success = not obs.is_overflowing and not obs.is_empty
    
    # Assuming standard rewards, calculate a normalized score
    # If your environment returns negative rewards, this clamps it to 0
    raw_score = sum(rewards) / len(rewards) if rewards else 0.0
    final_score = min(max(raw_score, 0.0), 1.0) 
    
    # [END] MANDATORY FORMAT (Now includes score!)
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={len(rewards)} score={final_score:.3f} rewards={rewards_str}", flush=True)

async def main():
    # Use the exact task names your environment engine expects
    tasks = ["basic_balance", "emergency_recovery", "efficient_management"]
    
    # Connect to your local server
    env = MyFirstEnv(url="http://localhost:8000")
    
    try:
        for tid in tasks:
            await run_task(env, tid)
    finally:
        # Good practice to close the env just like the sample
        try:
            close_coro = env.close()
            if asyncio.iscoroutine(close_coro):
                await close_coro
        except Exception:
            pass

if __name__ == "__main__":
    asyncio.run(main())