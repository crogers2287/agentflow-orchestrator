"""
Orchestrator - Main workflow manager for AgentFlow + Gemini collaboration

This is the brain of the system, managing the collaboration between
AgentFlow and Gemini based on context size and task requirements.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import yaml
import structlog
from pydantic import BaseModel
from pathlib import Path

from ..clients.agentflow_client import AgentFlowClient, AgentFlowResponse
from ..clients.gemini_client import GeminiClient, GeminiResponse
from .context_router import ContextRouter, ContextAnalysis, RoutingMode

logger = structlog.get_logger(__name__)


class WorkflowStage(str, Enum):
    """Stages of the workflow"""
    INIT = "init"
    ANALYSIS = "analysis"
    ROUTING = "routing"
    AGENTFLOW_PROCESSING = "agentflow_processing"
    GEMINI_PROCESSING = "gemini_processing"
    VERIFICATION = "verification"
    DEBATE = "debate"
    SYNTHESIS = "synthesis"
    COMPLETE = "complete"
    ERROR = "error"


class AgentDecision(BaseModel):
    """Decision made by an agent"""
    agent: str  # "agentflow" or "gemini"
    decision: str
    reasoning: str
    confidence: float  # 0.0 to 1.0


class WorkflowState(BaseModel):
    """Current state of the workflow"""
    stage: WorkflowStage
    task: str
    context_analysis: Optional[Dict] = None
    agentflow_solution: Optional[str] = None
    gemini_critique: Optional[str] = None
    gemini_analysis: Optional[str] = None
    debate_history: List[Dict] = []
    final_solution: Optional[str] = None
    decisions: List[AgentDecision] = []
    iteration_count: int = 0
    token_usage: Dict = {}


class Orchestrator:
    """
    Main orchestrator managing collaboration between AgentFlow and Gemini

    Key Principle: AgentFlow is ALWAYS the orchestrator, regardless of context size.
    """

    def __init__(self, config_path: str = "config/settings.yaml"):
        """
        Initialize the orchestrator

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = self._load_config(config_path)

        # Load prompts
        self.prompts = self._load_prompts("config/prompts.yaml")

        # Initialize components
        self.context_router = ContextRouter(self.config)
        self.agentflow = AgentFlowClient(self.config)
        self.gemini = GeminiClient(self.config)

        # Settings
        self.max_iterations = self.config.get("verification", {}).get("max_iterations", 3)
        self.debate_rounds = self.config.get("verification", {}).get("debate_rounds", 3)
        self.enable_verification = self.config.get("verification", {}).get("enabled", True)

        logger.info(
            "orchestrator_initialized",
            max_iterations=self.max_iterations,
            debate_rounds=self.debate_rounds,
            verification_enabled=self.enable_verification
        )

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}

    def _load_prompts(self, prompts_path: str) -> Dict:
        """Load prompt templates from YAML file"""
        try:
            with open(prompts_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"Prompts file not found: {prompts_path}, using defaults")
            return {}

    async def process_task(
        self,
        task: str,
        additional_context: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> WorkflowState:
        """
        Main entry point: Process a task through the collaborative workflow

        Args:
            task: The task description
            additional_context: Optional additional context
            attachments: Optional list of file contents or large context

        Returns:
            WorkflowState with final solution and workflow history
        """
        logger.info("task_processing_started", task_length=len(task))

        # Initialize workflow state
        state = WorkflowState(
            stage=WorkflowStage.INIT,
            task=task
        )

        try:
            # Stage 1: Analyze context and route
            state.stage = WorkflowStage.ANALYSIS
            context_analysis = self.context_router.analyze_context(
                task, additional_context, attachments
            )
            state.context_analysis = context_analysis.model_dump()

            logger.info(
                "context_analyzed",
                token_count=context_analysis.token_count,
                routing_mode=context_analysis.routing_mode.value
            )

            # Stage 2: Route to appropriate workflow
            state.stage = WorkflowStage.ROUTING
            if context_analysis.routing_mode == RoutingMode.AGENTFLOW_PRIMARY:
                state = await self._workflow_small_context(state, task, additional_context)

            elif context_analysis.routing_mode == RoutingMode.COLLABORATIVE_MEDIUM:
                state = await self._workflow_medium_context(state, task, additional_context, attachments)

            else:  # GEMINI_HEAVY_LIFTING
                state = await self._workflow_large_context(state, task, additional_context, attachments)

            state.stage = WorkflowStage.COMPLETE
            logger.info("task_processing_complete", iterations=state.iteration_count)

        except Exception as e:
            state.stage = WorkflowStage.ERROR
            logger.error("task_processing_error", error=str(e))
            raise

        return state

    async def _workflow_small_context(
        self,
        state: WorkflowState,
        task: str,
        context: Optional[str]
    ) -> WorkflowState:
        """
        Workflow for small context tasks (< 8K tokens)
        AgentFlow builds solution, Gemini verifies
        """
        logger.info("starting_small_context_workflow")

        # AgentFlow proposes solution
        state.stage = WorkflowStage.AGENTFLOW_PROCESSING
        system_prompt = self.prompts.get("agentflow", {}).get("system_prompt", "")

        af_response = await self.agentflow.propose_solution(
            task, system_prompt, context
        )
        state.agentflow_solution = af_response.content
        state.token_usage["agentflow_initial"] = af_response.token_count

        logger.info("agentflow_solution_generated", length=len(af_response.content))

        # Gemini verification (if enabled)
        if self.enable_verification:
            state = await self._verify_with_gemini(state, task)

        return state

    async def _workflow_medium_context(
        self,
        state: WorkflowState,
        task: str,
        context: Optional[str],
        attachments: Optional[List[str]]
    ) -> WorkflowState:
        """
        Workflow for medium context tasks (8K-100K tokens)
        AgentFlow coordinates, Gemini assists with context
        """
        logger.info("starting_medium_context_workflow")

        # AgentFlow coordinates and creates strategy
        state.stage = WorkflowStage.AGENTFLOW_PROCESSING
        system_prompt = self.prompts.get("agentflow", {}).get("system_prompt", "")

        coordination = await self.agentflow.coordinate_task(
            task,
            state.context_analysis,
            system_prompt
        )

        logger.info("agentflow_coordination_complete", length=len(coordination.content))

        # Gemini processes with full context
        state.stage = WorkflowStage.GEMINI_PROCESSING
        gemini_system = self.prompts.get("gemini_heavy_lifting", {}).get("system_prompt", "")

        # Combine all context
        full_context = "\n\n".join(filter(None, [context] + (attachments or [])))

        gemini_analysis = await self.gemini.analyze_large_context(
            task,
            full_context,
            "Medium-size project context",
            self.prompts.get("gemini_heavy_lifting", {}).get("codebase_analysis_prompt", "{task}"),
            state.context_analysis["token_count"]
        )
        state.gemini_analysis = gemini_analysis.content
        state.token_usage["gemini_analysis"] = gemini_analysis.token_count

        logger.info("gemini_analysis_complete", length=len(gemini_analysis.content))

        # AgentFlow synthesizes results
        state.stage = WorkflowStage.SYNTHESIS
        synthesis = await self.agentflow.synthesize_results(
            task,
            gemini_analysis.content,
            system_prompt
        )
        state.final_solution = synthesis.content
        state.token_usage["agentflow_synthesis"] = synthesis.token_count

        return state

    async def _workflow_large_context(
        self,
        state: WorkflowState,
        task: str,
        context: Optional[str],
        attachments: Optional[List[str]]
    ) -> WorkflowState:
        """
        Workflow for large context tasks (> 100K tokens)
        AgentFlow orchestrates, Gemini does heavy lifting
        """
        logger.info("starting_large_context_workflow")

        # AgentFlow orchestrates strategy
        state.stage = WorkflowStage.AGENTFLOW_PROCESSING
        system_prompt = self.prompts.get("agentflow", {}).get("system_prompt", "")

        coordination = await self.agentflow.coordinate_task(
            task,
            state.context_analysis,
            system_prompt
        )

        logger.info("agentflow_orchestration_complete", length=len(coordination.content))

        # Gemini processes massive context
        state.stage = WorkflowStage.GEMINI_PROCESSING
        gemini_system = self.prompts.get("gemini_heavy_lifting", {}).get("system_prompt", "")

        # Combine all context
        full_context = "\n\n".join(filter(None, [context] + (attachments or [])))

        # Use streaming for very large responses
        if state.context_analysis["token_count"] > 500000:
            logger.info("using_streaming_for_large_context")
            chunks = []
            async for chunk in self.gemini.stream_large_analysis(
                task,
                full_context,
                "Large codebase or document set",
                self.prompts.get("gemini_heavy_lifting", {}).get("codebase_analysis_prompt", "{task}")
            ):
                chunks.append(chunk)
            state.gemini_analysis = "".join(chunks)
        else:
            gemini_analysis = await self.gemini.analyze_large_context(
                task,
                full_context,
                "Large codebase or document set",
                self.prompts.get("gemini_heavy_lifting", {}).get("codebase_analysis_prompt", "{task}"),
                state.context_analysis["token_count"]
            )
            state.gemini_analysis = gemini_analysis.content
            state.token_usage["gemini_heavy_lifting"] = gemini_analysis.token_count

        logger.info("gemini_heavy_lifting_complete", length=len(state.gemini_analysis))

        # AgentFlow synthesizes and validates
        state.stage = WorkflowStage.SYNTHESIS
        synthesis = await self.agentflow.synthesize_results(
            task,
            state.gemini_analysis,
            system_prompt
        )
        state.final_solution = synthesis.content
        state.token_usage["agentflow_synthesis"] = synthesis.token_count

        logger.info("synthesis_complete", length=len(synthesis.content))

        return state

    async def _verify_with_gemini(
        self,
        state: WorkflowState,
        task: str
    ) -> WorkflowState:
        """
        Gemini verifies AgentFlow's solution

        Args:
            state: Current workflow state
            task: Original task

        Returns:
            Updated workflow state
        """
        state.stage = WorkflowStage.VERIFICATION

        review_template = self.prompts.get("gemini_verification", {}).get("review_prompt", "{task}\n{solution}")

        gemini_review = await self.gemini.review_solution(
            task,
            state.agentflow_solution,
            review_template
        )
        state.gemini_critique = gemini_review.content
        state.token_usage["gemini_verification"] = gemini_review.token_count

        logger.info("gemini_verification_complete", length=len(gemini_review.content))

        # Check if refinement is needed
        if self._needs_refinement(gemini_review.content):
            state = await self._refinement_loop(state, task)

        return state

    def _needs_refinement(self, critique: str) -> bool:
        """
        Determine if solution needs refinement based on critique

        Args:
            critique: Gemini's critique

        Returns:
            True if refinement needed
        """
        # Simple heuristic: check for keywords indicating issues
        issue_keywords = [
            "issue", "problem", "error", "vulnerability", "bug",
            "incorrect", "missing", "needs revision", "major concerns"
        ]
        critique_lower = critique.lower()
        return any(keyword in critique_lower for keyword in issue_keywords)

    async def _refinement_loop(
        self,
        state: WorkflowState,
        task: str
    ) -> WorkflowState:
        """
        Iterative refinement loop when issues are found

        Args:
            state: Current workflow state
            task: Original task

        Returns:
            Updated workflow state
        """
        logger.info("starting_refinement_loop")

        system_prompt = self.prompts.get("agentflow", {}).get("system_prompt", "")
        refinement_template = self.prompts.get("agentflow", {}).get("refinement_prompt", "")

        for iteration in range(self.max_iterations):
            state.iteration_count = iteration + 1

            logger.info("refinement_iteration", iteration=state.iteration_count)

            # AgentFlow responds to critique
            af_refinement = await self.agentflow.refine_solution(
                task,
                state.agentflow_solution,
                state.gemini_critique,
                system_prompt,
                refinement_template
            )

            # Check if AgentFlow is defending or refining
            if "defend" in af_refinement.content.lower()[:200]:
                # AgentFlow is defending - enter debate mode
                logger.info("agentflow_defending_solution")
                state = await self._debate_mode(state, task)
                break
            else:
                # AgentFlow refined the solution
                state.agentflow_solution = af_refinement.content
                logger.info("agentflow_refined_solution", length=len(af_refinement.content))

                # Gemini re-verifies
                review_template = self.prompts.get("gemini_verification", {}).get("review_prompt", "")
                gemini_review = await self.gemini.review_solution(
                    task,
                    state.agentflow_solution,
                    review_template
                )
                state.gemini_critique = gemini_review.content

                # Check if issues resolved
                if not self._needs_refinement(gemini_review.content):
                    logger.info("refinement_successful")
                    state.final_solution = state.agentflow_solution
                    break

        return state

    async def _debate_mode(
        self,
        state: WorkflowState,
        task: str
    ) -> WorkflowState:
        """
        Structured debate when agents disagree

        Args:
            state: Current workflow state
            task: Original task

        Returns:
            Updated workflow state
        """
        logger.info("entering_debate_mode")
        state.stage = WorkflowStage.DEBATE

        system_prompt = self.prompts.get("agentflow", {}).get("system_prompt", "")
        debate_template = self.prompts.get("debate", {}).get("initial_position_prompt", "")

        for round_num in range(self.debate_rounds):
            logger.info("debate_round", round_num=round_num + 1)

            # Both agents state positions
            af_position = await self.agentflow.debate_position(
                task,
                state.agentflow_solution,
                state.gemini_critique,
                system_prompt,
                debate_template
            )

            # For now, accept AgentFlow's final position
            # In a full implementation, you'd have more sophisticated
            # consensus detection and hybrid solution generation

            state.debate_history.append({
                "round": round_num + 1,
                "agentflow": af_position.content
            })

        # After debate, finalize with AgentFlow's solution
        state.final_solution = state.agentflow_solution

        logger.info("debate_complete", rounds=len(state.debate_history))

        return state

    async def health_check(self) -> Dict:
        """
        Check health of all components

        Returns:
            Dictionary with health status
        """
        agentflow_healthy = await self.agentflow.check_health()

        return {
            "orchestrator": "healthy",
            "agentflow": "healthy" if agentflow_healthy else "unhealthy",
            "gemini": "configured",
            "context_router": "healthy"
        }

    async def get_status(self) -> Dict:
        """
        Get current status and model information

        Returns:
            Dictionary with status information
        """
        return {
            "agentflow_info": self.agentflow.get_model_info(),
            "gemini_info": self.gemini.get_model_info(),
            "config": {
                "max_iterations": self.max_iterations,
                "debate_rounds": self.debate_rounds,
                "verification_enabled": self.enable_verification
            }
        }

    async def cleanup(self):
        """Cleanup resources"""
        await self.agentflow.close()
