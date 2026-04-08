"""
Smart Water Tank Environment for OpenEnv.

A realistic water management system where AI agents control pumps
to maintain water levels within safe operating bounds.
"""

from .client import MyFirstEnv
from .models import (
    MotorAction,
    WaterTankObservation,
    WaterTankState,
    step,
    reset,
    grade_task
)

__all__ = [
    "MyFirstEnv",
    "MotorAction",
    "WaterTankObservation",
    "WaterTankState",
    "step",
    "reset",
    "grade_task"
]

__version__ = "0.1.0"
