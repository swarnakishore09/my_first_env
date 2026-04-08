from openenv.core.env_server import Environment

# Try relative import first (for Docker/uv), fallback to absolute import (for direct Python run)
try:
    from ..models import MotorAction, WaterTankObservation, WaterTankState, step, reset, grade_task
except ImportError:
    from models import MotorAction, WaterTankObservation, WaterTankState, step, reset, grade_task

class MyFirstEnvironment(Environment[MotorAction, WaterTankObservation, WaterTankState]):
    """
    Smart Water Tank Environment with multiple tasks.
    
    Tasks:
    1. basic_balance (easy) - Keep water level in safe zone (40-80%)
    2. emergency_recovery (medium) - Recover from critical levels
    3. efficient_management (hard) - Minimize motor use while maintaining balance
    """
    
    def __init__(self, task_type: str = "basic_balance", difficulty: str = "easy"):
        super().__init__()
        self._current_state = None
        self.task_type = task_type
        self.difficulty = self._map_difficulty(difficulty)
    
    def _map_difficulty(self, task_type: str) -> str:
        """Map task type to appropriate difficulty level."""
        if task_type == "basic_balance":
            return "easy"
        elif task_type == "emergency_recovery":
            return "medium"
        else:  # efficient_management
            return "hard"

    def reset(self, task_type: str = None, **kwargs) -> WaterTankObservation:
        """
        Reset the environment for a new episode.
        
        Args:
            task_type: Optional task type to switch tasks
        """
        if task_type:
            self.task_type = task_type
            self.difficulty = self._map_difficulty(task_type)
        
        # Calls your Water Tank reset function
        obs, self._current_state = reset(difficulty=self.difficulty, task_type=self.task_type)
        return obs

    def step(self, action: MotorAction) -> tuple[WaterTankObservation, float, bool, dict]:
        """
        Execute one step of the environment.
        
        Returns:
            observation: WaterTankObservation
            reward: float
            done: bool
            info: dict with additional info including 'grade' when done
        """
        # Calls your Water Tank physics engine
        obs, self._current_state, reward, done = step(action, self._current_state)
        
        info = {"task_type": self.task_type}
        
        if done:
            # Calculate grade when episode ends
            grade = grade_task(self._current_state, self._current_state.episode_rewards)
            info["grade"] = grade
        
        return obs, float(reward), done, info
        
    def state(self) -> WaterTankState:
        """Get the current internal state (OpenEnv spec requirement)."""
        return self._current_state