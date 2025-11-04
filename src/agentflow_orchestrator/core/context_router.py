"""
Context Router - Analyzes task requirements and routes appropriately
"""

from enum import Enum
from typing import Dict, Optional, Tuple
import tiktoken
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)


class ContextSize(str, Enum):
    """Context size categories for routing decisions"""
    SMALL = "small"       # < 8K tokens: AgentFlow primary, Gemini verifies
    MEDIUM = "medium"     # 8K-100K: AgentFlow coordinates, Gemini assists
    LARGE = "large"       # > 100K: AgentFlow orchestrates, Gemini heavy lifting


class RoutingMode(str, Enum):
    """Routing modes for task processing"""
    AGENTFLOW_PRIMARY = "agentflow_primary"      # AgentFlow builds, Gemini verifies
    COLLABORATIVE_MEDIUM = "collaborative_medium" # AgentFlow coordinates, Gemini provides context
    GEMINI_HEAVY_LIFTING = "gemini_heavy_lifting" # AgentFlow orchestrates, Gemini processes


class ContextAnalysis(BaseModel):
    """Result of context analysis"""
    token_count: int
    context_size: ContextSize
    routing_mode: RoutingMode
    estimated_cost: float
    recommendations: list[str]
    should_split: bool = False
    split_strategy: Optional[str] = None


class ContextRouter:
    """
    Analyzes task requirements and routes to appropriate processing mode.

    Key principle: AgentFlow ALWAYS stays in the loop - routing determines
    who does what, not who gets excluded.
    """

    def __init__(self, config: Dict):
        """
        Initialize the context router

        Args:
            config: Configuration dictionary with thresholds and settings
        """
        self.config = config
        self.small_threshold = config.get("context_routing", {}).get("small_threshold", 8000)
        self.medium_threshold = config.get("context_routing", {}).get("medium_threshold", 100000)

        # Initialize tokenizer (using cl100k_base for GPT-4 compatibility)
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Failed to load tiktoken encoding, using approximate counting: {e}")
            self.tokenizer = None

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in the given text

        Args:
            text: Text to count tokens for

        Returns:
            Token count
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback: rough approximation (1 token ≈ 4 characters)
            return len(text) // 4

    def analyze_context(
        self,
        task: str,
        additional_context: Optional[str] = None,
        attachments: Optional[list[str]] = None
    ) -> ContextAnalysis:
        """
        Analyze the task and determine routing strategy

        Args:
            task: The main task description
            additional_context: Any additional context provided
            attachments: List of file contents or large context data

        Returns:
            ContextAnalysis with routing recommendations
        """
        # Count tokens for all input
        task_tokens = self.count_tokens(task)
        context_tokens = self.count_tokens(additional_context) if additional_context else 0
        attachment_tokens = sum(self.count_tokens(a) for a in attachments) if attachments else 0

        total_tokens = task_tokens + context_tokens + attachment_tokens

        logger.info(
            "context_analysis",
            task_tokens=task_tokens,
            context_tokens=context_tokens,
            attachment_tokens=attachment_tokens,
            total_tokens=total_tokens
        )

        # Determine context size and routing mode
        if total_tokens < self.small_threshold:
            context_size = ContextSize.SMALL
            routing_mode = RoutingMode.AGENTFLOW_PRIMARY
            recommendations = [
                "AgentFlow will handle primary processing",
                "Gemini will verify the solution",
                "Efficient for quick tasks"
            ]
            should_split = False
            split_strategy = None

        elif total_tokens < self.medium_threshold:
            context_size = ContextSize.MEDIUM
            routing_mode = RoutingMode.COLLABORATIVE_MEDIUM
            recommendations = [
                "AgentFlow coordinates the workflow",
                "Gemini assists with context-aware processing",
                "Collaborative approach for complex tasks"
            ]
            should_split = total_tokens > 50000  # Consider splitting very large medium tasks
            split_strategy = "chunk_by_file" if attachments else None

        else:
            context_size = ContextSize.LARGE
            routing_mode = RoutingMode.GEMINI_HEAVY_LIFTING
            recommendations = [
                "AgentFlow orchestrates the overall strategy",
                "Gemini handles heavy lifting with full context",
                "Optimal for codebase analysis, log processing, etc."
            ]
            should_split = total_tokens > 1000000  # Consider splitting extremely large tasks
            split_strategy = "iterative_processing" if should_split else None

        # Estimate cost (rough approximation)
        # Gemini: ~$0.001/1K tokens, AgentFlow: much cheaper
        gemini_usage = total_tokens if routing_mode != RoutingMode.AGENTFLOW_PRIMARY else 0
        estimated_cost = (gemini_usage / 1000) * 0.001

        if routing_mode == RoutingMode.GEMINI_HEAVY_LIFTING:
            recommendations.append(
                f"⚠️  Large context detected ({total_tokens:,} tokens). "
                f"Estimated cost: ${estimated_cost:.4f}"
            )

        return ContextAnalysis(
            token_count=total_tokens,
            context_size=context_size,
            routing_mode=routing_mode,
            estimated_cost=estimated_cost,
            recommendations=recommendations,
            should_split=should_split,
            split_strategy=split_strategy
        )

    def should_use_gemini_primary(self, analysis: ContextAnalysis) -> bool:
        """
        Determine if Gemini should be the primary processor

        Args:
            analysis: Context analysis result

        Returns:
            True if Gemini should handle primary processing
        """
        return analysis.routing_mode in [
            RoutingMode.COLLABORATIVE_MEDIUM,
            RoutingMode.GEMINI_HEAVY_LIFTING
        ]

    def should_verify_with_gemini(self, analysis: ContextAnalysis) -> bool:
        """
        Determine if Gemini should verify the solution

        Args:
            analysis: Context analysis result

        Returns:
            True if Gemini should verify (always true unless disabled in config)
        """
        return self.config.get("verification", {}).get("enabled", True)

    def get_processing_strategy(self, analysis: ContextAnalysis) -> Dict:
        """
        Get detailed processing strategy based on analysis

        Args:
            analysis: Context analysis result

        Returns:
            Dictionary with processing strategy details
        """
        strategy = {
            "routing_mode": analysis.routing_mode.value,
            "context_size": analysis.context_size.value,
            "token_count": analysis.token_count,
            "agentflow_role": "",
            "gemini_role": "",
            "workflow_steps": []
        }

        if analysis.routing_mode == RoutingMode.AGENTFLOW_PRIMARY:
            strategy["agentflow_role"] = "Primary processor - builds solution"
            strategy["gemini_role"] = "Verifier - reviews and critiques"
            strategy["workflow_steps"] = [
                "1. AgentFlow analyzes task",
                "2. AgentFlow proposes solution",
                "3. Gemini reviews solution",
                "4. Iterate if issues found",
                "5. Finalize solution"
            ]

        elif analysis.routing_mode == RoutingMode.COLLABORATIVE_MEDIUM:
            strategy["agentflow_role"] = "Coordinator - manages workflow"
            strategy["gemini_role"] = "Context provider - handles larger context"
            strategy["workflow_steps"] = [
                "1. AgentFlow breaks down task",
                "2. Gemini loads and analyzes full context",
                "3. AgentFlow coordinates implementation",
                "4. Gemini verifies with context awareness",
                "5. Iterate and refine",
                "6. AgentFlow finalizes"
            ]

        else:  # GEMINI_HEAVY_LIFTING
            strategy["agentflow_role"] = "Orchestrator - strategic direction"
            strategy["gemini_role"] = "Heavy lifter - processes large context"
            strategy["workflow_steps"] = [
                "1. AgentFlow analyzes requirements",
                "2. AgentFlow formulates strategy",
                "3. Gemini loads entire context",
                "4. Gemini performs comprehensive analysis",
                "5. AgentFlow reviews findings",
                "6. AgentFlow directs refinements",
                "7. Iterate until complete",
                "8. AgentFlow synthesizes final result"
            ]

        if analysis.should_split:
            strategy["workflow_steps"].insert(
                0,
                f"0. Split task using strategy: {analysis.split_strategy}"
            )

        return strategy
