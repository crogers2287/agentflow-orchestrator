# Development Guide

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Settings

```bash
# Copy example config
cp config/settings.example.yaml config/settings.yaml

# Edit with your API keys
nano config/settings.yaml
```

Add your Gemini API key:
```yaml
api_keys:
  gemini_api_key: "your-actual-api-key-here"
```

### 3. Start vLLM Server

In a separate terminal:

```bash
# Start vLLM with AgentFlow model
./scripts/start_vllm.sh
```

This will download and serve the `AgentFlow/agentflow-planner-7b` model on port 8000.

### 4. Test the System

```bash
# Check health
python main.py health

# Check status
python main.py status

# Run a simple task
python main.py run --task "Write a Python function to validate email addresses"

# Run with context
python main.py run --task "Analyze this code for bugs" --file mycode.py

# Interactive mode
python main.py interactive
```

## Architecture Overview

### Core Components

```
src/agentflow_orchestrator/
├── core/
│   ├── orchestrator.py      # Main workflow manager
│   └── context_router.py    # Context analysis and routing
├── clients/
│   ├── agentflow_client.py  # vLLM/AgentFlow integration
│   └── gemini_client.py     # Google Gemini API client
└── utils/
    └── logger.py            # Structured logging setup
```

### Workflow Modes

1. **Small Context (< 8K tokens)**
   - AgentFlow: Primary processor
   - Gemini: Verifier
   - Use case: Simple tasks, code generation

2. **Medium Context (8K-100K tokens)**
   - AgentFlow: Coordinator
   - Gemini: Context handler
   - Use case: Multi-file projects, API design

3. **Large Context (> 100K tokens)**
   - AgentFlow: Orchestrator
   - Gemini: Heavy lifter (processes entire context)
   - Use case: Codebase analysis, log processing

## Development Tasks

### Adding New Prompt Templates

Edit `config/prompts.yaml`:

```yaml
custom_prompts:
  my_new_prompt: |
    Your prompt template here
    Use {variables} for substitution
```

### Adding New Verification Modes

In `gemini_client.py`, add new method:

```python
async def my_verification(self, task: str, solution: str) -> GeminiResponse:
    # Your verification logic
    pass
```

### Extending the Orchestrator

In `orchestrator.py`, add new workflow stage:

```python
async def _my_new_workflow(self, state: WorkflowState) -> WorkflowState:
    # Your workflow logic
    pass
```

## Testing

### Unit Tests

```bash
pytest tests/
```

### Integration Tests

```bash
# Test small context workflow
python main.py run --task "Simple task here"

# Test medium context
python main.py run --task "Complex task" --file file1.py --file file2.py

# Test large context (requires large files)
python main.py run --task "Analyze entire codebase" --file project/*.py
```

## Debugging

### Enable Debug Logging

```bash
python main.py run --task "Your task" --debug
```

### Check Logs

```bash
tail -f logs/agentflow_*.log
```

### Test vLLM Connection

```bash
curl http://localhost:8000/health
```

### Test Gemini API

```python
from src.agentflow_orchestrator.clients.gemini_client import GeminiClient
import asyncio

config = {"api_keys": {"gemini_api_key": "your-key"}, "models": {"gemini": {}}}
client = GeminiClient(config)

async def test():
    response = await client.generate("Hello, Gemini!")
    print(response.content)

asyncio.run(test())
```

## Performance Optimization

### Token Usage Tracking

The system automatically tracks token usage. Check after each run:

```
Token Usage:
agentflow_initial: 1,234
gemini_verification: 5,678
TOTAL: 6,912
```

### Caching

Enable caching in `config/settings.yaml`:

```yaml
performance:
  enable_caching: true
  cache_ttl_seconds: 3600
```

### Streaming for Large Responses

Automatically enabled for contexts > 500K tokens.

## Common Issues

### vLLM Not Starting

- Check GPU availability: `nvidia-smi`
- Verify CUDA installation
- Try CPU mode: add `--device cpu` to vLLM command

### Gemini API Errors

- Verify API key in config
- Check quota limits at Google AI Studio
- Review safety settings in `gemini_client.py`

### Out of Memory

- Reduce `max_model_len` in vLLM
- Split large contexts using `should_split` logic
- Use streaming mode for large responses

## Contributing

1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request

## Roadmap

See GitHub Issues for planned features and improvements.
