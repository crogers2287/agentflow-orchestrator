# Phase 2 Tracker: Enhanced Debate & Custom Workflows

**Status**: Ready to begin (after Phase 1 complete)
**Timeline**: 1-2 weeks
**Prerequisites**: Phase 1 complete, system running, code understood

## 📋 Quick Overview

Phase 2 adds three major enhancements:
1. **Advanced Debate System** - Structured argumentation, consensus detection
2. **Solution Evaluation Framework** - Objective scoring and comparison
3. **Custom Workflow** - Your first domain-specific workflow

## ✅ Pre-Phase Checklist

Before starting Phase 2, verify:
- [ ] Phase 1 complete (all tests passing)
- [ ] System runs reliably
- [ ] You understand how routing works
- [ ] You understand verification loops
- [ ] You understand agent communication
- [ ] Configuration is tuned

**Verification command**:
```bash
python main.py health
python main.py run --task "test basic functionality" --debug
```

## 🎯 Goal 1: Advanced Debate System

**Timeline**: 3-4 days (Week 1)
**GitHub Issue**: #3

### Current State
✅ Basic debate exists in `orchestrator.py`
- Detects disagreements
- Simple back-and-forth
- Basic resolution

### What We're Building
- [ ] Structured argumentation framework
- [ ] Consensus detection algorithm
- [ ] Stalemate detection
- [ ] Hybrid solution synthesis
- [ ] Debate transcript storage

### Implementation Steps

#### Step 1: Create DebateManager (Day 1)
**File**: `src/agentflow_orchestrator/core/debate_manager.py`

**Components to build**:
- [ ] `Argument` dataclass (claim, evidence, reasoning, confidence)
- [ ] `DebateRound` dataclass
- [ ] `AdvancedDebateManager` class
- [ ] `facilitate_structured_debate()` method
- [ ] `_get_structured_argument()` method
- [ ] `_detect_consensus()` method
- [ ] `_detect_stalemate()` method
- [ ] `_synthesize_hybrid()` method

**Testing**:
```bash
# Unit tests
pytest tests/test_debate_manager.py

# Manual test
python -c "from src.agentflow_orchestrator.core.debate_manager import AdvancedDebateManager; print('Import works!')"
```

#### Step 2: Integrate with Orchestrator (Day 2)
**File**: `src/agentflow_orchestrator/core/orchestrator.py`

**Changes needed**:
- [ ] Import `AdvancedDebateManager`
- [ ] Initialize in `__init__`
- [ ] Update `_handle_disagreement()` method
- [ ] Add `_save_debate_transcript()` method
- [ ] Update `WorkflowState` to include debate data

**Testing**:
```bash
# Test with debate-triggering task
python main.py run --task "Design a caching system - in-memory or Redis?" --debug
```

#### Step 3: Add CLI Support (Day 3)
**File**: `main.py`

**Features to add**:
- [ ] Display debate rounds in output
- [ ] Show structured arguments
- [ ] Display consensus/stalemate detection
- [ ] Save debate transcripts to files
- [ ] Add `--show-debate` flag

**Testing**:
```bash
# Test debate display
python main.py run --task "Sort algorithm choice for 1M items" --show-debate

# Verify transcript saved
ls logs/debates/
```

#### Step 4: Write Tests (Day 4)
**File**: `tests/test_debate_manager.py`

**Tests to write**:
- [ ] Test argument parsing
- [ ] Test consensus detection (various scenarios)
- [ ] Test stalemate detection
- [ ] Test hybrid synthesis
- [ ] Integration test with real agents

**Run tests**:
```bash
pytest tests/test_debate_manager.py -v
pytest tests/test_debate_manager.py::test_consensus_detection
```

### Success Criteria
- [ ] Structured arguments generated correctly
- [ ] Consensus detected when agents agree
- [ ] Stalemate detected when stuck
- [ ] Hybrid solutions make sense
- [ ] All tests passing
- [ ] Works end-to-end via CLI

---

## 🎯 Goal 2: Solution Evaluation Framework

**Timeline**: 3-4 days (Week 1-2)
**GitHub Issue**: #1

### What We're Building
- [ ] Multi-criteria evaluation system
- [ ] Weighted scoring
- [ ] Objective comparison
- [ ] Detailed analysis generation

### Implementation Steps

#### Step 1: Create Evaluator (Day 1)
**File**: `src/agentflow_orchestrator/core/evaluator.py`

**Components to build**:
- [ ] `EvaluationCriterion` enum (5 criteria)
- [ ] `EvaluationScore` dataclass
- [ ] `SolutionEvaluator` class
- [ ] `evaluate_solution()` method
- [ ] `compare_solutions()` method
- [ ] `_evaluate_criterion()` method
- [ ] `_compute_weighted_score()` method
- [ ] `_generate_analysis()` method

**Testing**:
```bash
# Unit tests
pytest tests/test_evaluator.py

# Quick test
python -c "from src.agentflow_orchestrator.core.evaluator import SolutionEvaluator; print('Works!')"
```

#### Step 2: Configure Weights (Day 2)
**File**: `config/settings.yaml`

**Add section**:
```yaml
evaluation:
  weights:
    correctness: 0.30
    performance: 0.20
    security: 0.20
    maintainability: 0.15
    simplicity: 0.15

  # Optional: task-specific weights
  task_weights:
    security_audit:
      security: 0.50
      correctness: 0.30
    performance_optimization:
      performance: 0.50
      simplicity: 0.20
```

**Testing**:
```bash
# Verify config loads
python main.py status
```

#### Step 3: Integrate with Debate (Day 3)
**File**: `src/agentflow_orchestrator/core/debate_manager.py`

**Changes needed**:
- [ ] Initialize `SolutionEvaluator` in `__init__`
- [ ] Call evaluator after debate
- [ ] Use scores to inform synthesis
- [ ] Display evaluation results

**Testing**:
```bash
python main.py run --task "Implement rate limiter" --debug

# Should show:
# - Debate rounds
# - Evaluation scores
# - Objective recommendation
```

#### Step 4: Add Evaluation Prompts (Day 4)
**File**: `config/prompts.yaml`

**Add section**:
```yaml
evaluation:
  correctness: |
    Evaluate correctness: Does the solution solve the problem correctly?
    Consider edge cases, error handling, logic errors.

  performance: |
    Evaluate performance: Is the solution efficient?
    Consider time/space complexity, bottlenecks.

  # ... etc for all criteria
```

**Testing**:
```bash
# Test with custom prompts
python main.py run --task "Design API endpoint" --debug
```

### Success Criteria
- [ ] Solutions evaluated on all criteria
- [ ] Scores are reasonable and consistent
- [ ] Weighted scoring works correctly
- [ ] Comparisons are objective
- [ ] Analysis provides useful insights
- [ ] Integration with debate works
- [ ] All tests passing

---

## 🎯 Goal 3: Custom Workflow

**Timeline**: 3-4 days (Week 2)
**GitHub Issue**: Pick your domain

### Choose ONE to implement

#### Option A: Permit Tracking Workflow
**Best if**: You work with construction permits or document tracking

**Features**:
- [ ] Load permit documents
- [ ] Identify pending permits
- [ ] Group by project type
- [ ] Calculate days pending
- [ ] Generate priority report

**Testing data needed**:
- Collection of permit documents (PDFs or emails)
- At least 10-20 documents for testing

#### Option B: Battery Design Workflow
**Best if**: You work with electronics or battery systems

**Features**:
- [ ] Load battery specs and datasheets
- [ ] Design monitoring system
- [ ] Safety validation
- [ ] Generate Arduino/ESP32 code
- [ ] Component list with part numbers

**Testing data needed**:
- Battery datasheets (EVE LiFePO4)
- BMS specifications
- Safety requirements

### Implementation Steps (Either Workflow)

#### Step 1: Create Workflow Module (Day 1)
**File**: `src/agentflow_orchestrator/workflows/[your_workflow].py`

**Structure**:
```python
class YourWorkflow:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        # Workflow-specific config

    def run(self, inputs):
        # Main workflow logic
        pass

    def _load_documents(self, directory):
        # Load input files
        pass

    def _format_results(self, raw_results):
        # Format output
        pass
```

**Testing**:
```bash
# Test import
python -c "from src.agentflow_orchestrator.workflows.your_workflow import YourWorkflow; print('Works!')"
```

#### Step 2: Implement Core Logic (Day 2)
**Tasks**:
- [ ] Document loading logic
- [ ] Task formulation for orchestrator
- [ ] Result parsing and formatting
- [ ] Error handling

**Testing**:
```bash
# Test with sample data
python -c "
from src.agentflow_orchestrator.workflows.your_workflow import YourWorkflow
from src.agentflow_orchestrator.core.orchestrator import Orchestrator

orch = Orchestrator()
wf = YourWorkflow(orch)
result = wf.run('./test_data')
print(result)
"
```

#### Step 3: Add CLI Command (Day 3)
**File**: `main.py`

**Add command**:
```python
@cli.command()
def workflow(
    name: str,
    directory: str = None,
    output: str = None
):
    """Run a custom workflow"""
    # Implementation
```

**Testing**:
```bash
python main.py workflow --help
python main.py workflow permits --directory ./test_data
```

#### Step 4: Documentation and Testing (Day 4)
**Create**:
- [ ] `docs/workflows/[your_workflow].md` - Usage guide
- [ ] `tests/test_[your_workflow].py` - Tests
- [ ] Example data in `examples/[your_workflow]/`

**Testing**:
```bash
pytest tests/test_your_workflow.py -v
python main.py workflow your_workflow --directory examples/your_workflow/
```

### Success Criteria
- [ ] Workflow runs end-to-end
- [ ] Handles large context (if needed)
- [ ] AgentFlow orchestrates properly
- [ ] Gemini does heavy lifting (if large context)
- [ ] Results are useful and formatted
- [ ] Can run from CLI
- [ ] Documentation complete
- [ ] Tests passing

---

## 📊 Phase 2 Completion Checklist

### Advanced Debate System
- [ ] DebateManager implemented
- [ ] Integrated with Orchestrator
- [ ] CLI support added
- [ ] Consensus detection works
- [ ] Stalemate detection works
- [ ] Hybrid synthesis works
- [ ] Tests written and passing
- [ ] Debate transcripts saved

### Solution Evaluation
- [ ] Evaluator implemented
- [ ] 5 criteria defined
- [ ] Weighted scoring works
- [ ] Integrated with debate
- [ ] Configuration added
- [ ] Prompts customized
- [ ] Tests written and passing
- [ ] Results are useful

### Custom Workflow
- [ ] Workflow selected
- [ ] Module implemented
- [ ] CLI command added
- [ ] Documentation written
- [ ] Tests written and passing
- [ ] Example data created
- [ ] End-to-end tested
- [ ] Ready for production use

---

## 🚀 Getting Started

### Day 1 - Setup
```bash
# Verify Phase 1 complete
python main.py health
python main.py status

# Create feature branch
git checkout -b phase-2-enhancements

# Create new directories
mkdir -p src/agentflow_orchestrator/workflows
mkdir -p tests/workflows
mkdir -p docs/workflows
mkdir -p examples
```

### Each Day
1. **Morning**: Review goal for the day
2. **Implementation**: Code with tests
3. **Testing**: Verify it works
4. **Commit**: Save progress
5. **Evening**: Update this tracker

### Git Workflow
```bash
# Commit frequently
git add .
git commit -m "feat: [what you built]"

# Push to GitHub
git push origin phase-2-enhancements

# When done, create PR
gh pr create --title "Phase 2: Enhanced Debate & Custom Workflows"
```

---

## 🆘 Troubleshooting

### Debate System Issues
**Problem**: Arguments not structured properly
**Solution**: Check prompt templates in `config/prompts.yaml`

**Problem**: Consensus never detected
**Solution**: Lower similarity threshold in `_detect_consensus()`

### Evaluation Issues
**Problem**: Scores all the same
**Solution**: Verify prompts are specific enough for each criterion

**Problem**: Weights not applied
**Solution**: Check config loading in `SolutionEvaluator.__init__`

### Workflow Issues
**Problem**: Large context not loading
**Solution**: Check file reading, token counting

**Problem**: Results not useful
**Solution**: Refine task formulation for orchestrator

---

## 📚 Resources

### Code References
- Existing debate: `src/agentflow_orchestrator/core/orchestrator.py:_debate_mode()`
- Context routing: `src/agentflow_orchestrator/core/context_router.py`
- Prompts: `config/prompts.yaml`

### Documentation
- Phase 2 plan: `phase-2-revised-enhancements.md`
- Development guide: `DEVELOPMENT.md`
- API docs: Check docstrings in code

### GitHub Issues
- #1 - Solution evaluation framework
- #3 - Advanced debate features
- #6 - Document processing (for workflows)

---

## 🎓 Learning Goals

By end of Phase 2, you should:
- ✅ Understand structured argumentation
- ✅ Know how to evaluate solutions objectively
- ✅ Be able to create custom workflows
- ✅ Understand large context processing
- ✅ Be comfortable extending the system

---

## 📈 Progress Tracking

### Week 1
- [ ] Day 1: DebateManager basics
- [ ] Day 2: Orchestrator integration
- [ ] Day 3: CLI and display
- [ ] Day 4: Debate tests
- [ ] Day 5: Evaluator basics

### Week 2
- [ ] Day 1: Evaluator integration
- [ ] Day 2: Workflow selection & setup
- [ ] Day 3: Workflow implementation
- [ ] Day 4: Workflow testing
- [ ] Day 5: Documentation & cleanup

---

## ✨ Bonus Ideas

If you finish early:
- [ ] Add web UI for debate visualization
- [ ] Create second workflow
- [ ] Add debate history analysis
- [ ] Implement adaptive weights
- [ ] Add cost tracking per workflow

---

## 🎯 Success = Ready for Phase 3

Phase 2 complete when:
1. ✅ All three goals achieved
2. ✅ All tests passing
3. ✅ Documentation complete
4. ✅ PR merged to main
5. ✅ Ready to build more features

**Next**: Phase 3 - Production hardening, monitoring, optimization

**Let's build! 🚀**
