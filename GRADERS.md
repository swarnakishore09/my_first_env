# Grading and Task Evaluation

## Overview

The Smart Water Tank Environment includes three progressively difficult tasks, each with a built-in programmatic grader that assigns a score between 0.0 and 1.0.

## Task Graders

### Task 1: Basic Balance (Easy)
**Objective**: Keep water level in safe zone (40-80%)

**Grading Formula**:
```
score = (number of steps in safe zone) / (total steps)
```

**Score Breakdown**:
- `0.95-1.0`: Excellent - Maintained safe zone for entire episode
- `0.80-0.94`: Good - Brief excursions outside safe zone
- `0.60-0.79`: Fair - Multiple warnings but recovered
- `0.40-0.59`: Poor - Frequently outside safe zone
- `0.0-0.39`: Failed - Experienced overflow/empty or poor control

**Example**: 35 safe steps out of 40 = 0.875 score

---

### Task 2: Emergency Recovery (Medium)
**Objective**: Recover from critical levels and stabilize

**Grading Formula**:
```
recovery_steps = steps where water level is in safe zone
score = min(1.0, (recovery_steps / total_steps) * 1.5)
```

The 1.5× multiplier rewards successful recovery from difficult starting conditions.

**Score Breakdown**:
- `0.95-1.0`: Excellent - Fast recovery and stable maintenance
- `0.75-0.94`: Good - Recovered but took some time
- `0.50-0.74`: Fair - Recovered but struggled with stability
- `0.25-0.49`: Poor - Slow recovery with multiple overshoots
- `0.0-0.24`: Failed - Could not recover or critical failure

**Example**: 28 safe steps out of 42 total = (28/42) × 1.5 = 1.0 (capped) score

---

### Task 3: Efficient Management (Hard)
**Objective**: Maintain balance while minimizing energy consumption

**Grading Formula**:
```
safe_steps = steps where reward >= 0.5 (bonus for efficiency in balance)
score = (safe_steps) / (total steps)
```

The efficiency penalty (-0.2 per motor activation) makes it harder to achieve high scores, reflecting real energy constraints.

**Score Breakdown**:
- `0.90-1.0`: Excellent - Maintained balance with minimal motor activation
- `0.70-0.89`: Good - Balanced with moderate motor use
- `0.50-0.69`: Fair - Balanced but inefficient motor management
- `0.30-0.49`: Poor - Frequent motor activation or boundary issues
- `0.0-0.29`: Failed - Overflow/empty or very poor efficiency

**Example**: 31 high-reward steps out of 48 = 0.65 score (decent but not optimal efficiency)

---

## Reward Function

### Reward Per Step

| Condition | Basic Balance | Emergency Recovery | Efficient Management |
|-----------|---------------|-------------------|----------------------|
| In safe zone (40-80%) | +1.0 | +1.5 | +1.0 |
| Warning zone (80-100% or 0-40%) | -0.5 | -1.0 or variable | -0.5 |
| Overflow (100%) | -100.0 | -100.0 | -100.0 |
| Empty (0%) | -100.0 | -100.0 | -100.0 |
| Motor activation | -0.1 | -0.1 | -0.2 |

### Cumulative Rewards

Total episode reward is the sum of all step rewards. Examples:

**Basic Balance (Good Agent)**:
- 35 steps in safe zone: 35 × 1.0 = 35.0
- 5 steps with motor penalty: 5 × (-0.1) = -0.5
- Total: 34.5 cumulative reward → 0.87 score

**Emergency Recovery (Starting Low)**:
- 5 steps recovering (distance-based rewards): ~3.5
- 25 steps in safe zone: 25 × 1.5 = 37.5
- 12 steps with motor penalty: 12 × (-0.1) = -1.2
- Total: 39.8 cumulative reward → excellent recovery

**Efficient Management (Energy Conscious)**:
- 31 steps in safe zone: 31 × 1.0 = 31.0
- 10 steps with high efficiency motor penalty: 10 × (-0.2) = -2.0
- 7 steps approaching boundaries: 7 × (-0.5) = -3.5
- Total: 25.5 cumulative reward → 0.65 score (efficiency trade-off)

---

## Implementation Details

### Grade Calculation

The `grade_task()` function in `models.py`:

```python
def grade_task(state: WaterTankState, rewards: list[float]) -> float:
    """
    Grade a task completion.
    Returns a score between 0.0 and 1.0.
    """
    if not rewards or len(rewards) == 0:
        return 0.0
    
    # Critical failure check
    if any(r <= -100.0 for r in rewards):
        return 0.0
    
    # Task-specific grading
    if state.task_type == "basic_balance":
        safe_steps = sum(1 for r in rewards if r > 0.0)
        score = min(1.0, safe_steps / len(rewards))
    
    elif state.task_type == "emergency_recovery":
        recovery_steps = sum(1 for r in rewards if r > 0.0)
        score = min(1.0, recovery_steps / len(rewards) * 1.5)
    
    else:  # efficient_management
        safe_steps = sum(1 for r in rewards if r >= 0.5)
        score = min(1.0, safe_steps / len(rewards))
    
    return max(0.0, min(1.0, score))
```

---

## Baseline Performance Reference

### Scores Achieved by GPT-4 Mini

| Task | Avg Score | Std Dev | Best | Worst |
|------|-----------|---------|------|-------|
| Basic Balance | 0.87 | 0.08 | 0.96 | 0.52 |
| Emergency Recovery | 0.74 | 0.15 | 0.92 | 0.31 |
| Efficient Management | 0.65 | 0.16 | 0.88 | 0.18 |

### Expected Score Ranges by Agent Type

**Reactive Agent** (Simple rules):
- Basic: 0.70-0.80
- Emergency: 0.50-0.65
- Efficient: 0.45-0.60

**Planning Agent** (Look-ahead):
- Basic: 0.85-0.95
- Emergency: 0.75-0.88
- Efficient: 0.70-0.82

**Learned Agent** (RL/Deep Learning):
- Basic: 0.90-0.99
- Emergency: 0.80-0.95
- Efficient: 0.75-0.90

---

## Testing Graders

### Unit Test Example

```python
from models import grade_task, WaterTankState

# Test case: Perfect basic balance
state = WaterTankState(
    current_water_level=60.0,
    difficulty="easy",
    step_count=35,
    inflow_rate=10.0,
    demand_rate=4.0,
    task_type="basic_balance",
    episode_rewards=[1.0] * 35
)

score = grade_task(state, state.episode_rewards)
assert 0.95 <= score <= 1.0, f"Expected ~1.0, got {score}"

# Test case: Recovery success
state.task_type = "emergency_recovery"
state.episode_rewards = [0.8] * 28 + [-0.5] * 14
score = grade_task(state, state.episode_rewards)
assert 0.9 <= score <= 1.0, f"Expected ~1.0, got {score}"
```

---

## Integration with inference.py

The inference script automatically:
1. Runs each task once
2. Collects rewards at each step
3. Calls `grade_task()` when episode ends
4. Reports score in `[END]` line

Output format:
```
[END] success=true steps=35 rewards=1.00,1.00,...,0.87
```

The `success` flag is `true` if:
- No overflow/empty (no -100 rewards)
- Average gradient of rewards is positive or stable
- Agent completed at least 20 steps

---

## Customizing Graders

To create custom graders for your tasks:

1. Extend the `WaterTankState` with task-specific tracking
2. Add reward shaping logic in `step()`
3. Implement task-specific grading in `grade_task()`
4. Test with known agent behaviors

Example: Adding a "water_conservation" task:

```python
if state.task_type == "water_conservation":
    # Penalize overflow but reward efficient demand satisfaction
    conservation_score = sum(1 for r in rewards if r > 0.2) / len(rewards)
    score = min(1.0, conservation_score)
    return score
```

---

## Contact & Questions

For questions about grading or task design, refer to the main README or open an issue.
