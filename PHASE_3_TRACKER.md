# Phase 3 Tracker: Production Optimization & Workflows

**Status**: Ready to begin (after Phase 2 complete)
**Timeline**: 2-3 weeks
**Prerequisites**: Phase 1 & 2 complete, system tested, debate & evaluation working

## 📋 Quick Overview

Phase 3 completes the system for daily production use:
1. **Complete Custom Workflows** - Battery design + Trading verification
2. **Production Optimization** - Caching & cost tracking
3. **Performance Improvements** - Async processing & batch operations

## ✅ Pre-Phase Checklist

Before starting Phase 3, verify:
- [ ] Phase 1 & 2 complete
- [ ] Advanced debate system working
- [ ] Solution evaluation working
- [ ] One custom workflow (permits OR battery) complete
- [ ] All Phase 2 tests passing
- [ ] System used successfully for 1+ weeks

**Verification command**:
```bash
python main.py health
python main.py workflow permits --directory ./test_data
# Or battery if you built that first
python main.py costs
```

---

## 🎯 Goal 1: Complete Custom Workflows

**Timeline**: Week 1
**GitHub Issue**: Create new issue for second workflow

### Choose Your Path

#### If You Built Permits First → Build Battery Design
**File**: `src/agentflow_orchestrator/workflows/battery_design.py`

**Features**:
- [ ] Load battery specifications
- [ ] Extract safety requirements
- [ ] Design monitoring system architecture
- [ ] Generate Arduino/ESP32 code
- [ ] Create test plan
- [ ] Verify safety compliance
- [ ] Generate bill of materials
- [ ] Save all deliverables

**Components**:
```python
class BatteryDesignWorkflow:
    - design_complete_system()
    - verify_safety_compliance()
    - _load_battery_specs()
    - _generate_test_plan()
    - save_deliverables()
```

**Testing data needed**:
- EVE 280Ah LiFePO4 datasheet
- BMS specifications
- Safety standards (if available)
- Example Arduino code (optional)

#### If You Built Battery First → Build Trading Verification
**File**: `src/agentflow_orchestrator/workflows/trading_verification.py`

**Features**:
- [ ] Analyze trading algorithm logic
- [ ] Security audit (API keys, injection, etc.)
- [ ] Identify edge cases
- [ ] Performance review
- [ ] Risk assessment
- [ ] Generate test cases
- [ ] Provide recommendations

**Components**:
```python
class TradingVerificationWorkflow:
    - comprehensive_verification()
    - _analyze_algorithm()
    - _security_audit()
    - _identify_edge_cases()
    - _performance_review()
    - _assess_risks()
    - _generate_test_cases()
```

**Testing data needed**:
- Sample trading algorithm code
- API integration code
- Backtesting results (optional)

### Implementation Steps (Either Workflow)

#### Day 1: Setup & Design
```bash
# Create workflow file
touch src/agentflow_orchestrator/workflows/your_second_workflow.py

# Create test file
touch tests/test_your_second_workflow.py

# Create docs
mkdir -p docs/workflows
touch docs/workflows/your_second_workflow.md
```

**Tasks**:
- [ ] Define workflow class structure
- [ ] Define all methods
- [ ] Add configuration
- [ ] Write docstrings

#### Day 2-3: Implementation
**Tasks**:
- [ ] Implement main workflow logic
- [ ] Implement helper methods
- [ ] Add error handling
- [ ] Test with sample data
- [ ] Fix any issues

**Testing**:
```bash
# Test import
python -c "from src.agentflow_orchestrator.workflows.your_workflow import YourWorkflow; print('OK')"

# Test with data
python -c "
from src.agentflow_orchestrator.core.orchestrator import Orchestrator
from src.agentflow_orchestrator.workflows.your_workflow import YourWorkflow

orch = Orchestrator()
wf = YourWorkflow(orch)
result = wf.run('./test_data')
print(result)
"
```

#### Day 4: CLI Integration
**File**: `main.py`

**Changes**:
```python
@cli.command()
def workflow(
    name: str,
    directory: str = None,
    output: str = "./output"
):
    """Run a custom workflow"""

    if name == "battery":
        # Battery workflow code
        pass
    elif name == "trading":
        # Trading workflow code
        pass
    elif name == "permits":
        # Permits workflow code
        pass
```

**Testing**:
```bash
python main.py workflow --help
python main.py workflow battery --directory ./specs --output ./battery_output
python main.py workflow trading --directory ./trading_code --output ./audit_results
```

#### Day 5: Documentation & Final Testing
**Tasks**:
- [ ] Write usage guide (`docs/workflows/your_workflow.md`)
- [ ] Add examples to README
- [ ] Create example data directory
- [ ] Write comprehensive tests
- [ ] Test end-to-end multiple times

---

## 🎯 Goal 2: Production Optimization

**Timeline**: Week 2
**GitHub Issue**: #4 (Context optimization)

### Step 1: Implement Caching (Day 1-2)
**File**: `src/agentflow_orchestrator/production/cache.py`

**Features**:
- [ ] Generate cache keys from files + task
- [ ] Store results with timestamp
- [ ] Check cache freshness (max age)
- [ ] Invalidate stale cache
- [ ] Cache large context results only

**Implementation checklist**:
```python
class ContextCache:
    - [ ] get_cache_key(files, task) → str
    - [ ] get(files, task, max_age_hours) → Optional[dict]
    - [ ] set(files, task, result) → None
    - [ ] invalidate(cache_key) → None
    - [ ] clear_old(max_age_days) → int
```

**Testing**:
```bash
# Test caching
python main.py run --task "analyze this" --file test.py
# First run: processes normally
python main.py run --task "analyze this" --file test.py
# Second run: should say "Using cached result"

# Modify file
echo "# comment" >> test.py
python main.py run --task "analyze this" --file test.py
# Should reprocess (cache invalidated)
```

**Integration**:
```python
# In orchestrator.py
from .production.cache import ContextCache

class Orchestrator:
    def __init__(self):
        self.cache = ContextCache()

    def process_task(self, task, files, use_cache=True):
        if use_cache and files:
            cached = self.cache.get(files, task)
            if cached:
                return cached

        result = self._process_internal(task, files)

        if files and len(files) > 5:
            self.cache.set(files, task, result)

        return result
```

### Step 2: Implement Cost Tracking (Day 3-4)
**File**: `src/agentflow_orchestrator/production/cost_tracker.py`

**Features**:
- [ ] Track per-call costs
- [ ] Daily and monthly totals
- [ ] Budget limit warnings
- [ ] Cost breakdown by model
- [ ] Average cost per call

**Implementation checklist**:
```python
class CostTracker:
    - [ ] track_api_call(model, input_tokens, output_tokens) → float
    - [ ] get_summary() → dict
    - [ ] check_budget() → bool
    - [ ] _load_costs() → dict
    - [ ] _save_costs() → None
```

**Pricing (update as needed)**:
```python
pricing = {
    'gemini-2.5-pro-input': 0.00125,   # $1.25 per 1M tokens
    'gemini-2.5-pro-output': 0.005,    # $5 per 1M tokens
    'agentflow-7b': 0.0001,            # Negligible (local)
}
```

**CLI Command**:
```python
@cli.command()
def costs():
    """Show cost summary"""
    summary = orchestrator.cost_tracker.get_summary()

    console.print("\n💰 Cost Summary")
    console.print(f"  Today: {summary['today']}")
    console.print(f"  This Month: {summary['month']}")
    console.print(f"  Total: {summary['total']}")
    console.print(f"  API Calls: {summary['calls']}")
```

**Testing**:
```bash
# Run some tasks
python main.py run --task "test 1"
python main.py run --task "test 2"
python main.py run --task "test 3"

# Check costs
python main.py costs

# Should show:
# Today: $0.15
# This Month: $5.23
# Total: $12.45
# API Calls: 15
```

**Integration**:
```python
# In agentflow_client.py and gemini_client.py
def generate(self, prompt):
    response = # ... API call

    # Track cost
    self.cost_tracker.track_api_call(
        model=self.model_name,
        input_tokens=len(prompt_tokens),
        output_tokens=len(response_tokens)
    )

    return response
```

### Step 3: Configuration & Testing (Day 5)
**File**: `config/settings.yaml`

**Add sections**:
```yaml
production:
  caching:
    enabled: true
    directory: ".cache"
    max_age_hours: 24
    min_files_to_cache: 5

  cost_tracking:
    enabled: true
    daily_limit: 50.0
    monthly_limit: 500.0
    warn_at_percent: 80
```

**Testing checklist**:
- [ ] Caching works for large context
- [ ] Cache invalidates when files change
- [ ] Cache respects max age
- [ ] Cost tracking is accurate
- [ ] Budget warnings appear
- [ ] Costs command shows correct data
- [ ] Can disable caching via config
- [ ] Can adjust limits via config

---

## 🎯 Goal 3: Performance Improvements

**Timeline**: Week 3
**GitHub Issue**: Create new issue

### Step 1: Batch Processing (Day 1-2)
**File**: `src/agentflow_orchestrator/core/orchestrator.py`

**Feature**:
```python
def batch_process_documents(
    self,
    documents: List[str],
    batch_size: int = 10,
    task_template: str = "Analyze these documents"
):
    """Process many documents in manageable batches"""

    results = []
    total_batches = (len(documents) + batch_size - 1) // batch_size

    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        batch_num = i // batch_size + 1

        console.print(f"Processing batch {batch_num}/{total_batches}")

        result = self.process_task(
            task=task_template,
            files=batch
        )
        results.append(result)

    # Synthesize all batch results
    final = self._synthesize_batch_results(results)
    return final
```

**Testing**:
```bash
# Create 50 test files
for i in {1..50}; do echo "test $i" > test_$i.txt; done

# Batch process
python -c "
from src.agentflow_orchestrator.core.orchestrator import Orchestrator
orch = Orchestrator()
files = [f'test_{i}.txt' for i in range(1, 51)]
result = orch.batch_process_documents(files, batch_size=10)
print(result)
"
```

### Step 2: Async Processing (Day 3-4)
**File**: `src/agentflow_orchestrator/core/async_orchestrator.py`

**Feature** (optional, advanced):
```python
class AsyncOrchestrator(Orchestrator):
    """Async version for parallel task processing"""

    async def process_multiple_tasks(
        self,
        tasks: List[str]
    ) -> List[dict]:
        """Process multiple tasks in parallel"""
        results = await asyncio.gather(*[
            self._process_task_async(task)
            for task in tasks
        ])
        return results
```

**Note**: This is optional. Only implement if you need to process many tasks in parallel.

### Step 3: Performance Testing (Day 5)
**Create**: `tests/test_performance.py`

**Tests**:
- [ ] Large file processing time
- [ ] Cache hit rate
- [ ] Memory usage
- [ ] Batch vs. sequential comparison
- [ ] Token efficiency

**Benchmark script**:
```python
# tests/benchmark.py
import time
from src.agentflow_orchestrator.core.orchestrator import Orchestrator

def benchmark_large_context():
    orch = Orchestrator()

    # Create large context
    large_files = create_test_files(100, 1000)  # 100 files, 1K lines each

    start = time.time()
    result = orch.process_task(
        task="Summarize these files",
        files=large_files
    )
    elapsed = time.time() - start

    print(f"Large context: {elapsed:.2f}s")
    print(f"Tokens processed: {result['token_count']}")
    print(f"Cost: ${result['cost']:.4f}")

# Run benchmarks
if __name__ == "__main__":
    benchmark_large_context()
    benchmark_caching()
    benchmark_batch_processing()
```

---

## 📊 Phase 3 Completion Checklist

### Workflows
- [ ] Second workflow implemented
- [ ] CLI commands for both workflows
- [ ] Documentation for both
- [ ] Tests for both
- [ ] Example data for both
- [ ] Successfully used in practice

### Production Features
- [ ] Caching system working
- [ ] Cache invalidation correct
- [ ] Cost tracking accurate
- [ ] Budget limits enforced
- [ ] Costs command functional
- [ ] Configuration options work

### Performance
- [ ] Batch processing works
- [ ] Performance is acceptable
- [ ] Memory usage reasonable
- [ ] No memory leaks detected
- [ ] Benchmarks documented

### Quality
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Code reviewed
- [ ] No critical bugs
- [ ] Ready for daily use

---

## 🎓 Success Criteria

Phase 3 is complete when:
1. ✅ All custom workflows implemented (permits + battery/trading)
2. ✅ Caching reduces repeated work
3. ✅ Cost tracking provides visibility
4. ✅ System performs well for daily use
5. ✅ Ready for production!

---

## 🚀 Daily Usage After Phase 3

### Morning Routine
```bash
# Check yesterday's costs
python main.py costs

# Process permits
python main.py workflow permits --directory ~/permits

# Review results
cat output/permits_report.md
```

### During Day
```bash
# Verify trading algorithm
python main.py workflow trading --directory ~/trading

# Design battery system
python main.py workflow battery --directory ~/specs --output ~/battery_design

# Ad-hoc tasks
python main.py run --task "Your question here"
```

### Evening
```bash
# Review costs
python main.py costs

# Check cache stats
ls -lh .cache/

# Review logs
tail -n 100 logs/agentflow_*.log
```

---

## 🎉 You Did It!

After Phase 3, you have:

### Complete System ✅
- Three-tier context routing
- Advanced debate & evaluation
- Multiple custom workflows
- Production optimization
- Cost tracking & limits
- Caching system
- Performance tuned

### Ready For ✅
- Daily production use
- Multiple concurrent workflows
- Large document processing
- Budget-conscious operation
- Reliable automation

### Next Steps 💡
- Use it daily for 2-4 weeks
- Refine workflows based on experience
- Add more workflows as needed
- Consider Phase 4 features:
  - Adaptive learning
  - Web UI
  - Document processing
  - More integrations

---

## 📚 Resources

**Implementation Reference**:
- `phase-3-revised-production.md` - Detailed plan
- `DEVELOPMENT.md` - Architecture guide
- Existing workflow code - Templates

**GitHub Issues**:
- #4 - Context optimization
- #6 - Document processing (future)
- Create new issues for your workflows

**Testing**:
```bash
# Run all tests
pytest tests/ -v

# Performance benchmarks
python tests/benchmark.py

# End-to-end test
python main.py workflow permits --directory examples/permits/
python main.py workflow battery --directory examples/battery/
python main.py costs
```

---

## 💡 Pro Tips

**Caching**:
- Cache large contexts (>100K tokens)
- Don't cache small quick tasks
- Set appropriate max_age
- Monitor cache hit rate

**Cost Tracking**:
- Review costs daily
- Adjust budgets as needed
- Use caching to reduce costs
- Batch similar tasks

**Workflows**:
- Start simple, refine over time
- Use real data for testing
- Document edge cases
- Handle errors gracefully

**Performance**:
- Batch large document sets
- Use cache aggressively
- Monitor memory usage
- Profile slow operations

---

## 🆘 Common Issues

**Cache not working**:
- Check `.cache/` directory exists
- Verify file paths are consistent
- Check max_age setting
- Look for cache key collisions

**Costs seem wrong**:
- Verify pricing in `cost_tracker.py`
- Check Gemini API pricing page
- Confirm token counts are accurate
- Review `.cache/costs.json`

**Performance slow**:
- Check if caching is enabled
- Reduce batch size if memory issues
- Profile with debug mode
- Check vLLM is running properly

**Workflows failing**:
- Verify input data format
- Check file paths
- Review error logs
- Test with minimal data first

---

**Phase 3 Complete = Production Ready! 🎊**

The system is now fully functional for daily production use. All three phases complete, all features working, ready to deliver value every day.

**Congratulations!** 🚀
