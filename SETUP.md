# Setup Guide

## Quick Start

Follow these steps to get the AgentFlow + Gemini orchestration system running.

### 1. Prerequisites

- Python 3.10 or higher
- CUDA-capable GPU (recommended for vLLM)
- Google Gemini API key ([Get one here](https://ai.google.dev/))
- At least 16GB RAM (32GB+ recommended for large contexts)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/crogers2287/agentflow-orchestrator.git
cd agentflow-orchestrator

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy example configuration
cp config/settings.example.yaml config/settings.yaml

# Edit configuration with your API key
nano config/settings.yaml
```

**Required**: Add your Gemini API key:
```yaml
api_keys:
  gemini_api_key: "YOUR_ACTUAL_API_KEY_HERE"
```

### 4. Start vLLM Server

In a **separate terminal window**:

```bash
cd agentflow-orchestrator
source venv/bin/activate
./scripts/start_vllm.sh
```

This will:
- Download the `AgentFlow/agentflow-planner-7b` model (first time only)
- Start the vLLM server on `http://localhost:8000`
- Takes 2-5 minutes for first download

**Note**: If you don't have a GPU, vLLM will run on CPU (slower).

### 5. Verify Installation

```bash
# Check health of all components
python main.py health

# Expected output:
# System Health
# ┌─────────────────┬─────────────┐
# │ Component       │ Status      │
# ├─────────────────┼─────────────┤
# │ orchestrator    │ ✓ healthy   │
# │ agentflow       │ ✓ healthy   │
# │ gemini          │ ✓ configured│
# │ context_router  │ ✓ healthy   │
# └─────────────────┴─────────────┘

# Check model information
python main.py status
```

### 6. Run Your First Task

```bash
# Simple task (small context)
python main.py run --task "Write a Python function to calculate fibonacci numbers"

# Task with file context
python main.py run --task "Review this code for bugs" --file mycode.py

# Complex task (will demonstrate routing)
python main.py run --task "Explain the architecture of this project" --file src/agentflow_orchestrator/core/*.py
```

## Usage Examples

### Basic Task

```bash
python main.py run --task "Create a REST API endpoint for user authentication"
```

### Task with Context

```bash
python main.py run \
  --task "Refactor the database connection code" \
  --context "We're migrating from SQLite to PostgreSQL" \
  --file src/database.py
```

### Large Codebase Analysis

```bash
python main.py run \
  --task "Find all security vulnerabilities in this project" \
  --file src/**/*.py \
  --file tests/**/*.py
```

### Interactive Mode

```bash
python main.py interactive
```

Then enter tasks interactively:
```
Task> Write a function to parse JSON
Task> Optimize the previous solution for performance
Task> exit
```

## Troubleshooting

### vLLM Won't Start

**Problem**: Out of memory errors

**Solution**: Reduce model size or use CPU mode:
```bash
# Edit scripts/start_vllm.sh and add:
--max-model-len 4096
```

**Problem**: CUDA not found

**Solution**: Install CUDA toolkit or run on CPU:
```bash
pip install vllm-cpu  # CPU-only version
```

### Gemini API Errors

**Problem**: `Invalid API key`

**Solution**:
1. Verify your API key at https://ai.google.dev/
2. Check that `config/settings.yaml` has the correct key
3. Ensure no extra spaces or quotes around the key

**Problem**: `Rate limit exceeded`

**Solution**: Gemini free tier has limits. Wait or upgrade to paid tier.

### Import Errors

**Problem**: `ModuleNotFoundError`

**Solution**: Ensure you're in the virtual environment:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Token Limit Errors

**Problem**: Task exceeds context limit

**Solution**: The system should auto-route to Gemini's large context. If not:
1. Check context routing thresholds in `config/settings.yaml`
2. Split very large files into smaller chunks
3. Use `--file` multiple times instead of wildcards

## Next Steps

- Read [DEVELOPMENT.md](DEVELOPMENT.md) for architecture details
- Check [GitHub Issues](https://github.com/crogers2287/agentflow-orchestrator/issues) for planned features
- Try the example use cases in the documentation
- Join discussions to share your experience

## Getting Help

- 📖 [Documentation](README.md)
- 🐛 [Report Issues](https://github.com/crogers2287/agentflow-orchestrator/issues)
- 💬 [Discussions](https://github.com/crogers2287/agentflow-orchestrator/discussions)

## Common Configuration

### Disable Verification (faster, less accurate)

```yaml
verification:
  enabled: false
```

### Adjust Context Thresholds

```yaml
context_routing:
  small_threshold: 4000    # Lower = use Gemini more
  medium_threshold: 50000  # Adjust based on your needs
```

### Enable Debug Logging

```bash
python main.py run --task "your task" --debug
```

Or in config:
```yaml
logging:
  level: "DEBUG"
```

## Performance Tips

1. **Use smaller contexts when possible** - More efficient and faster
2. **Enable caching** - Reuses large context loads
3. **Monitor token usage** - Check costs with each run
4. **Use appropriate routing** - Don't force small tasks through Gemini

## Security Notes

- Never commit `config/settings.yaml` with API keys
- Use environment variables for production:
  ```bash
  export GEMINI_API_KEY="your-key"
  ```
- Review generated code before executing
- Be cautious with file permissions when processing entire codebases
