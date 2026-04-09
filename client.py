"""Client for the Smart Water Tank Environment."""
import os
import logging
from typing import Optional

# Robust import logic for OpenEnv Client
try:
    from openenv.core.env_client import HTTPEnvClient as EnvClient
except ImportError:
    try:
        from openenv.core.env_client import EnvClient
    except ImportError:
        try:
            from openenv.client import BaseEnv as EnvClient
        except ImportError:
            raise ImportError("Could not find a valid OpenEnv Client class. Please check your openenv-core version.")

try:
    from models import MotorAction, WaterTankObservation
except ImportError:
    from .models import MotorAction, WaterTankObservation

# Build the base class safely — EnvClient may not support generic subscripting
try:
    _Base = EnvClient[MotorAction, WaterTankObservation]
except TypeError:
    _Base = EnvClient

class MyFirstEnv(_Base):
    """
    Client for the Smart Water Tank Environment.
    """
    
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None, **kwargs):
        # Default to local dev server if no URL is provided
        target_url = url or os.environ.get("OPENENV_URL", "http://localhost:8000")
        
        # Different versions of OpenEnv use different init arguments
        import inspect
        sig = inspect.signature(_Base.__init__)
        init_kwargs = {}
        
        if "base_url" in sig.parameters:
            init_kwargs["base_url"] = target_url
        elif "url" in sig.parameters:
            init_kwargs["url"] = target_url
            
        if "api_key" in sig.parameters:
            init_kwargs["api_key"] = api_key
            
        for k, v in kwargs.items():
            if k in sig.parameters:
                init_kwargs[k] = v
                
        super().__init__(**init_kwargs)

    def _step_payload(self, action: MotorAction) -> dict:
        """Convert a MotorAction into a JSON-compatible dict for the /step endpoint."""
        return action.model_dump()

    def _parse_result(self, payload: dict):
        """Parse the server's step response into (observation, reward, done, info)."""
        obs_data = payload.get("observation", payload)

        # Handle double-wrapped payload from openenv server wrapper
        if isinstance(obs_data, dict) and "observation" in obs_data:
            info = obs_data.get("info", {})
            obs_data = obs_data["observation"]
        else:
            info = payload.get("info", {})

        observation = WaterTankObservation(**obs_data) if isinstance(obs_data, dict) else obs_data
        reward = float(payload.get("reward", 0.0))
        done = bool(payload.get("done", False))
        return observation, reward, done, info

    def _parse_state(self, payload: dict) -> WaterTankObservation:
        """Parse the server's state response into a WaterTankObservation."""
        return WaterTankObservation(**payload)

    async def reset(self, task_type: str = "basic_balance", **kwargs) -> WaterTankObservation:
        reset_kwargs = {"task_type": task_type}
        reset_kwargs.update(kwargs)
        result = await super().reset(**reset_kwargs)
        
        # super().reset() calls our _parse_result which returns a tuple,
        # but reset must return ONLY the observation to match inference.py expectations
        if isinstance(result, tuple):
            return result[0]
        elif hasattr(result, 'observation'):
            return result.observation
        return result