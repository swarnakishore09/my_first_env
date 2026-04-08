# Hugging Face Spaces Deployment - Complete Guide

## ⚠️ IMPORTANT: Credential Security

**DO NOT SHARE YOUR HF CREDENTIALS** 
- Instead, use HF Space Secrets (environment variables)
- Your password should NEVER be in code or committed to git

---

## Pre-Submission Checklist

### Phase 1: Local Validation ✅

- [x] All Python files pass syntax check
- [x] All models are Pydantic v2 compatible
- [x] `validate.py` shows 8/8 groups passing
- [x] `examples.py` runs all 3 tasks successfully
- [x] `verify_openenv_spec.py` confirms full OpenEnv compliance
- [x] No hardcoded API keys or tokens

### Phase 2: Specification Compliance ✅

- [x] **Action Model**: `MotorAction` (Pydantic)
- [x] **Observation Model**: `WaterTankObservation` (Pydantic)
- [x] **State Model**: `WaterTankState` (Pydantic)
- [x] **Methods**:
  - [x] `reset()` returns (observation, state)
  - [x] `step(action)` returns (observation, reward, done, info)
  - [x] `state()` returns WaterTankState
- [x] **openenv.yaml**: spec_version 1 compliant
- [x] **3 Tasks**: basic_balance, emergency_recovery, efficient_management
- [x] **Graders**: grade_task() returns 0.0-1.0

### Phase 3: Inference Script ✅

- [x] `inference.py` in root directory
- [x] Uses OpenAI Client (official library)
- [x] Reads environment variables:
  - [x] `API_BASE_URL` (with default)
  - [x] `MODEL_NAME` (with default)
  - [x] `HF_TOKEN` (required, validated)
- [x] Output format:
  - [x] `[START] task=... env=... model=...`
  - [x] `[STEP] step=... action=... reward=... done=... error=...`
  - [x] `[END] success=... steps=... rewards=...`

### Phase 4: Containerization ✅

- [x] **Dockerfile**: Complete, multi-stage build
- [x] **Base Image**: openenv-base
- [x] **Ports**: 8000 exposed
- [x] **Dependencies**: All in pyproject.toml
- [x] **Entry Point**: FastAPI server
- [x] **Health Check**: Configured
- [x] **Build Size**: <5GB (fits 8GB container)

### Phase 5: Documentation ✅

- [x] **README.md**: 400+ lines
  - [x] Environment overview & motivation
  - [x] Task descriptions (Easy/Medium/Hard)
  - [x] Action/Observation space definitions
  - [x] Setup instructions (local + Docker)
  - [x] Usage examples
  - [x] Baseline scores
- [x] **GRADERS.md**: Detailed grading documentation
- [x] **IMPLEMENTATION_SUMMARY.md**: Requirements mapping
- [x] **DEPLOYMENT_CHECKLIST.md**: Deployment steps
- [x] **OPENENV_SPEC_COMPLIANCE.md**: Spec compliance details

---

## HF Space Setup Instructions

### Step 1: Prepare Your Repository

```bash
# Initialize git (if not already done)
cd d:\my_openenv\my_first_env
git init
git add .
git commit -m "Initial OpenEnv submission"

# Create .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
.venv/
venv/
.pytest_cache/
.coverage
htmlcov/
.DS_Store
EOF

git add .gitignore
git commit -m "Add gitignore"
```

### Step 2: Push to GitHub

1. Create new GitHub repository at https://github.com/new
2. Name: `my_first_env` (or your choice)
3. Description: "Smart Water Tank Environment for OpenEnv"
4. Make it **PUBLIC** (required for HF Space)
5. Push your code:

```bash
git remote add origin https://github.com/swarnakishore/my_first_env.git
git branch -M main
git push -u origin main
```

### Step 3: Create Hugging Face Space

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in:
   - **Owner**: swarnakishore (your account)
   - **Space name**: my_first_env
   - **License**: Apache 2.0 (your choice)
   - **SDK**: Docker ⭐ (IMPORTANT)
   - **Visibility**: Public

4. Click "Create Space"

### Step 4: Add GitHub Repository

Once Space is created:

1. In Space settings → "Repository"
2. Connect GitHub repository
3. Select: `swarnakishore/my_first_env`
4. Branch: `main`
5. Click "Link Repository"

### Step 5: Set Environment Variables (Secrets)

⚠️ **NEVER commit credentials to git!**

In Space settings → "Secrets and variables":

Add these three secrets:

| Key | Value | Example |
|-----|-------|---------|
| `API_BASE_URL` | Your LLM API endpoint | `https://api.openai.com/v1` |
| `MODEL_NAME` | Your model name | `gpt-4-mini` |
| `HF_TOKEN` | Your HF/LLM API key | `hf_xxxxxxxxxxxxxxxxxxxx` |

**How to add secrets:**
1. Click "Add secret"
2. Name: `API_BASE_URL`
3. Value: `https://api.openai.com/v1`
4. Click "Save secret"
5. Repeat for `MODEL_NAME` and `HF_TOKEN`

### Step 6: Monitor Building

Space will automatically:
1. Clone your GitHub repo
2. Build Docker image
3. Start container on port 8000
4. Run health check

**Expected time**: 5-15 minutes

Check status in Space settings → "Building" tab

### Step 7: Verify Deployment

Once "Running" status appears:

```bash
# Test the health endpoint
curl https://huggingface.co/spaces/swarnakishore/my_first_env/health

# Should return 200 OK
```

---

## Testing Before Submission

### Local Docker Test

```bash
# Build locally
docker build -f server/Dockerfile -t my_first_env:latest .

# Run with environment variables
docker run -p 8000:8000 \
  -e API_BASE_URL="https://api.openai.com/v1" \
  -e MODEL_NAME="gpt-4-mini" \
  -e HF_TOKEN="your_hf_token_here" \
  my_first_env:latest

# In another terminal, test the server
curl http://localhost:8000/health
```

### Pre-Submission Validation

Run this before submitting:

```bash
# 1. Validate project structure
python validate.py
# Expected: 8/8 groups pass

# 2. Run examples
python examples.py
# Expected: 4 examples complete successfully

# 3. Verify OpenEnv spec
python verify_openenv_spec.py
# Expected: All 10 checks pass
```

---

## Submission Checklist

Before clicking submit on HF hackathon portal:

- [ ] Validation script passes (8/8)
- [ ] Examples run successfully
- [ ] OpenEnv spec verification passes (10/10)
- [ ] Space is in "Running" state
- [ ] Space responds to /health endpoint (200)
- [ ] GitHub repo is public
- [ ] All 3 environment variables set as secrets
- [ ] .gitignore configured (no credentials)
- [ ] Dockerfile builds successfully
- [ ] README has all required sections
- [ ] inference.py works locally

---

## Troubleshooting

### Space Won't Build

**Error**: Docker build fails

**Solutions**:
1. Check Dockerfile syntax: `docker build -f server/Dockerfile --dry-run .`
2. Ensure all dependencies in pyproject.toml
3. Check GitHub repo is public
4. View build logs in Space settings

**Command to test locally**:
```bash
cd d:\my_openenv\my_first_env
docker build -f server/Dockerfile -t test:latest .
```

### Space Won't Start

**Error**: Container exits immediately

**Solutions**:
1. Check CMD in Dockerfile
2. Verify port 8000 is exposed
3. Check environment variables are set
4. Review startup logs in Space settings

**Command to test locally**:
```bash
docker run -p 8000:8000 \
  -e API_BASE_URL="https://api.openai.com/v1" \
  -e MODEL_NAME="gpt-4-mini" \
  -e HF_TOKEN="test" \
  test:latest
```

### inference.py Fails

**Error**: Script exits with error

**Solutions**:
1. Ensure HF_TOKEN is set: `echo $HF_TOKEN`
2. Test locally: `python inference.py`
3. Check OpenAI client installed: `python -c "from openai import OpenAI"`
4. Verify output format matches specification

### Grading Returns Invalid Scores

**Error**: Grader returns >1.0 or <0.0

**Solutions**:
1. Check grade_task() function
2. Ensure rewards are collected: `state.episode_rewards`
3. Verify task_type is correct
4. Run examples to see grading in action

---

## Key Files for Submission

📂 **Required Files**:
- ✅ `inference.py` - In root directory
- ✅ `server/Dockerfile` - Docker configuration
- ✅ `openenv.yaml` - Environment metadata
- ✅ `models.py` - Pydantic models
- ✅ `server/my_first_env_environment.py` - Environment implementation
- ✅ `README.md` - Complete documentation
- ✅ `pyproject.toml` - Dependencies
- ✅ `.gitignore` - Exclude secrets

📂 **Optional but Helpful**:
- ℹ️ `GRADERS.md` - Grading documentation
- ℹ️ `examples.py` - Usage examples
- ℹ️ `validate.py` - Validation script
- ℹ️ `verify_openenv_spec.py` - Spec verification

---

## Expected Baseline Scores

When inference.py runs with GPT-4 Mini:

| Task | Difficulty | Expected Score |
|------|-----------|-----------------|
| Basic Balance | Easy | 0.80-0.95 |
| Emergency Recovery | Medium | 0.70-0.85 |
| Efficient Management | Hard | 0.60-0.75 |

**Your actual scores may vary based on:**
- Model capability (GPT-4 vs GPT-3.5)
- Random initialization (water level varies)
- Prompt engineering
- API latency

---

## Support Resources

- **OpenEnv Docs**: https://github.com/meta-pytorch/OpenEnv
- **HF Spaces Docs**: https://huggingface.co/docs/hub/spaces
- **HF API Tokens**: https://huggingface.co/settings/tokens
- **OpenAI API**: https://platform.openai.com/docs

---

## Final Notes

✅ **Your project is ready for deployment!**

1. **Do NOT share credentials** - Use HF Secrets instead
2. **Test locally first** - Run all validation scripts
3. **Monitor build** - Space building can take 5-15 minutes
4. **Check status frequently** - HF Spaces can timeout during build
5. **Review logs** - If build fails, check error messages in Space settings

**Good luck with your submission!** 🚀
