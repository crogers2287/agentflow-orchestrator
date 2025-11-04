# Phase 1: Setup, Testing & Understanding (REVISED)

## 🎉 MAJOR UPDATE: Sprint 1 MVP Already Complete!

Claude Code has built the entire MVP! The code exists at:
**https://github.com/crogers2287/agentflow-orchestrator**

## What Already Exists ✅

### Core Components (All Built!)
- ✅ **Orchestrator** - Three workflow modes, verification loops, debate protocol
- ✅ **Context Router** - Token counting, intelligent routing, cost estimation
- ✅ **AgentFlow Client** - vLLM integration, task analysis, refinement
- ✅ **Gemini Client** - 2M token context, verification, heavy lifting modes
- ✅ **CLI Interface** - Rich UI, interactive mode, health checks
- ✅ **Configuration** - YAML settings, prompt templates
- ✅ **Logging** - Structured logs, audit trails, token tracking

## Timeline
**3-5 days** (setup, testing, understanding)

## Goal
Get the existing system running on your machine, verify it works, and understand the implementation.

---

## Day 1: Setup & Installation

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/crogers2287/agentflow-orchestrator.git
cd agentflow-orchestrator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure API Keys
```bash
# Copy example config
cp config/settings.example.yaml config/settings.yaml

# Edit settings.yaml and add your Gemini API key
# Find the line: gemini_api_key: "YOUR_API_KEY_HERE"
nano config/settings.yaml  # or use your editor
```

### Step 3: Start vLLM (AgentFlow Model)
```bash
# In a separate terminal window:
./scripts/start_vllm.sh

# This will start the AgentFlow/agentflow-planner-7b model
# Wait for "Application startup complete" message
```

### Step 4: Verify Installation
```bash
# Back in your main terminal:
python main.py health

# Expected output:
# ✅ AgentFlow: Connected (localhost:8000)
# ✅ Gemini: API key configured
# ✅ System: Ready
```

**Success Criteria:**
- ✅ Repository cloned
- ✅ Dependencies installed  
- ✅ Gemini API key configured
- ✅ vLLM running locally
- ✅ Health check passes

---

## Day 2: Basic Functionality Testing

### Test 1: Small Context Task (< 8K tokens)
```bash
python main.py run --task "Write a Python function to reverse a string"
```

**What to observe:**
- Context analysis shows ~500 tokens
- Routes to "agentflow_primary" mode
- AgentFlow generates solution
- Gemini reviews it
- Quick completion (< 30 seconds)

**Expected output:**
```
📊 Context Analysis:
   Total tokens: ~500
   Routing: agentflow_primary
   Strategy: AgentFlow builds, Gemini verifies

🤖 AgentFlow: Generating solution...
💎 Gemini: Reviewing solution...
✅ Solution approved
```

### Test 2: Code Review (Medium Context)
Create a test file `test_code.py` with ~10K tokens of code, then:

```bash
python main.py run \
  --task "Review this code for bugs and improvements" \
  --file test_code.py
```

**What to observe:**
- Context analysis shows 8K-20K tokens
- Routes to "collaborative" mode
- AgentFlow coordinates
- Gemini does comprehensive analysis
- Takes 1-2 minutes

### Test 3: Verification Loop
```bash
python main.py run --task "Write a function to divide two numbers"
```

**What to observe:**
- AgentFlow writes initial version
- Gemini catches missing zero-check
- AgentFlow refines to add validation
- Gemini approves refined version
- Multiple iterations visible

### Test 4: Debug Mode
```bash
python main.py run --debug \
  --task "Create a secure password validator"
```

**What to observe:**
- Detailed logging of every step
- Agent reasoning exposed
- Token counts at each stage
- Decision-making process visible

**Success Criteria:**
- ✅ Small context routing works
- ✅ Verification loop triggers
- ✅ Can see agent conversations
- ✅ Debug mode shows internals

---

## Day 3: Understanding the Implementation

### Read the Code (In This Order)

#### 1. Start with `main.py`
**Focus on:**
- CLI argument parsing
- How tasks are submitted
- Health check implementation
- Interactive mode

**Key questions:**
- How does the CLI call the orchestrator?
- What information gets displayed to user?
- How are files loaded and passed?

#### 2. Then `orchestrator.py`
**Focus on:**
- `process_task()` method - main entry point
- Three workflow methods (small/medium/large)
- Verification loop logic
- Debate protocol

**Key questions:**
- How does it decide which workflow to use?
- When does verification loop trigger?
- How does debate work?
- What is the state management?

#### 3. Next `context_router.py`
**Focus on:**
- Token counting with tiktoken
- Routing decision logic
- Cost estimation
- Three routing thresholds

**Key questions:**
- How are tokens counted accurately?
- What are the threshold values?
- How is cost estimated?
- Can thresholds be adjusted?

#### 4. Then `agentflow_client.py`
**Focus on:**
- vLLM integration
- Prompt formatting
- Response parsing
- Refinement methods

**Key questions:**
- How does it call vLLM?
- What prompts are used?
- How does refinement work?
- When does it "defend" solutions?

#### 5. Finally `gemini_client.py`
**Focus on:**
- Google AI SDK usage
- 2M token context handling
- Verification prompts
- Heavy lifting mode

**Key questions:**
- How is large context passed?
- What verification prompts are used?
- How does streaming work?
- Cost tracking implementation?

### Take Notes
Document your understanding:
```bash
# Create a notes file
nano UNDERSTANDING.md
```

Write down:
- How the three workflows differ
- When each routing mode triggers
- How agents communicate
- What happens during verification
- When debate activates

**Success Criteria:**
- ✅ Understand orchestrator flow
- ✅ Know how routing works
- ✅ Understand both clients
- ✅ Can explain workflows
- ✅ Notes documented

---

## Day 4: Advanced Testing

### Test 5: Large Context (If You Have Files)
If you have a codebase or document set > 100K tokens:

```bash
python main.py run \
  --task "Analyze this codebase for security issues" \
  --file src/**/*.py
```

**What to observe:**
- Routes to "gemini_heavy_lifting"
- AgentFlow breaks down task
- Gemini loads entire context
- AgentFlow directs refinement
- AgentFlow validates final result

### Test 6: Debate Scenario
```bash
python main.py run \
  --task "Sort a list of 1 million numbers - what's the best approach?"
```

**What to observe:**
- AgentFlow proposes one approach
- Gemini suggests alternative
- Debate protocol activates
- They discuss trade-offs
- Consensus reached

### Test 7: Interactive Mode
```bash
python main.py interactive
```

Try multiple tasks in sequence:
1. "Write a hello world function"
2. "Now make it thread-safe"
3. "Add error handling"
4. "Review the final version"

**What to observe:**
- Conversation continuity
- State maintained across tasks
- Agent memory of previous work

### Test 8: Edge Cases
```bash
# Very long task description
python main.py run --task "$(cat long_requirements.txt)"

# Invalid file
python main.py run --task "review this" --file nonexistent.py

# Empty task
python main.py run --task ""

# Network interruption (disconnect internet briefly)
```

**What to observe:**
- Error handling
- Recovery mechanisms
- User-friendly error messages

**Success Criteria:**
- ✅ Large context works (if tested)
- ✅ Debate activates appropriately
- ✅ Interactive mode functional
- ✅ Edge cases handled gracefully

---

## Day 5: Configuration Tuning

### Understand Current Settings

```bash
# Review current configuration
cat config/settings.yaml
cat config/prompts.yaml
```

### Experiment with Thresholds

Edit `config/settings.yaml`:

```yaml
# Try different routing thresholds
context:
  small_threshold: 8000     # Default
  large_threshold: 100000   # Default
  
# Try: 5000 and 50000 for more aggressive Gemini use
# Try: 10000 and 200000 for more AgentFlow use
```

Test with the same task using different thresholds:
```bash
python main.py run --task "Your test task here"
```

### Tune Verification Behavior

```yaml
verification:
  max_iterations: 3           # Default
  require_approval: true      # Always get Gemini's OK
  auto_refine: true          # Auto-refine on issues
```

Try:
- `max_iterations: 5` - Allow more refinement
- `require_approval: false` - Trust AgentFlow more
- `auto_refine: false` - Ask user before refining

### Customize Prompts

Edit `config/prompts.yaml`:

```yaml
agentflow:
  system: |
    You are AgentFlow, an AI coordinator.
    [Customize this for your style]
    
verification:
  critique: |
    Review this solution carefully.
    [Add specific focus areas]
```

### Test Your Changes

```bash
# Test with debug mode to see prompt usage
python main.py run --debug --task "Test task"

# Verify your prompts are being used
# Check logs for your custom text
```

**Success Criteria:**
- ✅ Understand all config options
- ✅ Experimented with thresholds
- ✅ Tuned verification settings
- ✅ Customized prompts (optional)
- ✅ Documented your preferences

---

## Phase 1 Completion Checklist

### Installation & Setup
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Gemini API key configured
- [ ] vLLM running successfully
- [ ] Health check passes

### Testing
- [ ] Small context task works
- [ ] Medium context task works  
- [ ] Verification loop observed
- [ ] Debug mode tested
- [ ] Large context tested (if possible)
- [ ] Debate scenario tested
- [ ] Interactive mode works
- [ ] Edge cases handled

### Understanding
- [ ] Read main.py
- [ ] Read orchestrator.py
- [ ] Read context_router.py
- [ ] Read agentflow_client.py
- [ ] Read gemini_client.py
- [ ] Documented understanding
- [ ] Can explain workflows

### Configuration
- [ ] Reviewed settings.yaml
- [ ] Reviewed prompts.yaml
- [ ] Tested threshold changes
- [ ] Tuned verification settings
- [ ] Customized prompts (optional)

---

## What You Should Know After Phase 1

### System Architecture
- ✅ How the three routing modes work
- ✅ When AgentFlow vs Gemini takes the lead
- ✅ How token counting drives decisions
- ✅ What verification loops do
- ✅ When debate protocol activates

### Practical Usage
- ✅ How to run tasks via CLI
- ✅ How to use debug mode
- ✅ How to adjust configuration
- ✅ How to interpret output
- ✅ How to handle errors

### Code Understanding
- ✅ Main entry points and flow
- ✅ How clients integrate
- ✅ Prompt engineering used
- ✅ State management approach
- ✅ Extensibility points

---

## Ready for Phase 2?

Before moving to Phase 2, ensure:

1. **System runs reliably** on your machine
2. **You understand** how it works
3. **You've tested** all three routing modes
4. **Configuration is tuned** to your preferences
5. **You have ideas** for what to build in Phase 2

Run this review script:

```python
# review_phase_1.py
print("Phase 1 Readiness Check")
print("="*60)

checks = {
    "vLLM running": False,
    "Gemini configured": False,
    "Small context tested": False,
    "Medium context tested": False,
    "Code understood": False,
    "Config tuned": False
}

for check, status in checks.items():
    icon = "✅" if status else "❌"
    print(f"{icon} {check}")

print("\nComplete all checks before Phase 2!")
```

---

## What's Different from Original Phase 1 Plan?

### Original Plan: Build from Scratch
- Build orchestrator
- Build clients
- Build CLI
- Build configuration
- Build logging

### Revised Plan: Test & Understand
- ✅ All code already exists!
- Focus on setup and verification
- Focus on understanding implementation
- Focus on testing all modes
- Focus on configuration tuning

### Why This Is Better
- **Faster**: 3-5 days vs 1-2 weeks
- **Lower risk**: Code is proven to work
- **Better understanding**: Learn by testing
- **Ready for Phase 2**: Can immediately build on solid foundation

---

## Next: Phase 2 Preview

Phase 2 will focus on:
- Advanced debate and synthesis
- Solution evaluation framework  
- Comprehensive testing
- Your first custom workflow

**But first**: Complete Phase 1 to ensure solid foundation!
