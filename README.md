# AgentFlow + Gemini Collaborative Verification System

An intelligent orchestration system that combines AgentFlow (using smaller, efficient models) with Gemini 2.5 Pro for collaborative problem-solving with intelligent routing based on task complexity and context requirements.

## Core Principle

**AgentFlow is ALWAYS the orchestrator, regardless of context size.**

- **Small context (<8K tokens)**: AgentFlow builds, Gemini verifies
- **Medium context (8K-100K tokens)**: AgentFlow coordinates, Gemini assists
- **Large context (>100K tokens)**: AgentFlow orchestrates, Gemini handles heavy lifting

## Architecture

### Components

- `orchestrator.py` - Main workflow manager
- `context_router.py` - Analyzes task size and routes appropriately
- `agentflow_client.py` - vLLM integration with agentflow-planner-7b
- `gemini_client.py` - Google AI API integration with 2M context
- `main.py` - CLI interface

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config/settings.example.yaml config/settings.yaml
# Edit config/settings.yaml with your API keys
```

## Usage

```bash
# Run the orchestrator
python main.py

# Process a task
python main.py --task "Analyze this codebase for security vulnerabilities"
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for development guidelines and architecture details.

## License

MIT
