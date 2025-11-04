"""
AgentFlow Client - vLLM integration with agentflow-planner-7b model

This client interfaces with a vLLM server running the AgentFlow/agentflow-planner-7b model.
AgentFlow is designed for efficient reasoning and planning tasks.
"""

from typing import Dict, List, Optional
import httpx
import structlog
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger(__name__)


class AgentFlowResponse(BaseModel):
    """Response from AgentFlow"""
    content: str
    finish_reason: str
    token_count: Optional[int] = None
    model_used: str


class AgentFlowClient:
    """
    Client for interacting with AgentFlow via vLLM

    AgentFlow serves as the primary orchestrator and coordinator,
    handling task decomposition, planning, and decision-making.
    """

    def __init__(self, config: Dict):
        """
        Initialize AgentFlow client

        Args:
            config: Configuration dictionary with vLLM settings
        """
        self.config = config
        self.model_config = config.get("models", {}).get("agentflow", {})

        # vLLM connection settings
        self.vllm_host = self.model_config.get("vllm_host", "localhost")
        self.vllm_port = self.model_config.get("vllm_port", 8000)
        self.base_url = f"http://{self.vllm_host}:{self.vllm_port}/v1"

        # Model settings
        self.model_name = self.model_config.get("model_name", "AgentFlow/agentflow-planner-7b")
        self.temperature = self.model_config.get("temperature", 0.7)
        self.max_tokens = self.model_config.get("max_tokens", 2048)
        self.context_limit = self.model_config.get("context_limit", 8000)

        # HTTP client with timeout
        self.http_client = httpx.AsyncClient(timeout=60.0)

        logger.info(
            "agentflow_client_initialized",
            vllm_host=self.vllm_host,
            vllm_port=self.vllm_port,
            model=self.model_name,
            context_limit=self.context_limit
        )

    async def check_health(self) -> bool:
        """
        Check if vLLM server is healthy

        Returns:
            True if server is accessible
        """
        try:
            response = await self.http_client.get(f"http://{self.vllm_host}:{self.vllm_port}/health")
            return response.status_code == 200
        except Exception as e:
            logger.error("agentflow_health_check_failed", error=str(e))
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AgentFlowResponse:
        """
        Generate a response from AgentFlow

        Args:
            prompt: The user prompt
            system_prompt: Optional system instruction
            temperature: Optional temperature override
            max_tokens: Optional max tokens override

        Returns:
            AgentFlowResponse with generated content
        """
        try:
            # Build messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Build request payload
            payload = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                "max_tokens": max_tokens if max_tokens is not None else self.max_tokens,
            }

            # Make request to vLLM
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()

            result = response.json()

            # Extract content
            content = result["choices"][0]["message"]["content"]
            finish_reason = result["choices"][0].get("finish_reason", "stop")

            # Extract token usage
            token_count = None
            if "usage" in result:
                token_count = result["usage"].get("total_tokens")

            logger.info(
                "agentflow_generate_success",
                prompt_length=len(prompt),
                response_length=len(content),
                token_count=token_count,
                finish_reason=finish_reason
            )

            return AgentFlowResponse(
                content=content,
                finish_reason=finish_reason,
                token_count=token_count,
                model_used=self.model_name
            )

        except httpx.HTTPStatusError as e:
            logger.error(
                "agentflow_http_error",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise
        except Exception as e:
            logger.error("agentflow_generate_error", error=str(e))
            raise

    # Task Analysis and Planning

    async def analyze_task(
        self,
        task: str,
        system_prompt: str,
        analysis_prompt_template: str
    ) -> AgentFlowResponse:
        """
        Analyze a task and provide initial assessment

        Args:
            task: The task to analyze
            system_prompt: System instruction for AgentFlow
            analysis_prompt_template: Template for analysis prompt

        Returns:
            AgentFlowResponse with task analysis
        """
        prompt = analysis_prompt_template.format(task=task)

        logger.info("agentflow_analyzing_task", task_length=len(task))

        return await self.generate(prompt, system_prompt=system_prompt)

    async def propose_solution(
        self,
        task: str,
        system_prompt: str,
        context: Optional[str] = None
    ) -> AgentFlowResponse:
        """
        Propose a solution for a task (primary processor mode)

        Args:
            task: The task to solve
            system_prompt: System instruction
            context: Optional additional context

        Returns:
            AgentFlowResponse with proposed solution
        """
        if context:
            prompt = f"Task: {task}\n\nContext:\n{context}\n\nProvide a complete solution:"
        else:
            prompt = f"Task: {task}\n\nProvide a complete solution:"

        logger.info("agentflow_proposing_solution", task_length=len(task))

        return await self.generate(prompt, system_prompt=system_prompt)

    # Refinement and Response to Critique

    async def refine_solution(
        self,
        task: str,
        original_solution: str,
        critique: str,
        system_prompt: str,
        refinement_prompt_template: str
    ) -> AgentFlowResponse:
        """
        Refine solution based on Gemini's critique

        Args:
            task: Original task
            original_solution: AgentFlow's original solution
            critique: Gemini's critique
            system_prompt: System instruction
            refinement_prompt_template: Template for refinement prompt

        Returns:
            AgentFlowResponse with refined solution or defense
        """
        prompt = refinement_prompt_template.format(
            original_solution=original_solution,
            critique=critique
        )

        logger.info(
            "agentflow_refining_solution",
            original_length=len(original_solution),
            critique_length=len(critique)
        )

        return await self.generate(prompt, system_prompt=system_prompt)

    # Coordination Mode (for medium/large context tasks)

    async def coordinate_task(
        self,
        task: str,
        context_analysis: Dict,
        system_prompt: str
    ) -> AgentFlowResponse:
        """
        Coordinate a medium/large context task

        In this mode, AgentFlow breaks down the task and coordinates
        with Gemini who handles the heavy lifting.

        Args:
            task: The task to coordinate
            context_analysis: Analysis from context router
            system_prompt: System instruction

        Returns:
            AgentFlowResponse with coordination strategy
        """
        prompt = f"""Task: {task}

Context Analysis:
- Token count: {context_analysis['token_count']:,}
- Context size: {context_analysis['context_size']}
- Routing mode: {context_analysis['routing_mode']}

As the orchestrator, provide:
1. Task breakdown strategy
2. What information Gemini should extract from the large context
3. How to synthesize the results
4. Implementation plan
"""

        logger.info(
            "agentflow_coordinating_task",
            token_count=context_analysis['token_count'],
            routing_mode=context_analysis['routing_mode']
        )

        return await self.generate(prompt, system_prompt=system_prompt)

    async def synthesize_results(
        self,
        task: str,
        gemini_findings: str,
        system_prompt: str
    ) -> AgentFlowResponse:
        """
        Synthesize results from Gemini's large-context analysis

        Args:
            task: Original task
            gemini_findings: Findings from Gemini
            system_prompt: System instruction

        Returns:
            AgentFlowResponse with synthesis and next steps
        """
        prompt = f"""Task: {task}

Gemini has analyzed the large context and provided these findings:

{gemini_findings}

As the orchestrator, synthesize these findings and provide:
1. Summary of key points
2. Gaps or areas needing clarification
3. Next steps or actions
4. Final recommendations
"""

        logger.info(
            "agentflow_synthesizing_results",
            findings_length=len(gemini_findings)
        )

        return await self.generate(prompt, system_prompt=system_prompt)

    # Debate and Discussion

    async def debate_position(
        self,
        task: str,
        your_solution: str,
        gemini_solution: str,
        system_prompt: str,
        debate_prompt_template: str
    ) -> AgentFlowResponse:
        """
        State position in debate with Gemini

        Args:
            task: Original task
            your_solution: AgentFlow's solution
            gemini_solution: Gemini's alternative
            system_prompt: System instruction
            debate_prompt_template: Template for debate

        Returns:
            AgentFlowResponse with argumentation
        """
        prompt = debate_prompt_template.format(
            task=task,
            your_solution=your_solution,
            other_solution=gemini_solution
        )

        logger.info("agentflow_debate_position")

        return await self.generate(prompt, system_prompt=system_prompt)

    async def counter_argument(
        self,
        disagreement: str,
        gemini_argument: str,
        system_prompt: str,
        counter_prompt_template: str
    ) -> AgentFlowResponse:
        """
        Provide counter-argument in debate

        Args:
            disagreement: Core disagreement
            gemini_argument: Gemini's argument
            system_prompt: System instruction
            counter_prompt_template: Template for counter-argument

        Returns:
            AgentFlowResponse with counter-argument
        """
        prompt = counter_prompt_template.format(
            disagreement=disagreement,
            argument=gemini_argument
        )

        logger.info("agentflow_counter_argument")

        return await self.generate(prompt, system_prompt=system_prompt)

    def get_context_limit(self) -> int:
        """Get the context window size"""
        return self.context_limit

    def get_model_info(self) -> Dict:
        """Get information about the model"""
        return {
            "model_name": self.model_name,
            "context_limit": self.context_limit,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "vllm_endpoint": f"{self.vllm_host}:{self.vllm_port}"
        }

    async def close(self):
        """Close the HTTP client"""
        await self.http_client.aclose()
