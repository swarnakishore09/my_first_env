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
        super().__init__(url=target_url, api_key=api_key, **kwargs)

    def _step_payload(self, action: MotorAction) -> dict:
        """Convert a MotorAction into a JSON-compatible dict for the /step endpoint."""
        return action.model_dump()

    def _parse_result(self, payload: dict):
        """Parse the server's step response into (observation, reward, done, info)."""
        obs_data = payload.get("observation", payload)
        observation = WaterTankObservation(**obs_data) if isinstance(obs_data, dict) else obs_data
        reward = float(payload.get("reward", 0.0))
        done = bool(payload.get("done", False))
        info = payload.get("info", {})
        return observation, reward, done, info

    def _parse_state(self, payload: dict) -> WaterTankObservation:
        """Parse the server's state response into a WaterTankObservation."""
        return WaterTankObservation(**payload)

    def reset(self, task_type: str = "basic_balance", **kwargs) -> WaterTankObservation:
        reset_kwargs = {"task_type": task_type}
        reset_kwargs.update(kwargs)
        return super().reset(**reset_kwargs)