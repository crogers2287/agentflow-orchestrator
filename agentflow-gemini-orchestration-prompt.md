# AgentFlow + Gemini Collaborative Verification System

## Project Overview
Build an intelligent orchestration system that combines AgentFlow (using smaller, efficient models) with Gemini 2.5 Pro as both a verification partner and a large-context processor. The system enables iterative collaboration where both agents work together to arrive at optimal solutions, with intelligent routing based on task complexity and context requirements.

## Core Design Principle

**AgentFlow is ALWAYS the orchestrator, regardless of context size.**

Think of it like a construction project manager (AgentFlow) working with a structural engineer (Gemini):

- **Small projects**: Manager does most of the work, engineer reviews
- **Medium projects**: Manager coordinates, engineer provides expertise  
- **Large projects**: Manager orchestrates entire project, engineer handles complex calculations and analysis

The engineer (Gemini) never takes over the project - they provide their expertise when needed, but the manager (AgentFlow) always maintains oversight, makes decisions, and coordinates execution.

### Why This Matters

1. **Consistency**: User always interacts with AgentFlow's interface
2. **Control**: AgentFlow can validate Gemini's outputs and catch errors
3. **Efficiency**: AgentFlow breaks large tasks into manageable pieces
4. **Learning**: AgentFlow learns from interactions and improves routing
5. **Cost Management**: AgentFlow optimizes when/how to use expensive Gemini context

## System Architecture

### Phase 1: Core Orchestration Framework
Build the main orchestrator that manages the workflow between AgentFlow and Gemini:

1. **Create the Orchestrator Class** (`orchestrator.py`)
   - Task intake and parsing
   - **Context size analysis** - Determine if task requires large context window
   - Workflow state management
   - Decision logic for when to consult Gemini (verification vs. primary processing)
   - Conversation history tracking between agents
   - Solution comparison and selection logic
   - Token counting and context window optimization

2. **Agent Communication Protocol**
   - Define standardized message formats between agents
   - Create structured prompts for verification requests
   - Build response parsing for both agents
   - Implement conversation threading (so agents can reference prior exchanges)
   - **Context packaging** - Bundle large documents/codebases efficiently for Gemini

3. **Verification Workflow Engine**
   - Trigger conditions for verification (complexity thresholds, task types)
   - Multi-pass verification capability
   - Debate/discussion management when agents disagree
   - Convergence detection (when to stop iterating)

4. **Context Router** (`context_router.py`)
   - **NEW**: Analyze task requirements and route appropriately:
     - Small context (<8K tokens) → AgentFlow primary, Gemini verification
     - Medium context (8K-100K tokens) → AgentFlow coordinates, Gemini assists with context
     - Large context (100K-2M tokens) → AgentFlow orchestrates, Gemini handles heavy lifting
   - Estimate token counts before processing
   - Split large tasks intelligently if needed
   - Manage context window utilization
   - **AgentFlow ALWAYS stays in the loop** - never routes away completely

### Phase 2: AgentFlow Integration
Set up the AgentFlow component:

1. **AgentFlow Client** (`agentflow_client.py`)
   - API integration with AgentFlow or local model deployment
   - Task decomposition and planning
   - Initial solution generation (for standard-context tasks)
   - Response to critiques and refinement requests
   - Self-defense mechanisms (justify decisions when challenged)
   - **Context awareness** - Know when to defer to Gemini for large-context tasks

2. **AgentFlow Prompting Strategy**
   - System prompts for collaborative mindset
   - Instructions to be receptive to feedback
   - Format requirements for structured outputs
   - Reasoning transparency (show your work)
   - **Context limitation awareness** - Recognize when a task exceeds capabilities

### Phase 3: Gemini Integration
Set up Gemini as the verification layer AND large-context processor:

1. **Gemini Client** (`gemini_client.py`)
   - Google AI API integration (Gemini 2.5 Pro with 2M token context)
   - Rate limiting and quota management
   - Structured verification prompts
   - Alternative solution generation
   - **Large-context processing** - Handle massive documents, codebases, logs
   - Context window optimization strategies
   - Streaming for very long responses

2. **Dual-Mode Operation**
   
   **Mode A: Verification Mode** (Standard workflow - Small context)
   - AgentFlow builds solutions
   - Gemini reviews and provides critiques
   - Gemini provides alternatives when needed
   - They engage in debate when disagreeing
   
   **Mode B: Heavy Lifting Mode** (Large-context tasks)
   - AgentFlow orchestrates and coordinates
   - Gemini processes entire codebases at once
   - Gemini analyzes complete project documentation
   - Gemini reviews extensive log files or datasets
   - Gemini cross-references multiple large documents
   - AgentFlow synthesizes findings and directs next steps
   - AgentFlow validates results and requests refinements
   - **Key**: Gemini does the heavy processing, AgentFlow stays in control

3. **Verification Prompt Templates**
   Create specialized prompts for different verification modes:
   - **Correctness Review**: Logic errors, algorithm correctness
   - **Security Audit**: Vulnerabilities, injection risks, auth issues
   - **Performance Analysis**: Time/space complexity, bottlenecks
   - **Edge Case Detection**: Boundary conditions, error handling
   - **Alternative Solutions**: Better approaches, design patterns
   - **Requirements Validation**: Does it actually solve the problem?
   - **Cross-File Analysis**: Relationships across large codebases
   - **Documentation Completeness**: Gap analysis in large doc sets

4. **Large-Context Processing Templates**
   - **Codebase Analysis**: "Analyze this entire repository for..."
   - **Architecture Review**: "Review the complete system design across all files..."
   - **Log Analysis**: "Find patterns and anomalies in these 500K lines of logs..."
   - **Documentation Synthesis**: "Summarize and cross-reference these 50 documents..."
   - **Multi-File Refactoring**: "Suggest refactoring across this entire codebase..."

### Phase 4: Collaborative Decision System
Build the intelligence that mediates between agents:

1. **Solution Comparison Framework** (`solution_evaluator.py`)
   - Define evaluation criteria (correctness, efficiency, readability, maintainability)
   - Weighted scoring system
   - Pros/cons extraction from both agents
   - Conflict resolution strategies

2. **Debate Management**
   - Structured argumentation (claim → evidence → reasoning)
   - Counter-argument handling
   - Synthesis of hybrid solutions
   - Consensus detection

3. **Decision Logic**
   - When to accept AgentFlow's original solution
   - When to adopt Gemini's alternative
   - When to create a hybrid approach
   - When to request clarification from the user
   - **When to delegate heavy lifting to Gemini** (context size threshold)
   - **How AgentFlow coordinates** even during Gemini-heavy tasks

4. **Context-Aware Task Routing**
   ```python
   def route_task(task, context_size):
       if context_size < 8000:
           return "agentflow_primary"    # AgentFlow builds, Gemini verifies
       elif context_size < 100000:
           return "collaborative_medium"  # AgentFlow coordinates, Gemini provides context
       else:
           return "gemini_heavy_lifting"  # AgentFlow orchestrates, Gemini processes large context
       
       # Note: AgentFlow is ALWAYS involved - routing determines who does what,
       # not who gets excluded
   ```

### Phase 5: User Interface
Create the interaction layer:

1. **CLI Interface** (`main.py`)
   - Task submission
   - Real-time workflow visibility
   - See the "conversation" between agents
   - Manual override and guidance options
   - **Context size display** - Show token counts and routing decisions

2. **Logging and Transparency**
   - Full audit trail of decisions
   - Reasoning chains from both agents
   - Performance metrics (time, tokens used, iterations)
   - Export conversation transcripts
   - **Context utilization metrics** - Track large-context usage

## Key Features to Implement

### 1. Standard Iterative Refinement Loop (Small-Medium Context)
```
User submits task (< 100K tokens)
  ↓
AgentFlow analyzes and proposes Solution A
  ↓
Send to Gemini: "Review this solution for issues"
  ↓
Gemini responds with:
  - Issues found (if any)
  - Alternative Solution B (if significant issues)
  ↓
If issues found:
  - AgentFlow reviews Gemini's critique
  - AgentFlow either:
    a) Refines Solution A addressing issues
    b) Defends Solution A with reasoning
    c) Proposes hybrid Solution C
  ↓
Orchestrator evaluates:
  - If agents agree → proceed
  - If agents disagree → facilitate debate
  ↓
Final solution selection with justification
```

### 2. Large-Context Processing Loop (> 100K tokens)
```
User submits task with large context (e.g., entire codebase)
  ↓
Context Router analyzes: "This requires 500K tokens"
  ↓
Route to Gemini for Heavy Lifting, AgentFlow coordinates
  ↓
AgentFlow breaks down the task:
  - "What information do we need from this large context?"
  - "What's the analysis strategy?"
  - "What's the implementation plan?"
  ↓
Gemini processes entire context (heavy lifting):
  - Analyzes complete codebase
  - Identifies patterns across all files
  - Extracts relevant information
  - Provides comprehensive analysis
  ↓
AgentFlow synthesizes and orchestrates:
  - Reviews Gemini's findings
  - Asks targeted follow-up questions to Gemini
  - Plans implementation steps
  - Coordinates execution
  ↓
Iterative collaboration:
  - AgentFlow: "Based on your analysis, implement solution for module X"
  - Gemini: Implements with full context awareness
  - AgentFlow: Reviews, identifies gaps, requests refinements
  - Gemini: Refines using large context
  ↓
Result: Solution that leverages Gemini's context capacity 
        with AgentFlow's coordination and oversight
```

### 3. Hybrid Processing (Medium-Large Context)
```
User submits multi-file refactoring task (50K tokens)
  ↓
AgentFlow analyzes task and plans approach
  ↓
AgentFlow: "Gemini, load this entire codebase and identify refactoring opportunities"
  ↓
Gemini loads entire context and provides analysis
  ↓
AgentFlow reviews analysis and creates execution plan
  ↓
AgentFlow: "Let's start with the authentication module"
  ↓
Gemini implements changes with full context awareness
  ↓
AgentFlow reviews: "Good, but we need to update the tests"
  ↓
Gemini updates tests considering entire test suite context
  ↓
AgentFlow: "Now verify consistency across all dependent modules"
  ↓
Gemini checks with full codebase context
  ↓
Iterate until AgentFlow is satisfied with system-wide coherence
```

### 4. Debate Protocol
When agents disagree, structure the exchange:
- Round 1: Initial positions stated clearly
- Round 2: Each agent responds to the other's argument
- Round 3: Synthesis - find common ground or identify core disagreement
- Orchestrator decision based on objective criteria

### 5. Context-Aware Verification
Different task types and sizes trigger different workflows:

**Small Context Tasks (<8K tokens)**
- **Security-critical code** → AgentFlow builds, Gemini deep security audit
- **Performance-critical** → AgentFlow builds, Gemini algorithmic analysis
- **Simple utilities** → AgentFlow builds, Gemini quick check

**Medium Context Tasks (8K-100K tokens)**
- **Multi-file projects** → AgentFlow coordinates, Gemini provides comprehensive analysis
- **System integration** → AgentFlow plans, Gemini handles cross-component logic
- **API design** → AgentFlow orchestrates, Gemini ensures consistency across endpoints

**Large Context Tasks (>100K tokens)**
- **Complete codebase refactoring** → AgentFlow orchestrates strategy, Gemini processes entire codebase
- **Architecture review** → AgentFlow breaks down review, Gemini performs comprehensive system analysis
- **Log analysis** → AgentFlow defines search criteria, Gemini detects patterns across massive logs
- **Documentation audit** → AgentFlow specifies requirements, Gemini cross-references entire doc set
- **Legacy system migration** → AgentFlow plans migration steps, Gemini understands full system context

### 6. Learning and Improvement
Track decisions over time:
- When was Gemini's critique helpful?
- When was AgentFlow right to defend its solution?
- Which types of tasks need more verification passes?
- What context size thresholds work best?
- How often do large-context tasks benefit from Gemini's full analysis?
- Adjust verification triggers and routing based on history

## Use Cases That Leverage Gemini's Large Context

### 1. Complete Codebase Analysis
```
Task: "Analyze my entire React application for security vulnerabilities"
Input: 200K tokens (entire codebase)
Workflow: 
  → AgentFlow: "This is a large context task, delegating analysis to Gemini"
  → AgentFlow instructs: "Gemini, load entire codebase and identify security issues"
  → Gemini loads all files
  → Gemini analyzes data flow across components
  → Gemini identifies vulnerabilities considering full context
  → AgentFlow reviews findings: "Prioritize by severity"
  → Gemini categorizes and prioritizes
  → AgentFlow: "Now provide fix recommendations for top 5"
  → Gemini provides targeted fixes with file locations
  → AgentFlow validates and presents final report to user
```

### 2. Multi-Document Research
```
Task: "Compare these 30 research papers and identify common themes"
Input: 500K tokens (30 PDFs)
Workflow:
  → Gemini loads all papers
  → Cross-references methodologies
  → Identifies patterns and contradictions
  → Synthesizes comprehensive analysis
```

### 3. Log Analysis and Debugging
```
Task: "Find the root cause of this production issue"
Input: 1M tokens (week of server logs)
Workflow:
  → AgentFlow: "Large log dataset, need Gemini for heavy lifting"
  → AgentFlow: "Gemini, load logs from Nov 1-7 and look for error patterns"
  → Gemini loads complete log history
  → Gemini identifies error patterns across time
  → AgentFlow: "Focus on errors in the payment service"
  → Gemini traces issues through multiple services
  → AgentFlow: "When did the issue start?"
  → Gemini provides timeline analysis
  → AgentFlow: "What changed before that timestamp?"
  → Gemini cross-references with full context
  → AgentFlow synthesizes root cause report with evidence
```

### 4. System Architecture Review
```
Task: "Review our microservices architecture for bottlenecks"
Input: 300K tokens (all service code + configs + docs)
Workflow:
  → AgentFlow: "Complex system analysis - Gemini, load everything"
  → Gemini loads entire system
  → AgentFlow: "Map out all service dependencies"
  → Gemini analyzes service dependencies
  → AgentFlow: "Identify communication bottlenecks"
  → Gemini identifies communication patterns and issues
  → AgentFlow: "What are the top 3 bottlenecks?"
  → Gemini prioritizes with evidence from full context
  → AgentFlow: "Propose solutions for the database bottleneck"
  → Gemini recommends optimizations considering entire system
  → AgentFlow validates feasibility and creates implementation plan
```

### 5. Permit Documentation Analysis (Your Use Case!)
```
Task: "Find all projects requiring permit follow-up"
Input: 150K tokens (6 months of emails + documents)
Workflow:
  → AgentFlow: "Need to search large document set - Gemini, load it"
  → Gemini loads all project communications
  → AgentFlow: "Find all permit submittals and their status"
  → Gemini identifies permit status across all projects
  → AgentFlow: "Which ones are pending for more than 30 days?"
  → Gemini cross-references submittal dates and deadlines
  → AgentFlow: "Group by project type: Dunkin, Marathon, Mobil"
  → Gemini organizes findings by category
  → AgentFlow: "Prioritize by deadline urgency"
  → Gemini generates priority list with evidence and links to source emails
  → AgentFlow creates actionable report with follow-up tasks
```

### 6. Battery System Integration (Your Use Case!)
```
Task: "Design monitoring system for 16S LiFePO4 battery"
Input: 50K tokens (datasheets + safety specs + existing code)
Workflow:
  → AgentFlow: "Safety-critical system, need comprehensive analysis"
  → AgentFlow: "Gemini, load all datasheets and safety requirements"
  → Gemini loads all technical specifications
  → AgentFlow: "What are the critical voltage thresholds across all cells?"
  → Gemini considers safety requirements across all docs
  → AgentFlow: "Design voltage monitoring strategy"
  → Gemini proposes comprehensive monitoring solution
  → AgentFlow: "What happens if sensor fails?"
  → Gemini analyzes failure modes with full context
  → AgentFlow refines design: "Add redundant monitoring"
  → Gemini updates design considering all constraints
  → AgentFlow validates against safety specs and creates implementation plan
```

## Implementation Priorities

**Sprint 1: MVP with Context Routing** (Week 1-2)
- Basic orchestrator with sequential workflow
- Context size analysis and routing logic
- Simple AgentFlow integration (can use OpenAI or local model initially)
- Gemini API integration with large-context support
- Single verification pass (no debate yet)
- CLI interface with basic logging and context size display

**Sprint 2: Dual-Mode Operation** (Week 3-4)
- Multi-pass verification for standard tasks
- Large-context processing mode for Gemini
- Debate/discussion capability
- Solution comparison framework
- Enhanced prompting strategies for both modes

**Sprint 3: Intelligence & Optimization** (Week 5-6)
- Context-aware verification triggers
- Sophisticated decision logic
- Context window optimization
- Performance monitoring
- Comprehensive testing with various context sizes

**Sprint 4: Advanced Features** (Week 7-8)
- Adaptive routing based on task history
- Hybrid processing strategies
- Cost optimization (balance context size vs. quality)
- Advanced logging and analytics
- Production hardening

## Technical Stack Recommendations

- **Language**: Python 3.10+
- **AgentFlow**: Direct API integration or local deployment (Qwen-2.5-7B or similar)
- **Gemini**: Google AI Python SDK (`google-generativeai`) with Gemini 2.5 Pro
- **Context Analysis**: tiktoken for token counting
- **Orchestration**: Custom async framework or LangChain/LangGraph
- **State Management**: Pydantic models for type safety
- **Logging**: structlog for detailed audit trails
- **CLI**: Rich library for beautiful terminal output with progress bars
- **Config**: YAML files for prompts, routing rules, and settings
- **Testing**: pytest with mock APIs
- **Document Processing**: pypdf, python-docx for loading large documents

## Context Window Strategy

### Token Budget Management
```python
CONTEXT_LIMITS = {
    "agentflow": 8000,      # AgentFlow context limit
    "gemini": 2000000,      # Gemini 2M token context
    "routing_threshold": {
        "small": 8000,      # Route to AgentFlow primary
        "medium": 100000,   # Route to Gemini primary
        "large": 100001     # Route to Gemini exclusive
    }
}
```

### Smart Context Packing
- Compress redundant information
- Remove comments/whitespace when appropriate
- Prioritize relevant files/sections
- Use summarization for reference material
- Stream responses for very long outputs

### Cost Optimization
- Track token usage per task
- Cache frequently accessed large contexts
- Implement context window sliding for iterative tasks
- Balance quality vs. cost for different task types

## Example Usage Flows

### Example 1: Standard Task (Small Context)
```python
task = "Create a Python function to validate email addresses with RFC 5322"
context_size = 2000  # Small task

# Workflow:
# 1. AgentFlow generates solution
# 2. Gemini reviews (3K tokens for review)
# 3. AgentFlow refines
# 4. Done - efficient use of both models
```

### Example 2: Multi-File Project (Medium Context)
```python
task = "Refactor authentication logic across my Express.js app"
context_size = 45000  # Medium - entire auth system

# Workflow:
# 1. Gemini loads all auth-related files
# 2. Gemini proposes refactoring strategy
# 3. AgentFlow implements file-by-file
# 4. Gemini verifies consistency across all files
# 5. Hybrid approach: Gemini's context, AgentFlow's efficiency
```

### Example 3: Large Codebase Analysis (Large Context)
```python
task = "Find all SQL injection vulnerabilities in our Django application"
context_size = 450000  # Large - entire application

# Workflow:
# 1. AgentFlow: "This requires analyzing 450K tokens"
# 2. AgentFlow: "Gemini, load entire codebase and scan for SQL patterns"
# 3. Gemini loads and analyzes all files with full context
# 4. Gemini identifies 15 potential vulnerabilities across multiple files
# 5. AgentFlow: "Show me the top 5 most critical"
# 6. Gemini prioritizes based on exploitability
# 7. AgentFlow: "For issue #1, provide the fix"
# 8. Gemini provides fix considering all code dependencies
# 9. AgentFlow validates fix won't break other modules
# 10. Iterate through all issues
# Result: AgentFlow coordinates comprehensive security audit
#         leveraging Gemini's ability to see entire codebase at once
```