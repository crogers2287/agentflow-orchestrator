# Phase 3: Production Optimization & Remaining Workflows (REVISED)

## Context

You now have:
- ✅ Working Sprint 1 MVP (Phase 1)
- ✅ Advanced debate and evaluation (Phase 2)
- ✅ One custom workflow (permits OR battery)

Phase 3 completes your system for daily production use.

## Timeline
**2-3 weeks**

---

## Goal 1: Complete Your Custom Workflows (Week 1)

Build the workflows you didn't do in Phase 2.

### Workflow 2: Battery Design (if you did permits first)

```python
# src/agentflow_orchestrator/workflows/battery_design.py

class BatteryDesignWorkflow:
    """
    Design monitoring system for 16S LiFePO4 battery pack
    Uses EVE 280Ah cells with safety-critical requirements
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.config = {
            'cells': 16,
            'cell_type': 'EVE 280Ah LiFePO4',
            'nominal_voltage': 3.2,
            'max_voltage': 3.65,
            'min_voltage': 2.5,
            'max_current': 280,
            'target_pack_voltage': 51.2  # 16 * 3.2V
        }
    
    def design_complete_system(self, spec_directory: str):
        """
        End-to-end battery monitoring system design
        """
        print("\n🔋 BATTERY MONITORING SYSTEM DESIGN")
        print("=" * 60)
        
        # Step 1: Load all specifications
        specs = self._load_battery_specs(spec_directory)
        print(f"📄 Loaded {len(specs)} specification documents")
        
        # Step 2: Extract safety requirements
        safety_task = """
        Extract all safety requirements from these datasheets:
        1. Voltage limits per cell
        2. Temperature limits
        3. Current limits
        4. Failure modes to detect
        5. Required alert conditions
        """
        
        safety_reqs = self.orchestrator.process_task(
            task=safety_task,
            files=specs
        )
        
        # Step 3: Design system architecture
        design_task = f"""
        Design a monitoring system for a {self.config['cells']}-cell
        {self.config['cell_type']} battery pack:
        
        Safety Requirements:
        {safety_reqs}
        
        Design Requirements:
        1. Monitor each cell voltage individually
        2. Monitor pack current (charge/discharge)
        3. Monitor temperatures (multiple locations)
        4. Detect sensor failures
        5. Provide visual and audible alerts
        6. Log data for analysis
        7. Redundancy for critical measurements
        
        Constraints:
        - Budget: ~$200
        - Platform: Arduino Mega or Raspberry Pi
        - Must be DIY-buildable
        
        Provide:
        - System architecture diagram
        - Bill of materials
        - Wiring plan
        - Software architecture
        """
        
        design = self.orchestrator.process_task(
            task=design_task,
            files=specs
        )
        
        # Step 4: Generate implementation code
        code_task = f"""
        Implement the monitoring system based on this design:
        {design}
        
        Generate:
        1. Arduino/C++ code for voltage monitoring
        2. Current sensing code
        3. Temperature monitoring
        4. Alert logic
        5. Data logging
        6. Calibration routines
        
        Include extensive comments and safety checks.
        """
        
        code = self.orchestrator.process_task(task=code_task)
        
        # Step 5: Generate test plan
        test_plan = self._generate_test_plan(design)
        
        # Step 6: Create documentation
        docs = self._create_documentation(design, code, test_plan)
        
        return {
            'safety_requirements': safety_reqs,
            'system_design': design,
            'implementation_code': code,
            'test_plan': test_plan,
            'documentation': docs,
            'bill_of_materials': self._extract_bom(design)
        }
    
    def verify_safety_compliance(self, design: str, specs: List[str]):
        """
        Verify design meets all safety requirements
        """
        task = f"""
        Verify this battery monitoring design is safe:
        
        Design:
        {design}
        
        Check against specifications and answer:
        1. Are all voltage limits enforced?
        2. Are temperature limits monitored?
        3. Is overcurrent protection present?
        4. What happens if a sensor fails?
        5. Are there any unsafe failure modes?
        6. Is the alert system redundant?
        
        Be critical - this is safety-critical equipment.
        """
        
        verification = self.orchestrator.process_task(
            task=task,
            files=specs
        )
        
        return verification
    
    def _load_battery_specs(self, directory: str) -> List[str]:
        """Load all battery-related documents"""
        from pathlib import Path
        
        specs = []
        spec_dir = Path(directory)
        
        for file_path in spec_dir.rglob('*'):
            if file_path.suffix in ['.pdf', '.txt', '.md']:
                specs.append(str(file_path))
        
        return specs
    
    def _generate_test_plan(self, design: str) -> str:
        """Generate comprehensive test plan"""
        task = f"""
        Create a test plan for this battery monitoring system:
        {design}
        
        Include:
        1. Unit tests for each component
        2. Integration tests
        3. Safety tests (what if scenarios)
        4. Calibration procedures
        5. Acceptance criteria
        
        Be thorough - this is safety equipment.
        """
        
        return self.orchestrator.process_task(task=task)
    
    def save_deliverables(self, result: dict, output_dir: str):
        """Save all design deliverables"""
        from pathlib import Path
        
        output = Path(output_dir)
        output.mkdir(exist_ok=True)
        
        # Save design document
        with open(output / 'DESIGN.md', 'w') as f:
            f.write(result['system_design'])
        
        # Save code
        with open(output / 'battery_monitor.ino', 'w') as f:
            f.write(result['implementation_code'])
        
        # Save test plan
        with open(output / 'TEST_PLAN.md', 'w') as f:
            f.write(result['test_plan'])
        
        # Save BOM
        with open(output / 'BOM.md', 'w') as f:
            f.write(result['bill_of_materials'])
        
        print(f"\n💾 All deliverables saved to {output_dir}/")
```

### Workflow 3: Trading Algorithm Verification

```python
# src/agentflow_orchestrator/workflows/trading_verification.py

class TradingVerificationWorkflow:
    """
    Verify trading algorithms for correctness, security, and performance
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def comprehensive_verification(self, algorithm_files: List[str]):
        """
        Complete verification of trading algorithm
        """
        print("\n📈 TRADING ALGORITHM VERIFICATION")
        print("=" * 60)
        
        # Step 1: Code analysis
        analysis = self._analyze_algorithm(algorithm_files)
        
        # Step 2: Security audit
        security = self._security_audit(algorithm_files)
        
        # Step 3: Edge case identification
        edge_cases = self._identify_edge_cases(algorithm_files)
        
        # Step 4: Performance review
        performance = self._performance_review(algorithm_files)
        
        # Step 5: Risk assessment
        risks = self._assess_risks(algorithm_files)
        
        # Step 6: Generate test cases
        tests = self._generate_test_cases(edge_cases, algorithm_files)
        
        return {
            'analysis': analysis,
            'security_issues': security,
            'edge_cases': edge_cases,
            'performance_issues': performance,
            'risk_assessment': risks,
            'test_cases': tests,
            'recommendation': self._generate_recommendation(
                security, risks, performance
            )
        }
    
    def _analyze_algorithm(self, files: List[str]) -> str:
        """Analyze trading logic"""
        task = """
        Analyze this trading algorithm:
        
        1. What is the trading strategy?
        2. How does it make buy/sell decisions?
        3. What data does it use?
        4. How does it manage position sizing?
        5. What risk controls are in place?
        
        Provide a clear explanation of the logic.
        """
        
        return self.orchestrator.process_task(task=task, files=files)
    
    def _security_audit(self, files: List[str]) -> dict:
        """Security-focused review"""
        task = """
        Security audit of this trading code:
        
        Check for:
        1. API key exposure or hardcoding
        2. Input validation on external data
        3. SQL injection possibilities
        4. Authentication/authorization issues
        5. Logging of sensitive data
        6. Rate limiting on API calls
        7. Error handling that leaks info
        
        Rate each issue: Critical, High, Medium, Low
        Provide specific line numbers and fixes.
        """
        
        audit = self.orchestrator.process_task(task=task, files=files)
        return self._parse_security_audit(audit)
    
    def _identify_edge_cases(self, files: List[str]) -> List[str]:
        """Find edge cases"""
        task = """
        Identify edge cases this trading algorithm must handle:
        
        Consider:
        1. Market closed (weekends, holidays)
        2. After-hours trading
        3. Extreme volatility (circuit breakers)
        4. Zero liquidity
        5. API rate limits
        6. Network failures
        7. Invalid/stale data
        8. Account balance edge cases
        9. Earnings announcements
        10. Stock splits/dividends
        
        For each, explain: What could go wrong?
        """
        
        return self.orchestrator.process_task(task=task, files=files)
    
    def _generate_test_cases(
        self, 
        edge_cases: List[str], 
        files: List[str]
    ) -> str:
        """Generate comprehensive test suite"""
        task = f"""
        Generate test cases for this trading algorithm.
        
        Edge cases to cover:
        {edge_cases}
        
        For each test case provide:
        1. Test name
        2. Setup (market conditions, account state)
        3. Action (what happens)
        4. Expected result
        5. Python/pytest code
        
        Include both unit tests and integration tests.
        """
        
        return self.orchestrator.process_task(task=task, files=files)
```

### Add to CLI

```python
@app.command()
def workflow(
    workflow_name: str = typer.Argument(...),
    directory: str = typer.Option(None),
    output: str = typer.Option("./output", help="Output directory")
):
    """Run a custom workflow"""
    
    if workflow_name == "battery":
        from agentflow_orchestrator.workflows.battery_design import BatteryDesignWorkflow
        wf = BatteryDesignWorkflow(orchestrator)
        result = wf.design_complete_system(directory)
        wf.save_deliverables(result, output)
        console.print(f"[green]✅ Battery design complete![/green]")
        console.print(f"[blue]📁 Output: {output}/[/blue]")
        
    elif workflow_name == "trading":
        from agentflow_orchestrator.workflows.trading_verification import TradingVerificationWorkflow
        import glob
        files = glob.glob(f"{directory}/**/*.py", recursive=True)
        wf = TradingVerificationWorkflow(orchestrator)
        result = wf.comprehensive_verification(files)
        
        # Display results
        console.print("\n[bold]Security Issues:[/bold]")
        for issue in result['security_issues']:
            console.print(f"  • {issue}")
        
        console.print("\n[bold]Edge Cases:[/bold]")
        for case in result['edge_cases'][:5]:
            console.print(f"  • {case}")
        
        console.print(f"\n[bold]Recommendation:[/bold] {result['recommendation']}")
```

---

## Goal 2: Production Optimization (Week 2)

### Caching System

```python
# src/agentflow_orchestrator/production/cache.py

import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

class ContextCache:
    """
    Cache large context analyses to avoid reprocessing
    """
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def get_cache_key(self, files: List[str], task: str) -> str:
        """Generate cache key from files and task"""
        hasher = hashlib.sha256()
        
        # Hash file contents and modification times
        for filepath in sorted(files):
            path = Path(filepath)
            if path.exists():
                hasher.update(path.read_bytes())
                hasher.update(str(path.stat().st_mtime).encode())
        
        # Hash task
        hasher.update(task.encode())
        
        return hasher.hexdigest()[:16]
    
    def get(
        self, 
        files: List[str], 
        task: str, 
        max_age_hours: int = 24
    ) -> Optional[dict]:
        """
        Retrieve cached result if available and fresh
        """
        cache_key = self.get_cache_key(files, task)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        # Load cache
        with open(cache_file, 'r') as f:
            cached = json.load(f)
        
        # Check age
        cached_time = datetime.fromisoformat(cached['timestamp'])
        age = datetime.now() - cached_time
        
        if age > timedelta(hours=max_age_hours):
            return None  # Too old
        
        return cached['result']
    
    def set(self, files: List[str], task: str, result: dict):
        """
        Cache result
        """
        cache_key = self.get_cache_key(files, task)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cached = {
            'timestamp': datetime.now().isoformat(),
            'files': [str(f) for f in files],
            'task': task,
            'result': result
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cached, f, indent=2)
```

### Cost Tracking

```python
# src/agentflow_orchestrator/production/cost_tracker.py

import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict

class CostTracker:
    """
    Track API costs and enforce budgets
    """
    
    def __init__(self, cost_file: str = ".cache/costs.json"):
        self.cost_file = Path(cost_file)
        self.cost_file.parent.mkdir(exist_ok=True)
        self.costs = self._load_costs()
        
        # Pricing (per 1K tokens)
        self.pricing = {
            'gemini-2.5-pro-input': 0.00125,   # $1.25 per 1M
            'gemini-2.5-pro-output': 0.005,    # $5 per 1M
            'agentflow-7b': 0.0001,            # Negligible (local)
        }
        
        # Budget limits
        self.daily_limit = 50.0   # $50/day
        self.monthly_limit = 500.0  # $500/month
    
    def track_api_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Track an API call and return cost
        """
        # Calculate cost
        if 'gemini' in model.lower():
            input_cost = (input_tokens / 1000) * self.pricing['gemini-2.5-pro-input']
            output_cost = (output_tokens / 1000) * self.pricing['gemini-2.5-pro-output']
            cost = input_cost + output_cost
        else:
            cost = (input_tokens + output_tokens) / 1000 * self.pricing.get(model, 0.0)
        
        # Record
        today = str(date.today())
        if today not in self.costs['daily']:
            self.costs['daily'][today] = 0.0
        
        self.costs['daily'][today] += cost
        self.costs['total'] += cost
        self.costs['calls'] += 1
        
        self._save_costs()
        
        # Check limits
        if self.costs['daily'][today] > self.daily_limit:
            print(f"\n⚠️  WARNING: Daily cost limit reached (${self.costs['daily'][today]:.2f})")
        
        return cost
    
    def get_summary(self) -> Dict:
        """
        Get cost summary
        """
        today = str(date.today())
        today_cost = self.costs['daily'].get(today, 0.0)
        
        # Calculate monthly
        current_month = date.today().strftime("%Y-%m")
        monthly_cost = sum(
            cost for day, cost in self.costs['daily'].items()
            if day.startswith(current_month)
        )
        
        return {
            'today': f"${today_cost:.2f}",
            'month': f"${monthly_cost:.2f}",
            'total': f"${self.costs['total']:.2f}",
            'calls': self.costs['calls'],
            'avg_per_call': f"${self.costs['total'] / max(self.costs['calls'], 1):.4f}",
            'daily_limit': f"${self.daily_limit:.2f}",
            'monthly_limit': f"${self.monthly_limit:.2f}"
        }
    
    def _load_costs(self) -> Dict:
        """Load cost data"""
        if self.cost_file.exists():
            with open(self.cost_file, 'r') as f:
                return json.load(f)
        return {
            'total': 0.0,
            'calls': 0,
            'daily': {}
        }
    
    def _save_costs(self):
        """Save cost data"""
        with open(self.cost_file, 'w') as f:
            json.dump(self.costs, f, indent=2)
```

### Integrate with Orchestrator

```python
from .production.cache import ContextCache
from .production.cost_tracker import CostTracker

class Orchestrator:
    def __init__(self, ...):
        # ... existing init ...
        self.cache = ContextCache()
        self.cost_tracker = CostTracker()
    
    def process_task(self, task: str, files: List[str] = None, use_cache: bool = True):
        """Enhanced with caching and cost tracking"""
        
        # Check cache first
        if use_cache and files:
            cached = self.cache.get(files, task)
            if cached:
                print("♻️  Using cached result")
                return cached
        
        # Process normally
        result = self._process_task_internal(task, files)
        
        # Cache if large context
        if files and len(files) > 5:
            self.cache.set(files, task, result)
        
        return result
```

### Add Cost Command to CLI

```python
@app.command()
def costs():
    """Show cost summary"""
    summary = orchestrator.cost_tracker.get_summary()
    
    console.print("\n[bold]💰 Cost Summary[/bold]")
    console.print(f"  Today: {summary['today']}")
    console.print(f"  This Month: {summary['month']}")
    console.print(f"  Total: {summary['total']}")
    console.print(f"  API Calls: {summary['calls']}")
    console.print(f"  Avg/Call: {summary['avg_per_call']}")
    console.print(f"\n[dim]Daily Limit: {summary['daily_limit']}[/dim]")
    console.print(f"[dim]Monthly Limit: {summary['monthly_limit']}[/dim]")
```

---

## Goal 3: Performance Improvements (Week 3)

### Async Processing

```python
# src/agentflow_orchestrator/core/async_orchestrator.py

import asyncio
from typing import List

class AsyncOrchestrator(Orchestrator):
    """
    Async version for parallel processing
    """
    
    async def process_multiple_tasks(
        self,
        tasks: List[str]
    ) -> List[dict]:
        """
        Process multiple tasks in parallel
        """
        results = await asyncio.gather(*[
            self._process_task_async(task)
            for task in tasks
        ])
        return results
    
    async def _process_task_async(self, task: str):
        """Async version of process_task"""
        # Implementation using aiohttp for API calls
        pass
```

### Batch Processing

```python
def batch_process_documents(
    self,
    documents: List[str],
    batch_size: int = 10
):
    """
    Process documents in batches to avoid overwhelming context window
    """
    results = []
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        print(f"\nProcessing batch {i//batch_size + 1}/{len(documents)//batch_size + 1}")
        
        result = self.process_task(
            task="Analyze these documents",
            files=batch
        )
        results.append(result)
    
    # Synthesize batch results
    final = self._synthesize_results(results)
    return final
```

---

## Testing Checklist

### Workflows
- [ ] Battery workflow completes end-to-end
- [ ] Trading verification finds real issues
- [ ] Both workflows tested with real data
- [ ] Output files generated correctly
- [ ] CLI commands work smoothly

### Production Features
- [ ] Caching reduces repeated processing
- [ ] Cache invalidation works correctly
- [ ] Cost tracking is accurate
- [ ] Budget limits enforced
- [ ] Cost command shows correct data

### Performance
- [ ] Large contexts process efficiently
- [ ] No memory leaks
- [ ] Reasonable response times
- [ ] Batch processing works

---

## Success Criteria

**Phase 3 is complete when:**
1. ✅ All three workflows implemented
2. ✅ Caching system working
3. ✅ Cost tracking accurate
4. ✅ System performant for daily use
5. ✅ Ready for production!

---

## Final System Status

After Phase 3, you have:

### Core System ✅
- Three-tier context routing
- Verification and refinement loops
- Advanced debate with evaluation
- Structured logging and audit trails

### Custom Workflows ✅
- Permit tracking (150K token docs)
- Battery system design (50K token specs)
- Trading algorithm verification

### Production Features ✅
- Context caching
- Cost tracking and limits
- Performance optimization
- Batch processing

### Quality of Life ✅
- Beautiful CLI with Rich
- Health checks
- Debug mode
- Interactive mode
- Comprehensive config

---

## Daily Usage

```bash
# Morning: Check permits
python main.py workflow permits --directory ~/permits

# Afternoon: Verify trading changes
python main.py workflow trading --directory ~/trading

# Check costs
python main.py costs

# Ad-hoc tasks
python main.py run --task "Your task here"
```

---

## You're Done! 🎉

The system is production-ready for your personal use. You can now:
1. Track permits automatically
2. Design battery systems safely
3. Verify trading algorithms confidently
4. Handle any large-context task efficiently

**Next steps**: Use it daily, refine workflows based on experience, add more workflows as needed.
