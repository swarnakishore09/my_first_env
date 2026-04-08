#!/usr/bin/env python
"""
Example script showing how to use the Smart Water Tank Environment.

This script demonstrates:
1. Using the environment directly (local mode)
2. Interacting with the server via HTTP client
3. Evaluating different tasks
4. Calculating grades
"""

import sys
import os

# Add parent directory to path for local imports
sys.path.insert(0, os.path.dirname(__file__))

from models import MotorAction, WaterTankState, step, reset, grade_task


def example_direct_usage():
    """Example 1: Use the environment directly (no server needed)."""
    print("=" * 60)
    print("Example 1: Direct Environment Usage (Easy Task)")
    print("=" * 60)
    
    # Reset the environment
    obs, state = reset(difficulty="easy", task_type="basic_balance")
    
    print(f"\nInitial observation:")
    print(f"  Water level: {obs.current_water_level}%")
    print(f"  Demand rate: {obs.current_demand_rate}")
    print(f"  Inflow rate: {obs.inflow_rate}")
    print(f"  Overflowing: {obs.is_overflowing}")
    print(f"  Empty: {obs.is_empty}")
    
    # Simulate 10 steps with a simple control strategy
    print(f"\nRunning 10 steps with simple control strategy...")
    print(f"Strategy: Turn motor ON if below 60%, OFF if above 70%\n")
    
    for step_num in range(1, 11):
        # Simple control logic
        if obs.current_water_level < 60.0:
            action = MotorAction(motor_status=1)  # Turn ON
        elif obs.current_water_level > 70.0:
            action = MotorAction(motor_status=0)  # Turn OFF
        else:
            action = MotorAction(motor_status=0)  # Default OFF
        
        # Execute step
        obs, state, reward, done = step(action, state)
        
        motor_status = "ON" if action.motor_status == 1 else "OFF"
        print(f"Step {step_num}: Motor {motor_status:2} | Level {obs.current_water_level:5.1f}% | "
              f"Reward {reward:6.2f} | Done {done}")
        
        if done:
            print(f"\nEpisode ended at step {step_num}")
            break
    
    # Calculate final grade
    grade = grade_task(state, state.episode_rewards)
    print(f"\nFinal Statistics:")
    print(f"  Total steps: {len(state.episode_rewards)}")
    print(f"  Total reward: {sum(state.episode_rewards):.2f}")
    print(f"  Average reward: {sum(state.episode_rewards) / len(state.episode_rewards):.2f}")
    print(f"  Grade: {grade:.3f}")


def example_medium_task():
    """Example 2: Try the medium difficulty task (Emergency Recovery)."""
    print("\n" + "=" * 60)
    print("Example 2: Emergency Recovery Task (Medium)")
    print("=" * 60)
    
    obs, state = reset(difficulty="medium", task_type="emergency_recovery")
    
    print(f"\nStarting from critical level: {obs.current_water_level:.1f}%")
    print(f"Demand rate: {obs.current_demand_rate:.1f}")
    print(f"Inflow rate: {obs.inflow_rate:.1f}")
    
    # More aggressive control strategy for recovery
    print(f"\nRunning with recovery-focused strategy...")
    print(f"Strategy: Turn motor ON if below 50%, OFF if above 75%\n")
    
    steps_taken = 0
    for step_num in range(1, 51):
        # Recovery-focused strategy
        if obs.current_water_level < 50.0:
            action = MotorAction(motor_status=1)  # Turn ON (fill tank)
        elif obs.current_water_level > 75.0:
            action = MotorAction(motor_status=0)  # Turn OFF (let demand reduce level)
        else:
            # Maintain balance
            action = MotorAction(motor_status=0 if obs.current_water_level > 60.0 else 1)
        
        obs, state, reward, done = step(action, state)
        steps_taken += 1
        
        motor_status = "ON" if action.motor_status == 1 else "OFF"
        print(f"Step {step_num:2}: Motor {motor_status:2} | Level {obs.current_water_level:5.1f}% | "
              f"Reward {reward:6.2f}")
        
        if done:
            break
    
    # Calculate grade
    grade = grade_task(state, state.episode_rewards)
    print(f"\nRecovery Task Results:")
    print(f"  Total steps: {steps_taken}")
    print(f"  Total reward: {sum(state.episode_rewards):.2f}")
    print(f"  Grade: {grade:.3f} ({grade*100:.1f}%)")


def example_efficient_task():
    """Example 3: Try the hard difficulty task (Efficient Management)."""
    print("\n" + "=" * 60)
    print("Example 3: Efficient Management Task (Hard)")
    print("=" * 60)
    
    obs, state = reset(difficulty="hard", task_type="efficient_management")
    
    print(f"\nStarting level: {obs.current_water_level:.1f}%")
    print(f"Variable demand: {obs.current_demand_rate:.1f}")
    print(f"Variable inflow: {obs.inflow_rate:.1f}")
    print(f"\nThis task penalizes motor activation more (-0.2 vs -0.1)")
    print(f"Strategy: Turn motor ON only when necessary (below 45%)\n")
    
    steps_taken = 0
    for step_num in range(1, 51):
        # Efficient strategy: minimize motor use
        if obs.current_water_level < 45.0:
            action = MotorAction(motor_status=1)  # Only turn ON when critical
        else:
            action = MotorAction(motor_status=0)  # Prefer OFF for efficiency
        
        obs, state, reward, done = step(action, state)
        steps_taken += 1
        
        motor_status = "ON" if action.motor_status == 1 else "OFF"
        print(f"Step {step_num:2}: Motor {motor_status:2} | Level {obs.current_water_level:5.1f}% | "
              f"Reward {reward:6.2f}")
        
        if done:
            break
    
    # Calculate grade (harder to get high scores due to efficiency penalty)
    grade = grade_task(state, state.episode_rewards)
    print(f"\nEfficiency Task Results:")
    print(f"  Total steps: {steps_taken}")
    print(f"  Total reward: {sum(state.episode_rewards):.2f}")
    print(f"  Grade: {grade:.3f} ({grade*100:.1f}%)")


def compare_strategies():
    """Example 4: Compare different control strategies."""
    print("\n" + "=" * 60)
    print("Example 4: Strategy Comparison")
    print("=" * 60)
    
    strategies = {
        "Conservative": (40, 70),    # Turn ON at 40%, OFF at 70%
        "Moderate": (50, 75),        # Turn ON at 50%, OFF at 75%
        "Aggressive": (30, 80),      # Turn ON at 30%, OFF at 80%
    }
    
    results = {}
    
    for strategy_name, (on_threshold, off_threshold) in strategies.items():
        obs, state = reset(difficulty="easy", task_type="basic_balance")
        
        for _ in range(50):
            if obs.current_water_level < on_threshold:
                action = MotorAction(motor_status=1)
            elif obs.current_water_level > off_threshold:
                action = MotorAction(motor_status=0)
            else:
                action = MotorAction(motor_status=0)
            
            obs, state, reward, done = step(action, state)
            
            if done:
                break
        
        grade = grade_task(state, state.episode_rewards)
        results[strategy_name] = {
            "grade": grade,
            "steps": len(state.episode_rewards),
            "total_reward": sum(state.episode_rewards),
        }
    
    print("\nStrategy Performance (Easy Task - Basic Balance):\n")
    print(f"{'Strategy':<15} {'Grade':<8} {'Steps':<8} {'Total Reward':<12}")
    print("-" * 43)
    
    for strategy, metrics in results.items():
        print(f"{strategy:<15} {metrics['grade']:.3f}   {metrics['steps']:<8} "
              f"{metrics['total_reward']:>10.2f}")


if __name__ == "__main__":
    print("\n")
    print("+========================================================+")
    print("|                                                        |")
    print("|  Smart Water Tank Environment - Usage Examples| ")
    print("|                                                        |")
    print("+========================================================+")
    
    # Run examples
    example_direct_usage()
    example_medium_task()
    example_efficient_task()
    compare_strategies()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60 + "\n")
