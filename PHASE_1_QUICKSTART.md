# Phase 1 Quick Start Guide

**Goal**: Get the system running and understand how it works (3-5 days)

## ⚡ Quick Setup (30 minutes)

### 1. Install
```bash
git clone https://github.com/crogers2287/agentflow-orchestrator.git
cd agentflow-orchestrator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure
```bash
cp config/settings.example.yaml config/settings.yaml
# Edit settings.yaml - add your Gemini API key
nano config/settings.yaml
```

### 3. Start vLLM (separate terminal)
```bash
./scripts/start_vllm.sh
# Wait for "Application startup complete"
```

### 4. Test
```bash
python main.py health
python main.py run --task "Write a hello world function"
```

## 📋 Testing Checklist

### Day 1: Basic Setup ✅
- [ ] Clone repo and install dependencies
- [ ] Configure Gemini API key
- [ ] Start vLLM successfully
- [ ] Health check passes

### Day 2: Basic Tests ✅
- [ ] Small context task (< 8K tokens)
- [ ] Medium context task (8K-100K tokens)
- [ ] Verification loop triggers
- [ ] Debug mode works

### Day 3: Code Understanding ✅
- [ ] Read and understand `main.py`
- [ ] Read and understand `orchestrator.py`
- [ ] Read and understand `context_router.py`
- [ ] Read and understand `agentflow_client.py`
- [ ] Read and understand `gemini_client.py`
- [ ] Document your understanding

### Day 4: Advanced Testing ✅
- [ ] Large context (if files available)
- [ ] Debate scenario
- [ ] Interactive mode
- [ ] Edge cases

### Day 5: Configuration ✅
- [ ] Understand all settings
- [ ] Experiment with thresholds
- [ ] Tune verification behavior
- [ ] Customize prompts (optional)

## 🎯 Key Test Commands

### Test 1: Small Context
```bash
python main.py run --task "Write a Python function to reverse a string"
```
**Expected**: AgentFlow primary, Gemini verifies, ~30 seconds

### Test 2: Medium Context
```bash
python main.py run --task "Review this code" --file mycode.py
```
**Expected**: Collaborative mode, 1-2 minutes

### Test 3: Debug Mode
```bash
python main.py run --debug --task "Create a secure password validator"
```
**Expected**: Detailed logs, token counts, agent reasoning

### Test 4: Interactive
```bash
python main.py interactive
```
**Try**: Multiple related tasks in sequence

## 🔍 What to Observe

### Routing Decisions
- **< 8K tokens** → AgentFlow primary, Gemini verifies
- **8K-100K tokens** → Collaborative, AgentFlow coordinates
- **> 100K tokens** → Gemini heavy lifting, AgentFlow orchestrates

### Verification Loop
1. AgentFlow proposes solution
2. Gemini reviews and critiques
3. If issues found → AgentFlow refines
4. Repeat until approved

### Debate Protocol
1. Agents disagree on approach
2. Both state positions
3. Counter-arguments exchanged
4. Synthesis or final decision

## 📚 Code Reading Order

1. **`main.py`** - CLI and user interaction
2. **`orchestrator.py`** - Main workflow logic
3. **`context_router.py`** - Routing decisions
4. **`agentflow_client.py`** - vLLM integration
5. **`gemini_client.py`** - Gemini API usage

## 🎓 Understanding Goals

After Phase 1, you should know:

✅ **How routing works** - Token counting drives all decisions
✅ **Three workflow modes** - Small/Medium/Large context
✅ **Verification process** - How agents collaborate
✅ **Debate mechanics** - When and how agents disagree
✅ **Configuration options** - How to tune behavior
✅ **CLI usage** - All command patterns
✅ **Code structure** - Where everything lives
✅ **Extension points** - Where to add features

## 🚀 Ready for Phase 2?

Complete this checklist:

- [ ] System runs reliably on your machine
- [ ] You understand how all three modes work
- [ ] You've tested verification and debate
- [ ] Configuration is tuned to your preferences
- [ ] You can explain the architecture
- [ ] You have ideas for Phase 2 features

## 💡 Quick Tips

**If vLLM fails to start:**
- Check GPU with `nvidia-smi`
- Try reducing `--max-model-len 4096`
- Use CPU mode if no GPU

**If Gemini errors:**
- Verify API key at https://ai.google.dev/
- Check no extra spaces in config
- Watch rate limits (free tier)

**If routing seems wrong:**
- Check token counts with `--debug`
- Adjust thresholds in `config/settings.yaml`
- Review `context_router.py` logic

**For best results:**
- Start with simple tasks
- Use debug mode to learn
- Read the code alongside testing
- Take notes on how it works

## 📖 Full Documentation

- **[phase-1-revised-setup-testing.md](phase-1-revised-setup-testing.md)** - Complete Phase 1 guide
- **[SETUP.md](SETUP.md)** - Detailed setup instructions
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Architecture and development
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete overview

## 🆘 Getting Help

**Something not working?**
1. Check `logs/` directory for error details
2. Run with `--debug` for verbose output
3. Review [SETUP.md](SETUP.md) troubleshooting section
4. Check GitHub issues for similar problems
5. Create new issue with debug logs

**Ready to move forward?**
- Complete all Phase 1 checklist items
- Document what you learned
- Review Phase 2 plans in GitHub issues
- Start thinking about custom workflows

---

**Time Budget**: 3-5 days
**Priority**: Understanding over speed
**Next**: Phase 2 - Building new features

🎉 **The hard work is done - now learn how it all works!**
