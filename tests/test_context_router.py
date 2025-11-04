"""
Tests for ContextRouter
"""

import pytest
from src.agentflow_orchestrator.core.context_router import (
    ContextRouter,
    ContextSize,
    RoutingMode
)


@pytest.fixture
def router():
    """Create a context router with default config"""
    config = {
        "context_routing": {
            "small_threshold": 8000,
            "medium_threshold": 100000
        }
    }
    return ContextRouter(config)


def test_small_context_routing(router):
    """Test routing for small context tasks"""
    task = "Write a simple hello world function"
    analysis = router.analyze_context(task)

    assert analysis.context_size == ContextSize.SMALL
    assert analysis.routing_mode == RoutingMode.AGENTFLOW_PRIMARY
    assert analysis.token_count < 8000


def test_medium_context_routing(router):
    """Test routing for medium context tasks"""
    task = "Refactor this code" * 1000  # Create medium-sized task
    analysis = router.analyze_context(task)

    assert analysis.context_size in [ContextSize.SMALL, ContextSize.MEDIUM]


def test_large_context_routing(router):
    """Test routing for large context tasks"""
    task = "Analyze this codebase"
    large_context = "def function():\n    pass\n" * 10000  # Large codebase
    attachments = [large_context]

    analysis = router.analyze_context(task, attachments=attachments)

    assert analysis.context_size == ContextSize.LARGE
    assert analysis.routing_mode == RoutingMode.GEMINI_HEAVY_LIFTING


def test_token_counting(router):
    """Test token counting"""
    text = "Hello world"
    tokens = router.count_tokens(text)

    assert tokens > 0
    assert isinstance(tokens, int)


def test_processing_strategy(router):
    """Test getting processing strategy"""
    task = "Simple task"
    analysis = router.analyze_context(task)
    strategy = router.get_processing_strategy(analysis)

    assert "routing_mode" in strategy
    assert "agentflow_role" in strategy
    assert "gemini_role" in strategy
    assert "workflow_steps" in strategy
    assert len(strategy["workflow_steps"]) > 0
