import sys
import os

# 1. Force Python to recognize the project root for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Import the correct server engine and models
try:
    from openenv.core.env_server.http_server import create_app
except ImportError:
    # Fallback for different library versions
    from openenv.core.env_server import create_fastapi_app as create_app

# Import your custom models and environment
from models import MotorAction, WaterTankObservation
from .my_first_env_environment import MyFirstEnvironment

# 3. Create the FastAPI app
# We pass the CLASS (MyFirstEnvironment), not an instance. 
# This handles the dashboard and API in one command.
app = create_app(
    MyFirstEnvironment,
    MotorAction,
    WaterTankObservation,
    env_name="my_first_env",
    max_concurrent_envs=1
)

# 4. Standard Uvicorn Runner
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)