import random
from pydantic import BaseModel, Field
from typing import Literal

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
    task_type: Literal["basic_balance", "emergency_recovery", "efficient_management"] = "basic_balance"
    max_safe_level: float = 80.0
    min_safe_level: float = 40.0
    episode_rewards: list[float] = Field(default_factory=list)

# Helper function to generate what the AI sees from the hidden state
def get_observation(state: WaterTankState) -> WaterTankObservation:
    return WaterTankObservation(
        current_water_level=round(state.current_water_level, 2),
        current_demand_rate=round(state.demand_rate, 2),
        inflow_rate=round(state.inflow_rate, 2),
        is_overflowing=state.current_water_level >= 100.0,
        is_empty=state.current_water_level <= 0.0
    )

# ==========================================
# 4. RESET FUNCTION (Starts a new simulation)
# ==========================================
def reset(difficulty: str = "medium", task_type: str = "basic_balance") -> tuple[WaterTankObservation, WaterTankState]:
    """
    Initializes the tank based on the chosen difficulty and task type.
    
    Tasks:
    - basic_balance (EASY): Keep water level in safe zone (40-80%)
    - emergency_recovery (MEDIUM): Recover from critical low/high levels
    - efficient_management (HARD): Minimize motor runtime while maintaining balance
    """
    
    # Set physics based on difficulty
    if difficulty == "easy":
        # Highly predictable: steady inflow, steady demand
        inflow = 10.0
        demand = 4.0
    elif difficulty == "medium":
        # Slight variations in physics
        inflow = random.uniform(8.0, 12.0)
        demand = random.uniform(3.0, 7.0)
    else:  # hard
        # Hard: Wild variations, high demand, weak inflow
        inflow = random.uniform(5.0, 15.0)
        demand = random.uniform(5.0, 12.0)

    # Set initial water level based on task
    if task_type == "basic_balance":
        # Start in safe zone
        initial_level = random.uniform(40.0, 60.0)
    elif task_type == "emergency_recovery":
        # Start in critical condition
        initial_level = random.choice([
            random.uniform(0.0, 20.0),    # Too low
            random.uniform(80.0, 100.0)   # Too high
        ])
    else:  # efficient_management
        # Start in safe zone but with strict efficiency requirements
        initial_level = random.uniform(40.0, 60.0)

    # Always start the tank in a moderately safe zone (40% to 60%)
    initial_state = WaterTankState(
        current_water_level=initial_level,
        difficulty=difficulty,
        step_count=0,
        inflow_rate=inflow,
        demand_rate=demand,
        task_type=task_type,
        episode_rewards=[]
    )
    
    return get_observation(initial_state), initial_state

# ==========================================
# 5. STEP FUNCTION (The Physics and Rewards)
# ==========================================
def step(action: MotorAction, state: WaterTankState) -> tuple[WaterTankObservation, WaterTankState, float, bool]:
    """
    Applies the AI's motor action, calculates physics, and returns the score.
    
    Reward structure:
    - Safe zone (40-80%): +1.0 for basic task
    - Getting full (80-100%): -0.5 (warning)
    - Getting empty (0-40%): -0.5 (warning)
    - Overflow/Empty: -100.0 (failure)
    - Motor efficiency bonus: -0.1 per step for efficient_management task
    """
    state.step_count += 1
    done = False
    reward = 0.0

    # Apply Physics: New Level = Old Level + (Water In) - (Water Out)
    water_in = state.inflow_rate if action.motor_status == 1 else 0.0
    state.current_water_level += (water_in - state.demand_rate)

    # Clamp water level to valid range
    state.current_water_level = max(0.0, min(100.0, state.current_water_level))

    # Check boundaries and calculate rewards based on task type
    if state.current_water_level >= 100.0:
        state.current_water_level = 100.0
        reward = -100.0  # Massive penalty for overflowing
        done = True
    elif state.current_water_level <= 0.0:
        state.current_water_level = 0.0
        reward = -100.0  # Massive penalty for running dry
        done = True
    else:
        # The tank is still alive. Score based on task type
        if state.task_type == "basic_balance":
            # Task 1 (Easy): Just keep it in safe zone
            if 40.0 <= state.current_water_level <= 80.0:
                reward = 1.0  # Perfect safe zone
            elif 80.0 < state.current_water_level < 100.0:
                reward = -0.5  # Warning: Getting too full
            elif 0.0 < state.current_water_level < 40.0:
                reward = -0.5  # Warning: Getting too empty
        
        elif state.task_type == "emergency_recovery":
            # Task 2 (Medium): Recover from critical levels faster
            distance_from_safe = min(
                abs(state.current_water_level - 40.0) if state.current_water_level < 40.0 else 0,
                abs(state.current_water_level - 80.0) if state.current_water_level > 80.0 else 0
            )
            
            if 40.0 <= state.current_water_level <= 80.0:
                reward = 1.5  # Extra bonus for recovery success
            elif distance_from_safe > 0:
                reward = max(-5.0, 1.0 - distance_from_safe / 10.0)  # Reward recovery progress
            else:
                reward = -1.0
        
        elif state.task_type == "efficient_management":
            # Task 3 (Hard): Maximize efficiency (minimize motor use) while maintaining balance
            if 40.0 <= state.current_water_level <= 80.0:
                reward = 1.0
            elif 80.0 < state.current_water_level < 100.0:
                reward = -0.5
            elif 0.0 < state.current_water_level < 40.0:
                reward = -0.5
            
            # Efficiency penalty: penalize excessive motor use
            if action.motor_status == 1:
                reward -= 0.2  # Higher penalty for motor use in efficiency task

    # Prevent infinite loops during testing by capping episodes at 50 steps
    if state.step_count >= 50:
        done = True

    state.episode_rewards.append(reward)
    return get_observation(state), state, float(reward), done


# ==========================================
# 6. GRADER FUNCTIONS (For evaluation)
# ==========================================
def grade_task(state: WaterTankState, rewards: list[float]) -> float:
    """
    Grade a task completion.
    Returns a score between 0.0 and 1.0.
    
    Grading criteria:
    - No overflow/empty: Mandatory (0.0 if failed)
    - Avg reward > 0.5: 0.5-1.0 score
    - Efficiency (fewer motor toggles): +bonus in efficient task
    """
    if not rewards or len(rewards) == 0:
        return 0.0
    
    # If any critical failure occurred, return low score
    if any(r <= -100.0 for r in rewards):
        return 0.0
    
    # Calculate base score from average reward
    avg_reward = sum(rewards) / len(rewards)
    
    if state.task_type == "basic_balance":
        # Score based on maintaining balance
        safe_steps = sum(1 for r in rewards if r > 0.0)
        score = min(1.0, safe_steps / len(rewards))
    
    elif state.task_type == "emergency_recovery":
        # Score based on recovery speed and avoiding disaster
        recovery_steps = sum(1 for r in rewards if r > 0.0)
        score = min(1.0, recovery_steps / len(rewards) * 1.5)  # Recovery gets bonus
    
    else:  # efficient_management
        # Score based on balance AND efficiency (low motor use)
        safe_steps = sum(1 for r in rewards if r >= 0.5)
        score = min(1.0, safe_steps / len(rewards))
    
    return max(0.0, min(1.0, score))