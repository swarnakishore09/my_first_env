"""
FastAPI application for the Smart Water Tank Environment.

This server provides an HTTP interface to the water tank control environment.
It accepts pump control actions and returns observations about the tank state.
"""
import sys
import os

# 1. Force Python to recognize the current folder as the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from openenv.core.env_server.http_server import create_app
except Exception as e:
    raise ImportError(
        "openenv-core is required. Install with 'pip install openenv-core[core]'"
    ) from e

# 2. Use direct absolute imports (No more confusing dots!)
from models import MotorAction, WaterTankObservation
from server.my_first_env_environment import MyFirstEnvironment

# 3. Create the FastAPI app
app = create_app(
    MyFirstEnvironment,
    MotorAction,           
    WaterTankObservation,  
    env_name="my_first_env",
    max_concurrent_envs=10,  # Allow multiple concurrent environments
)


def main(host: str = "0.0.0.0", port: int = 8000):
    """Run the development server."""
    import uvicorn
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Smart Water Tank Environment Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    args = parser.parse_args()
    main(host=args.host, port=args.port)
