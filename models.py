import random
import uuid
from pydantic import BaseModel, Field
from typing import Literal

# Available task types
TASK_TYPES = ["basic_balance", "emergency_recovery", "efficient_management"]

# ==========================================
# 1. DEFINE WHAT THE AI CAN DO (ACTION)
# ==========================================
class MotorAction(BaseModel):
    """Action to control the water pump motor."""
    motor_status: int = Field(default=0, ge=0, le=1, description="Set to 1 to turn the pump ON, 0 to turn it OFF.")

# ==========================================
# 2. DEFINE WHAT THE AI SEES (OBSERVATION)
# ==========================================
class WaterTankObservation(BaseModel):
    """Observation of the water tank environment."""
    current_water_level: float = Field(description="Current percentage of the tank filled (0.0 to 100.0)")
    current_demand_rate: float = Field(description="How fast water is leaving the tank per step")
    inflow_rate: float = Field(description="How fast water enters the tank when the motor is ON")
    is_overflowing: bool = Field(description="True if water hit 100%")
    is_empty: bool = Field(description="True if water hit 0%")
    reward: float = 0.0

# ==========================================
# 3. DEFINE INTERNAL TRACKING (STATE)
# ==========================================
class WaterTankState(BaseModel):
    """Internal state of the water tank environment."""
    current_water_level: float
    difficulty: str
    step_count: int
    inflow_rate: float
    demand_rate: float
    task_type: str = "basic_balance"
    max_safe_level: float = 80.0
    min_safe_level: float = 40.0
    episode_rewards: list[float] = Field(default_factory=list)
    episode_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # NEW: This field allows us to see custom alerts in the JSON!
    status_message: str = "Ready"

def get_observation(state: WaterTankState, current_reward: float = 0.0) -> WaterTankObservation:
    return WaterTankObservation(
        current_water_level=round(state.current_water_level, 2),
        current_demand_rate=round(state.demand_rate, 2),
        inflow_rate=round(state.inflow_rate, 2),
        is_overflowing=state.current_water_level >= 100.0,
        is_empty=state.current_water_level <= 0.0,
        reward=current_reward
    )

# ==========================================
# 4. RESET FUNCTION
# ==========================================
def reset(difficulty: str = "medium", task_type: str = "basic_balance") -> tuple[WaterTankObservation, WaterTankState]:
    if difficulty == "easy":
        inflow, demand = 10.0, 4.0
    elif difficulty == "medium":
        inflow, demand = random.uniform(8.0, 12.0), random.uniform(3.0, 7.0)
    else:
        inflow, demand = random.uniform(5.0, 15.0), random.uniform(5.0, 12.0)

    initial_level = random.uniform(40.0, 60.0)
    
    initial_state = WaterTankState(
        current_water_level=initial_level,
        difficulty=difficulty,
        step_count=0,
        inflow_rate=inflow,
        demand_rate=demand,
        task_type=task_type,
        status_message="System Reset - Waiting for first step"
    )
    
    return get_observation(initial_state), initial_state

# ==========================================
# 5. STEP FUNCTION (With Alerts & Warnings)
# ==========================================
def step(action: MotorAction, state: WaterTankState) -> tuple[WaterTankObservation, WaterTankState, float, bool]:
    state.step_count += 1
    done = False
    reward = 0.0

    # Physics
    water_in = state.inflow_rate if action.motor_status == 1 else 0.0
    state.current_water_level += (water_in - state.demand_rate)
    state.current_water_level = max(0.0, min(100.0, state.current_water_level))

    # --- NEW ALERT & WARNING LOGIC ---
    # We round to 1 decimal place to catch the 50% alert more easily
    current_rounded = round(state.current_water_level, 1)
    
    if current_rounded == 50.0:
        state.status_message = "ALERT: Water level is at exactly 50%!"
    elif state.current_water_level < 25.0:
        state.status_message = "WARNING: Water level critically low (Below 25%)!"
    else:
        state.status_message = f"Step {state.step_count} - Level Normal"

    # Reward logic (Stay between 0.0 and 1.0)
    if state.current_water_level >= 100.0 or state.current_water_level <= 0.0:
        reward = 0.0
        done = True
        state.status_message = "CRITICAL FAILURE: Tank Empty/Full"
    else:
        if 40.0 <= state.current_water_level <= 80.0:
            reward = 1.0
        else:
            reward = 0.2

    state.episode_rewards.append(reward)
    return get_observation(state, float(reward)), state, float(reward), done

# ==========================================
# 6. GRADER FUNCTION
# ==========================================
def grade_task(state: WaterTankState, rewards: list[float]) -> float:
    if not rewards or state.current_water_level >= 100.0 or state.current_water_level <= 0.0:
        return 0.0
    return round(float(sum(rewards) / len(rewards)), 3)