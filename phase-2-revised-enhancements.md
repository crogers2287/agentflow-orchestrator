# Phase 2: Enhanced Debate & Custom Workflows (REVISED)

## Context: Building on Sprint 1 MVP

Phase 1 (revised) got the existing system running. Now we enhance it with:
- Advanced debate capabilities (basic debate exists)
- Solution evaluation framework (missing)
- Your first custom workflow (permits or battery)

## Pre-Phase Review

Run this before starting:

```bash
# Check Phase 1 completion
python main.py health
python main.py run --task "test" --debug

# Verify you understand:
# - How routing works
# - How verification loops work  
# - How agents communicate
```

## Timeline
**1-2 weeks**

---

## Goal 1: Advanced Debate System (Week 1)

### Current State
The existing system has basic debate:
- Detects when Gemini suggests alternatives
- Allows back-and-forth
- Simple resolution

### What's Missing
- Structured argumentation framework
- Hybrid solution synthesis
- Consensus detection
- Debate history analysis

### Implementation

#### Step 1: Enhance DebateManager

Create `src/agentflow_orchestrator/core/debate_manager.py`:

```python
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Argument:
    """Structured argument in debate"""
    claim: str
    evidence: List[str]
    reasoning: str
    confidence: float  # 0.0 to 1.0

@dataclass
class DebateRound:
    """Single round of debate"""
    round_number: int
    agentflow_argument: Optional[Argument]
    gemini_argument: Optional[Argument]
    
class AdvancedDebateManager:
    """
    Enhanced debate system with structured argumentation
    """
    
    def __init__(self, agentflow_client, gemini_client):
        self.agentflow = agentflow_client
        self.gemini = gemini_client
        self.debate_history: List[DebateRound] = []
    
    def facilitate_structured_debate(
        self, 
        task: str,
        agentflow_solution: str,
        gemini_alternative: str,
        max_rounds: int = 3
    ) -> Dict:
        """
        Run structured debate with multiple rounds
        """
        print("\n🎭 ADVANCED DEBATE MODE")
        print("=" * 60)
        
        self.debate_history = []
        
        for round_num in range(1, max_rounds + 1):
            print(f"\n📢 Round {round_num}")
            
            # AgentFlow presents structured argument
            af_arg = self._get_structured_argument(
                agent="agentflow",
                task=task,
                solution=agentflow_solution,
                opponent_solution=gemini_alternative,
                previous_rounds=self.debate_history
            )
            
            # Gemini responds with structured argument
            gem_arg = self._get_structured_argument(
                agent="gemini",
                task=task,
                solution=gemini_alternative,
                opponent_solution=agentflow_solution,
                previous_rounds=self.debate_history
            )
            
            # Record round
            debate_round = DebateRound(
                round_number=round_num,
                agentflow_argument=af_arg,
                gemini_argument=gem_arg
            )
            self.debate_history.append(debate_round)
            
            # Check for convergence
            if self._detect_consensus(af_arg, gem_arg):
                print(f"\n✅ Consensus reached in round {round_num}")
                break
            
            # Check if positions have changed
            if self._detect_stalemate(self.debate_history):
                print(f"\n⚠️  Stalemate detected - moving to synthesis")
                break
        
        # Synthesize final solution
        final_solution = self._synthesize_hybrid(
            task, agentflow_solution, gemini_alternative
        )
        
        return {
            'final_solution': final_solution,
            'debate_transcript': self.debate_history,
            'rounds': len(self.debate_history),
            'resolution': 'consensus' if consensus else 'synthesis'
        }
    
    def _get_structured_argument(
        self,
        agent: str,
        task: str,
        solution: str,
        opponent_solution: str,
        previous_rounds: List[DebateRound]
    ) -> Argument:
        """
        Get structured argument from agent
        """
        # Format debate history for context
        history_text = self._format_debate_history(previous_rounds)
        
        prompt = f"""
        Task: {task}
        
        Your solution:
        {solution}
        
        Opponent's solution:
        {opponent_solution}
        
        Debate history:
        {history_text}
        
        Present a structured argument for your approach:
        
        1. CLAIM: What is your main point?
        2. EVIDENCE: What supports your claim? (3-5 points)
        3. REASONING: Why does this evidence support your claim?
        4. CONFIDENCE: How confident are you? (0.0 to 1.0)
        
        Be specific and objective. Reference concrete aspects.
        """
        
        if agent == "agentflow":
            response = self.agentflow.generate(prompt)
        else:
            response = self.gemini.generate(prompt)
        
        # Parse structured response
        return self._parse_argument(response)
    
    def _detect_consensus(
        self, 
        arg1: Argument, 
        arg2: Argument
    ) -> bool:
        """
        Detect if agents have reached consensus
        """
        # Check if claims are similar
        claim_similarity = self._compute_similarity(
            arg1.claim, arg2.claim
        )
        
        # Check if both have low confidence (agreeing to compromise)
        low_confidence = (arg1.confidence < 0.6 and 
                         arg2.confidence < 0.6)
        
        # Check if evidence overlaps significantly
        evidence_overlap = self._compute_evidence_overlap(
            arg1.evidence, arg2.evidence
        )
        
        return (claim_similarity > 0.8 or 
                low_confidence or 
                evidence_overlap > 0.7)
    
    def _detect_stalemate(
        self, 
        history: List[DebateRound]
    ) -> bool:
        """
        Detect if debate has stalled (same arguments repeating)
        """
        if len(history) < 2:
            return False
        
        # Check if last two rounds have very similar arguments
        last_round = history[-1]
        prev_round = history[-2]
        
        af_similarity = self._compute_similarity(
            last_round.agentflow_argument.claim,
            prev_round.agentflow_argument.claim
        )
        
        gem_similarity = self._compute_similarity(
            last_round.gemini_argument.claim,
            prev_round.gemini_argument.claim
        )
        
        return af_similarity > 0.9 and gem_similarity > 0.9
    
    def _synthesize_hybrid(
        self,
        task: str,
        solution_a: str,
        solution_b: str
    ) -> str:
        """
        Create hybrid solution incorporating best of both
        """
        print("\n🔄 Synthesizing hybrid solution...")
        
        # Both agents work together to create hybrid
        synthesis_prompt = f"""
        Task: {task}
        
        Two approaches have been debated:
        
        Approach A:
        {solution_a}
        
        Approach B:
        {solution_b}
        
        Debate history shows both have merits.
        
        Create a hybrid solution that:
        1. Takes the best ideas from both approaches
        2. Addresses concerns raised by both sides
        3. Is practical and implementable
        
        Explain what you took from each approach and why.
        """
        
        # AgentFlow coordinates synthesis
        hybrid = self.agentflow.generate(synthesis_prompt)
        
        # Gemini validates hybrid addresses concerns
        validation = self.gemini.verify_solution(task, hybrid)
        
        return hybrid
```

#### Step 2: Integrate with Orchestrator

Update `orchestrator.py`:

```python
from .debate_manager import AdvancedDebateManager

class Orchestrator:
    def __init__(self, ...):
        # ... existing init ...
        self.debate_manager = AdvancedDebateManager(
            self.agentflow,
            self.gemini
        )
    
    def _handle_disagreement(self, task, af_solution, gem_critique):
        """
        Enhanced disagreement handling with structured debate
        """
        if self._is_significant_disagreement(gem_critique):
            # Use advanced debate
            result = self.debate_manager.facilitate_structured_debate(
                task=task,
                agentflow_solution=af_solution,
                gemini_alternative=self._extract_alternative(gem_critique),
                max_rounds=3
            )
            
            # Save debate transcript for learning
            self._save_debate_transcript(result['debate_transcript'])
            
            return result['final_solution']
        else:
            # Simple refinement is sufficient
            return self.agentflow.refine_solution(task, af_solution, gem_critique)
```

#### Step 3: Test Debate System

```bash
# Test structured debate
python main.py run \
  --task "Design a caching system - should it be in-memory or Redis?"

# Expected:
# - Agents present structured arguments
# - Multiple rounds of debate
# - Consensus or synthesis reached
# - Debate transcript shown
```

---

## Goal 2: Solution Evaluation Framework (Week 1-2)

### What's Missing
Currently there's no systematic way to evaluate which solution is better when agents disagree.

### Implementation

#### Step 1: Create Evaluation Framework

Create `src/agentflow_orchestrator/core/evaluator.py`:

```python
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class EvaluationCriterion(Enum):
    CORRECTNESS = "correctness"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    SIMPLICITY = "simplicity"

@dataclass
class EvaluationScore:
    criterion: EvaluationCriterion
    score: float  # 0.0 to 1.0
    reasoning: str
    evidence: List[str]

class SolutionEvaluator:
    """
    Evaluate and compare solutions objectively
    """
    
    def __init__(self, gemini_client):
        self.gemini = gemini_client
        
        # Configurable weights
        self.criterion_weights = {
            EvaluationCriterion.CORRECTNESS: 0.30,
            EvaluationCriterion.PERFORMANCE: 0.20,
            EvaluationCriterion.SECURITY: 0.20,
            EvaluationCriterion.MAINTAINABILITY: 0.15,
            EvaluationCriterion.SIMPLICITY: 0.15
        }
    
    def evaluate_solution(
        self,
        task: str,
        solution: str,
        criteria: List[EvaluationCriterion] = None
    ) -> Dict[EvaluationCriterion, EvaluationScore]:
        """
        Evaluate a solution across multiple criteria
        """
        if criteria is None:
            criteria = list(EvaluationCriterion)
        
        scores = {}
        
        for criterion in criteria:
            score = self._evaluate_criterion(task, solution, criterion)
            scores[criterion] = score
        
        return scores
    
    def compare_solutions(
        self,
        task: str,
        solution_a: str,
        solution_b: str
    ) -> Dict:
        """
        Compare two solutions and recommend the better one
        """
        print("\n⚖️  Evaluating solutions...")
        
        # Evaluate both solutions
        scores_a = self.evaluate_solution(task, solution_a)
        scores_b = self.evaluate_solution(task, solution_b)
        
        # Compute weighted scores
        total_a = self._compute_weighted_score(scores_a)
        total_b = self._compute_weighted_score(scores_b)
        
        # Determine winner
        if abs(total_a - total_b) < 0.1:
            recommendation = "tie"
            winner = None
        elif total_a > total_b:
            recommendation = "solution_a"
            winner = solution_a
        else:
            recommendation = "solution_b"
            winner = solution_b
        
        return {
            'recommendation': recommendation,
            'winner': winner,
            'score_a': total_a,
            'score_b': total_b,
            'detailed_scores_a': scores_a,
            'detailed_scores_b': scores_b,
            'analysis': self._generate_analysis(scores_a, scores_b)
        }
    
    def _evaluate_criterion(
        self,
        task: str,
        solution: str,
        criterion: EvaluationCriterion
    ) -> EvaluationScore:
        """
        Evaluate solution on specific criterion
        """
        prompt = f"""
        Task: {task}
        
        Solution:
        {solution}
        
        Evaluate this solution for: {criterion.value}
        
        Provide:
        1. Score (0.0 to 1.0)
        2. Reasoning (2-3 sentences)
        3. Evidence (specific examples from solution)
        
        Be objective and specific.
        """
        
        response = self.gemini.generate(prompt)
        return self._parse_evaluation(response, criterion)
    
    def _compute_weighted_score(
        self, 
        scores: Dict[EvaluationCriterion, EvaluationScore]
    ) -> float:
        """
        Compute weighted total score
        """
        total = 0.0
        for criterion, score_obj in scores.items():
            weight = self.criterion_weights.get(criterion, 0.0)
            total += score_obj.score * weight
        return total
```

#### Step 2: Integrate with Debate Manager

```python
class AdvancedDebateManager:
    def __init__(self, agentflow_client, gemini_client):
        # ... existing init ...
        self.evaluator = SolutionEvaluator(gemini_client)
    
    def facilitate_structured_debate(self, ...):
        # ... existing debate logic ...
        
        # After debate, use evaluator to help decide
        evaluation = self.evaluator.compare_solutions(
            task=task,
            solution_a=agentflow_solution,
            solution_b=gemini_alternative
        )
        
        print(f"\n📊 Evaluation Results:")
        print(f"   Solution A score: {evaluation['score_a']:.2f}")
        print(f"   Solution B score: {evaluation['score_b']:.2f}")
        print(f"   Recommendation: {evaluation['recommendation']}")
        
        # Use evaluation to inform synthesis
        ...
```

#### Step 3: Test Evaluation

```bash
# Test solution evaluation
python main.py run \
  --task "Implement a rate limiter" \
  --debug

# Should show:
# - Structured debate
# - Evaluation scores for each solution
# - Objective comparison
# - Data-driven recommendation
```

---

## Goal 3: Your First Custom Workflow (Week 2)

Choose ONE to implement this phase:

### Option A: Permit Tracking Workflow

```python
# src/agentflow_orchestrator/workflows/permit_tracking.py

class PermitTrackingWorkflow:
    """
    Search permit documents and identify projects needing follow-up
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def find_pending_permits(
        self,
        document_directory: str,
        days_threshold: int = 30
    ):
        """
        Find all permits pending longer than threshold
        """
        print("\n🏗️  PERMIT TRACKING WORKFLOW")
        print("=" * 60)
        
        # Load documents
        docs = self._load_documents(document_directory)
        
        # Use large context workflow
        task = f"""
        Analyze these permit documents and identify:
        1. All permit submittals
        2. Current status of each
        3. Which have been pending > {days_threshold} days
        4. Group by project type (Dunkin, Marathon, Mobil, etc)
        
        Provide a prioritized action list.
        """
        
        result = self.orchestrator.process_task(
            task=task,
            files=docs
        )
        
        # Format as report
        report = self._format_permit_report(result)
        return report
```

### Option B: Battery Design Workflow

```python
# src/agentflow_orchestrator/workflows/battery_design.py

class BatteryDesignWorkflow:
    """
    Design monitoring system for 16S LiFePO4 battery
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.battery_config = {
            'cells': 16,
            'cell_type': 'EVE 280Ah LiFePO4',
            'max_voltage': 3.65,
            'min_voltage': 2.5
        }
    
    def design_monitoring_system(
        self,
        datasheet_directory: str
    ):
        """
        Design complete monitoring system
        """
        print("\n🔋 BATTERY DESIGN WORKFLOW")
        print("=" * 60)
        
        # Load specifications
        specs = self._load_specifications(datasheet_directory)
        
        # Design with safety focus
        task = f"""
        Design a monitoring system for a {self.battery_config['cells']}-cell
        {self.battery_config['cell_type']} battery pack.
        
        Requirements:
        1. Monitor each cell voltage ({self.battery_config['min_voltage']}V to {self.battery_config['max_voltage']}V)
        2. Pack current and temperature
        3. Safety alerts for out-of-range conditions
        4. Sensor failure detection
        5. Redundancy for critical measurements
        
        Output: Complete design with component list and wiring
        """
        
        result = self.orchestrator.process_task(
            task=task,
            files=specs
        )
        
        # Generate implementation code
        code = self._generate_arduino_code(result)
        return {
            'design': result,
            'code': code
        }
```

### Add to CLI

Update `main.py`:

```python
@app.command()
def workflow(
    workflow_name: str = typer.Argument(..., help="Workflow to run"),
    directory: str = typer.Option(None, help="Input directory")
):
    """Run a custom workflow"""
    
    if workflow_name == "permits":
        from agentflow_orchestrator.workflows.permit_tracking import PermitTrackingWorkflow
        wf = PermitTrackingWorkflow(orchestrator)
        result = wf.find_pending_permits(directory)
        
    elif workflow_name == "battery":
        from agentflow_orchestrator.workflows.battery_design import BatteryDesignWorkflow
        wf = BatteryDesignWorkflow(orchestrator)
        result = wf.design_monitoring_system(directory)
    
    console.print(result)
```

### Test Your Workflow

```bash
# Test permit workflow
python main.py workflow permits --directory ~/permits

# OR test battery workflow
python main.py workflow battery --directory ~/datasheets
```

---

## Testing Checklist

### Debate System
- [ ] Structured arguments generated
- [ ] Multiple debate rounds work
- [ ] Consensus detection works
- [ ] Stalemate detection works
- [ ] Hybrid synthesis works
- [ ] Debate transcripts saved

### Evaluation Framework
- [ ] Solutions evaluated on criteria
- [ ] Scores are reasonable
- [ ] Weighted scoring works
- [ ] Comparison is objective
- [ ] Recommendations make sense

### Custom Workflow
- [ ] Workflow runs end-to-end
- [ ] Handles large context correctly
- [ ] AgentFlow orchestrates properly
- [ ] Results are useful
- [ ] Can run from CLI

---

## Success Criteria

**Phase 2 is complete when:**
1. ✅ Advanced debate system works
2. ✅ Solution evaluation is objective
3. ✅ One custom workflow implemented
4. ✅ All features tested thoroughly
5. ✅ Ready to build more workflows

---

## Next: Phase 3 Preview

Phase 3 will add:
- Second custom workflow
- Context optimization and caching
- Cost tracking and limits
- Performance improvements

**But first**: Complete Phase 2!
