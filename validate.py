#!/usr/bin/env python
"""
Validation script to check if the project meets all OpenEnv hackathon requirements.
Run this before submission to ensure everything is configured correctly.
"""

import os
import sys
import json
from pathlib import Path

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def check(condition, message):
    """Print check result."""
    if condition:
        print(f"{GREEN}✓{RESET} {message}")
        return True
    else:
        print(f"{RED}✗{RESET} {message}")
        return False


def print_header(text):
    """Print section header."""
    print(f"\n{BLUE}{BOLD}{'─' * 60}{RESET}")
    print(f"{BLUE}{BOLD}{text}{RESET}")
    print(f"{BLUE}{BOLD}{'─' * 60}{RESET}")


def validate_file_structure():
    """Check project file structure."""
    print_header("1. PROJECT STRUCTURE")
    
    checks = []
    base_path = Path(__file__).parent
    
    required_files = {
        "inference.py": "Inference script (must be in root)",
        "models.py": "Data models and graders",
        "client.py": "OpenEnv client",
        "__init__.py": "Package initialization",
        "openenv.yaml": "Environment metadata",
        "README.md": "Documentation",
        "GRADERS.md": "Grading documentation",
        "examples.py": "Usage examples",
        "pyproject.toml": "Project configuration",
    }
    
    required_dirs = {
        "server": "Server module",
    }
    
    required_server_files = {
        "server/__init__.py": "Server package init",
        "server/app.py": "FastAPI application",
        "server/my_first_env_environment.py": "Environment implementation",
        "server/Dockerfile": "Docker container",
        "server/requirements.txt": "Server dependencies",
    }
    
    # Check files
    for file_name, description in required_files.items():
        file_path = base_path / file_name
        checks.append(check(
            file_path.exists(),
            f"{file_name:<25} - {description}"
        ))
    
    # Check directories
    for dir_name, description in required_dirs.items():
        dir_path = base_path / dir_name
        checks.append(check(
            dir_path.is_dir(),
            f"{dir_name:<25} - {description}"
        ))
    
    # Check server files
    for file_name, description in required_server_files.items():
        file_path = base_path / file_name
        checks.append(check(
            file_path.exists(),
            f"{file_name:<25} - {description}"
        ))
    
    return all(checks)


def validate_inference_script():
    """Check inference.py compliance."""
    print_header("2. INFERENCE.PY VALIDATION")
    
    checks = []
    base_path = Path(__file__).parent
    inference_file = base_path / "inference.py"
    
    if not inference_file.exists():
        print(f"{RED}✗ inference.py not found!{RESET}")
        return False
    
    # Read the file
    with open(inference_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required imports
    checks.append(check(
        "from openai import OpenAI" in content,
        "Uses OpenAI client (not alternatives)"
    ))
    
    # Check for environment variables
    checks.append(check(
        'os.getenv("API_BASE_URL"' in content,
        "Reads API_BASE_URL environment variable"
    ))
    
    checks.append(check(
        'os.getenv("MODEL_NAME"' in content,
        "Reads MODEL_NAME environment variable"
    ))
    
    checks.append(check(
        'os.getenv("HF_TOKEN"' in content,
        "Reads HF_TOKEN environment variable"
    ))
    
    checks.append(check(
        'API_BASE_URL, "https://api.openai.com/v1"' in content or
        'API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")' in content,
        "API_BASE_URL has default value"
    ))
    
    checks.append(check(
        'MODEL_NAME, "gpt-4' in content or
        'MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4' in content,
        "MODEL_NAME has default value"
    ))
    
    checks.append(check(
        'HF_TOKEN is None' in content or 'if not HF_TOKEN' in content,
        "HF_TOKEN is mandatory (checked)"
    ))
    
    # Check for output format
    checks.append(check(
        "[START]" in content,
        "Uses [START] output format"
    ))
    
    checks.append(check(
        "[STEP]" in content,
        "Uses [STEP] output format"
    ))
    
    checks.append(check(
        "[END]" in content,
        "Uses [END] output format"
    ))
    
    return all(checks)


def validate_models():
    """Check models.py for required classes and functions."""
    print_header("3. MODELS & GRADING VALIDATION")
    
    checks = []
    base_path = Path(__file__).parent
    models_file = base_path / "models.py"
    
    if not models_file.exists():
        print(f"{RED}✗ models.py not found!{RESET}")
        return False
    
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for Pydantic models
    checks.append(check(
        "class MotorAction(BaseModel)" in content,
        "MotorAction Pydantic model defined"
    ))
    
    checks.append(check(
        "class WaterTankObservation(BaseModel)" in content,
        "WaterTankObservation Pydantic model defined"
    ))
    
    checks.append(check(
        "class WaterTankState(BaseModel)" in content,
        "WaterTankState Pydantic model defined"
    ))
    
    # Check for functions
    checks.append(check(
        "def reset(" in content,
        "reset() function implemented"
    ))
    
    checks.append(check(
        "def step(" in content,
        "step() function implemented"
    ))
    
    checks.append(check(
        "def grade_task(" in content,
        "grade_task() function implemented"
    ))
    
    # Check for tasks
    checks.append(check(
        "basic_balance" in content,
        "basic_balance task defined"
    ))
    
    checks.append(check(
        "emergency_recovery" in content,
        "emergency_recovery task defined"
    ))
    
    checks.append(check(
        "efficient_management" in content,
        "efficient_management task defined"
    ))
    
    return all(checks)


def validate_environment_class():
    """Check MyFirstEnvironment class."""
    print_header("4. ENVIRONMENT CLASS VALIDATION")
    
    checks = []
    base_path = Path(__file__).parent
    env_file = base_path / "server" / "my_first_env_environment.py"
    
    if not env_file.exists():
        print(f"{RED}✗ my_first_env_environment.py not found!{RESET}")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks.append(check(
        "class MyFirstEnvironment(Environment" in content,
        "MyFirstEnvironment class extends Environment"
    ))
    
    checks.append(check(
        "def reset(" in content,
        "reset() method implemented"
    ))
    
    checks.append(check(
        "def step(" in content,
        "step() method implemented"
    ))
    
    checks.append(check(
        "def get_state(" in content or "state()" in content,
        "state() method implemented"
    ))
    
    checks.append(check(
        "grade_task" in content,
        "grade_task is used for evaluation"
    ))
    
    return all(checks)


def validate_dockerfile():
    """Check Dockerfile."""
    print_header("5. DOCKERFILE VALIDATION")
    
    checks = []
    base_path = Path(__file__).parent
    dockerfile = base_path / "server" / "Dockerfile"
    
    if not dockerfile.exists():
        print(f"{RED}✗ Dockerfile not found!{RESET}")
        return False
    
    with open(dockerfile, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks.append(check(
        "FROM" in content,
        "Dockerfile has FROM statement"
    ))
    
    checks.append(check(
        "openenv-base" in content,
        "Uses openenv-base image"
    ))
    
    checks.append(check(
        "WORKDIR" in content,
        "Sets working directory"
    ))
    
    checks.append(check(
        "RUN" in content,
        "Has RUN commands to install dependencies"
    ))
    
    checks.append(check(
        "CMD" in content or "ENTRYPOINT" in content,
        "Has CMD or ENTRYPOINT to start server"
    ))
    
    checks.append(check(
        "uvicorn" in content or "fastapi" in content,
        "Starts FastAPI/uvicorn server"
    ))
    
    checks.append(check(
        "8000" in content,
        "Exposes port 8000"
    ))
    
    return all(checks)


def validate_documentation():
    """Check documentation files."""
    print_header("6. DOCUMENTATION VALIDATION")
    
    checks = []
    base_path = Path(__file__).parent
    
    # README checks
    readme = base_path / "README.md"
    checks.append(check(
        readme.exists(),
        "README.md exists"
    ))
    
    if readme.exists():
        with open(readme, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks.append(check(
            "Task" in content and ("Easy" in content or "easy" in content),
            "README describes Easy task"
        ))
        
        checks.append(check(
            "Medium" in content or "medium" in content,
            "README describes Medium task"
        ))
        
        checks.append(check(
            "Hard" in content or "hard" in content,
            "README describes Hard task"
        ))
        
        checks.append(check(
            "Setup" in content or "setup" in content,
            "README has setup instructions"
        ))
        
        checks.append(check(
            "Docker" in content,
            "README has Docker instructions"
        ))
        
        checks.append(check(
            "baseline" in content.lower(),
            "README has baseline scores"
        ))
    
    # GRADERS.md checks
    graders = base_path / "GRADERS.md"
    checks.append(check(
        graders.exists(),
        "GRADERS.md exists"
    ))
    
    return all(checks)


def validate_openenv_yaml():
    """Check openenv.yaml."""
    print_header("7. OPENENV.YAML VALIDATION")
    
    checks = []
    base_path = Path(__file__).parent
    yaml_file = base_path / "openenv.yaml"
    
    if not yaml_file.exists():
        print(f"{RED}✗ openenv.yaml not found!{RESET}")
        return False
    
    with open(yaml_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks.append(check(
        "spec_version:" in content,
        "Has spec_version"
    ))
    
    checks.append(check(
        "name:" in content,
        "Has name field"
    ))
    
    checks.append(check(
        "runtime:" in content,
        "Has runtime field"
    ))
    
    checks.append(check(
        "app:" in content,
        "Has app field pointing to FastAPI app"
    ))
    
    checks.append(check(
        "port:" in content,
        "Has port configuration"
    ))
    
    return all(checks)


def validate_pyproject():
    """Check pyproject.toml."""
    print_header("8. PYPROJECT.TOML VALIDATION")
    
    checks = []
    base_path = Path(__file__).parent
    pyproject = base_path / "pyproject.toml"
    
    if not pyproject.exists():
        print(f"{RED}✗ pyproject.toml not found!{RESET}")
        return False
    
    with open(pyproject, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks.append(check(
        "name" in content,
        "Has project name"
    ))
    
    checks.append(check(
        "openenv-core" in content,
        "Depends on openenv-core"
    ))
    
    checks.append(check(
        "fastapi" in content,
        "Depends on fastapi"
    ))
    
    checks.append(check(
        "pydantic" in content,
        "Depends on pydantic"
    ))
    
    return all(checks)


def main():
    """Run all validations."""
    print(f"\n{BOLD}{'╔' + '═' * 58 + '╗'}{RESET}")
    print(f"{BOLD}║{RESET}" + " " * 58 + f"{BOLD}║{RESET}")
    print(f"{BOLD}║{RESET}  " + 
          "OpenEnv Hackathon Project Validation".center(54) + 
          f"  {BOLD}║{RESET}")
    print(f"{BOLD}║{RESET}" + " " * 58 + f"{BOLD}║{RESET}")
    print(f"{BOLD}{'╚' + '═' * 58 + '╝'}{RESET}\n")
    
    results = {
        "File Structure": validate_file_structure(),
        "Inference Script": validate_inference_script(),
        "Models & Grading": validate_models(),
        "Environment Class": validate_environment_class(),
        "Dockerfile": validate_dockerfile(),
        "Documentation": validate_documentation(),
        "openenv.yaml": validate_openenv_yaml(),
        "pyproject.toml": validate_pyproject(),
    }
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {status}  {name}")
    
    print(f"\n{BOLD}Overall: {passed}/{total} validation groups passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}{BOLD}✓ All validations passed! Ready for submission.{RESET}")
        return 0
    else:
        print(f"\n{YELLOW}{BOLD}⚠ Some validations failed. Please review above.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
