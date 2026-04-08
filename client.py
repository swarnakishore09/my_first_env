"""Client for the Smart Water Tank Environment."""
import os
import logging

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

from .models import MotorAction, WaterTankObservation

class MyFirstEnv(EnvClient[MotorAction, WaterTankObservation]):
    """
    Client for the Smart Water Tank Environment.
    """
    
    def __init__(self, url: str | None = None, api_key: str | None = None, **kwargs):
        # Default to local dev server if no URL is provided
        target_url = url or os.environ.get("OPENENV_URL", "http://localhost:8000")
        super().__init__(url=target_url, api_key=api_key, **kwargs)

    def reset(self, task_type: str = "basic_balance", **kwargs) -> WaterTankObservation:
        reset_kwargs = {"task_type": task_type}
        reset_kwargs.update(kwargs)
        return super().reset(**reset_kwargs)