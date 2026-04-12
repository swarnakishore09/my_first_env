from pydantic import BaseModel
from openenv.core.env_server import Environment
from models import MotorAction, WaterTankObservation, WaterTankState, step, reset, grade_task

# 1. Use StepResult to match the exact schema OpenEnv UI and Evaluators expect
try:
    from openenv.core.env_server import StepResult
except ImportError:
    try:
        from openenv.core.schemas import StepResult
    except ImportError:
        # Fallback for library shifts to prevent crashes
        class StepResult(BaseModel):
            observation: WaterTankObservation
            reward: float
            done: bool
            info: dict

class MyFirstEnvironment(Environment[MotorAction, WaterTankObservation, WaterTankState]):
    """
    Smart Water Tank Environment Engine.
    Handles the bridge between physics (models.py) and the API server.
    """
    
    def __init__(self, task_type: str = "basic_balance", difficulty: str = "easy"):
        super().__init__()
        self.task_type = task_type
        self.difficulty = self._map_difficulty(task_type)
        
        # Initialize state immediately so the dashboard doesn't load into an error
        self._current_state = None
        self.reset(self.task_type)
        
    def _map_difficulty(self, task_type: str) -> str:
        """Maps specific tasks to internal difficulty presets."""
        mapping = {
            "basic_balance": "easy",
            "emergency_recovery": "medium",
            "efficient_management": "hard"
        }
        return mapping.get(task_type, "easy")

    def reset(self, task_type: str = None, **kwargs):
        """
        Resets the tank. 
        Returns a StepResult so the Web UI sees 'done: false' and status info immediately.
        """
        if task_type:
            self.task_type = task_type
            self.difficulty = self._map_difficulty(task_type)
            
        # Get new physics state from models.py
        obs, self._current_state = reset(difficulty=self.difficulty, task_type=self.task_type)
        
        # Return structured for the UI - including our new status field
        return StepResult(
            observation=obs,
            reward=0.0,
            done=False,
            info={
                "task_type": self.task_type,
                "status": self._current_state.status_message,
                "quality_status": obs.quality_status,
                "recommendation": obs.recommendation
            }
        )

    def step(self, action: MotorAction):
        """
        Processes a single tick of time.
        Calculates physics, checks for overflow/alerts, and updates the score.
        """
        # 1. Execute physics logic (which now sets the status_message in models.py)
        obs, self._current_state, reward, done = step(action, self._current_state)
        
        # 2. Add grading and dynamic status info for the Web UI
        info = {
            "task_type": self.task_type,
            "status": self._current_state.status_message,
            "quality_status": obs.quality_status,
            "recommendation": obs.recommendation
        }
        
        if done:
            info["grade"] = grade_task(self._current_state, self._current_state.episode_rewards)
            
        # 3. Return 'Flat' StepResult
        return StepResult(
            observation=obs,
            reward=float(reward),
            done=done,
            info=info
        )
        
    @property
    def state(self) -> WaterTankState:
        """Exposes internal state to the OpenEnv 'get_state' endpoint."""
        return self._current_state