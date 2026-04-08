"""
Client for the Smart Water Tank Environment.
"""
import os
from openenv.client import BaseEnv

from .models import MotorAction, WaterTankObservation

class MyFirstEnv(BaseEnv[MotorAction, WaterTankObservation]):
    """
    Client for the Smart Water Tank Environment.
    
    Provides convenient access to the water tank control environment
    with three tasks of increasing difficulty:
    - basic_balance (easy)
    - emergency_recovery (medium)
    - efficient_management (hard)
    """
    
    def __init__(self, url: str | None = None, api_key: str | None = None, **kwargs):
        """
        Initialize the environment client.
        
        Args:
            url: Server URL (default: http://localhost:8000)
            api_key: API key for authentication (optional)
            **kwargs: Additional arguments passed to BaseEnv
        """
        super().__init__(url=url, api_key=api_key, **kwargs)
    
    def reset(self, task_type: str = "basic_balance", **kwargs) -> WaterTankObservation:
        """
        Reset the environment for a new episode.
        
        Args:
            task_type: One of "basic_balance", "emergency_recovery", "efficient_management"
            **kwargs: Additional reset arguments
            
        Returns:
            WaterTankObservation for the initial state
        """
        reset_kwargs = {"task_type": task_type}
        reset_kwargs.update(kwargs)
        return super().reset(**reset_kwargs)
