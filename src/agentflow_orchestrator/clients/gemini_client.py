"""
Gemini Client - Google AI API integration with 2M token context window
"""

import os
from typing import Dict, List, Optional, AsyncGenerator
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import structlog
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

logger = structlog.get_logger(__name__)


class GeminiResponse(BaseModel):
    """Response from Gemini"""
    content: str
    token_count: int
    finish_reason: str
    safety_ratings: Optional[Dict] = None
    model_used: str


class GeminiClient:
    """
    Client for interacting with Gemini 2.5 Pro with 2M token context window

    Handles both verification mode (reviewing AgentFlow solutions) and
    heavy lifting mode (processing large contexts under AgentFlow coordination)
    """

    def __init__(self, config: Dict):
        """
        Initialize Gemini client

        Args:
            config: Configuration dictionary with API keys and model settings
        """
        self.config = config
        self.model_config = config.get("models", {}).get("gemini", {})

        # Get API key from config or environment
        api_key = config.get("api_keys", {}).get("gemini_api_key") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key not found in config or environment")

        # Configure the API
        genai.configure(api_key=api_key)

        # Initialize the model
        self.model_name = self.model_config.get("model_name", "gemini-2.5-pro")
        self.temperature = self.model_config.get("temperature", 0.7)
        self.max_tokens = self.model_config.get("max_tokens", 8192)

        # Safety settings - be permissive for code analysis
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

        # Generation config
        self.generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }

        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            safety_settings=self.safety_settings,
            generation_config=self.generation_config
        )

        logger.info(
            "gemini_client_initialized",
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> GeminiResponse:
        """
        Generate a response from Gemini

        Args:
            prompt: The user prompt
            system_instruction: Optional system instruction
            temperature: Optional temperature override

        Returns:
            GeminiResponse with the generated content
        """
        try:
            # Override generation config if needed
            gen_config = self.generation_config.copy()
            if temperature is not None:
                gen_config["temperature"] = temperature

            # Create model with system instruction if provided
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    safety_settings=self.safety_settings,
                    generation_config=gen_config,
                    system_instruction=system_instruction
                )
            else:
                model = self.model

            # Generate response
            response = await model.generate_content_async(prompt)

            # Extract content
            content = response.text if hasattr(response, 'text') else str(response)

            # Count tokens (approximate from response metadata)
            token_count = 0
            if hasattr(response, 'usage_metadata'):
                token_count = response.usage_metadata.total_token_count

            # Get safety ratings
            safety_ratings = None
            if hasattr(response, 'safety_ratings'):
                safety_ratings = {
                    rating.category.name: rating.probability.name
                    for rating in response.safety_ratings
                }

            logger.info(
                "gemini_generate_success",
                prompt_length=len(prompt),
                response_length=len(content),
                token_count=token_count
            )

            return GeminiResponse(
                content=content,
                token_count=token_count,
                finish_reason=response.candidates[0].finish_reason.name if response.candidates else "UNKNOWN",
                safety_ratings=safety_ratings,
                model_used=self.model_name
            )

        except Exception as e:
            logger.error("gemini_generate_error", error=str(e), prompt_length=len(prompt))
            raise

    async def stream_generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from Gemini (useful for long responses)

        Args:
            prompt: The user prompt
            system_instruction: Optional system instruction

        Yields:
            Chunks of generated text
        """
        try:
            # Create model with system instruction if provided
            if system_instruction:
                model = genai.GenerativeModel(
                    model_name=self.model_name,
                    safety_settings=self.safety_settings,
                    generation_config=self.generation_config,
                    system_instruction=system_instruction
                )
            else:
                model = self.model

            # Stream response
            response = await model.generate_content_async(prompt, stream=True)

            async for chunk in response:
                if hasattr(chunk, 'text'):
                    yield chunk.text

        except Exception as e:
            logger.error("gemini_stream_error", error=str(e))
            raise

    # Verification Mode Methods

    async def review_solution(
        self,
        task: str,
        solution: str,
        review_prompt_template: str
    ) -> GeminiResponse:
        """
        Review a solution from AgentFlow (verification mode)

        Args:
            task: The original task
            solution: AgentFlow's solution
            review_prompt_template: Template for review prompt

        Returns:
            GeminiResponse with critique and recommendations
        """
        prompt = review_prompt_template.format(
            task=task,
            solution=solution
        )

        logger.info("gemini_reviewing_solution", task_length=len(task), solution_length=len(solution))

        return await self.generate(prompt)

    async def security_audit(
        self,
        task: str,
        solution: str,
        audit_prompt_template: str
    ) -> GeminiResponse:
        """
        Perform security audit on a solution

        Args:
            task: The original task
            solution: Solution to audit
            audit_prompt_template: Template for security audit

        Returns:
            GeminiResponse with security findings
        """
        prompt = audit_prompt_template.format(
            task=task,
            solution=solution
        )

        logger.info("gemini_security_audit", solution_length=len(solution))

        return await self.generate(prompt, temperature=0.3)  # Lower temp for security

    async def performance_review(
        self,
        task: str,
        solution: str,
        performance_prompt_template: str
    ) -> GeminiResponse:
        """
        Analyze performance characteristics of a solution

        Args:
            task: The original task
            solution: Solution to analyze
            performance_prompt_template: Template for performance analysis

        Returns:
            GeminiResponse with performance analysis
        """
        prompt = performance_prompt_template.format(
            task=task,
            solution=solution
        )

        logger.info("gemini_performance_review", solution_length=len(solution))

        return await self.generate(prompt)

    # Heavy Lifting Mode Methods

    async def analyze_large_context(
        self,
        task: str,
        context: str,
        context_description: str,
        analysis_prompt_template: str,
        token_count: Optional[int] = None
    ) -> GeminiResponse:
        """
        Analyze large context (heavy lifting mode)

        This is where Gemini's 2M token context window shines.
        Processes entire codebases, log files, or document sets.

        Args:
            task: The task from AgentFlow coordination
            context: The large context to analyze
            context_description: Description of what the context contains
            analysis_prompt_template: Template for analysis prompt
            token_count: Optional pre-counted token count

        Returns:
            GeminiResponse with comprehensive analysis
        """
        prompt = analysis_prompt_template.format(
            task=task,
            context_description=context_description,
            token_count=token_count or "unknown"
        )

        # Append the large context
        full_prompt = f"{prompt}\n\n=== CONTEXT START ===\n{context}\n=== CONTEXT END ==="

        logger.info(
            "gemini_large_context_analysis",
            task_length=len(task),
            context_length=len(context),
            token_count=token_count
        )

        return await self.generate(full_prompt)

    async def stream_large_analysis(
        self,
        task: str,
        context: str,
        context_description: str,
        analysis_prompt_template: str
    ) -> AsyncGenerator[str, None]:
        """
        Stream analysis of large context (for very long responses)

        Args:
            task: The task from AgentFlow
            context: Large context to analyze
            context_description: Description of context
            analysis_prompt_template: Template for analysis

        Yields:
            Chunks of analysis
        """
        prompt = analysis_prompt_template.format(
            task=task,
            context_description=context_description,
            token_count="streaming"
        )

        full_prompt = f"{prompt}\n\n=== CONTEXT START ===\n{context}\n=== CONTEXT END ==="

        logger.info("gemini_streaming_large_analysis", context_length=len(context))

        async for chunk in self.stream_generate(full_prompt):
            yield chunk

    # Debate and Discussion Methods

    async def debate_position(
        self,
        task: str,
        your_solution: str,
        other_solution: str,
        debate_prompt_template: str
    ) -> GeminiResponse:
        """
        State position in a debate with AgentFlow

        Args:
            task: The original task
            your_solution: Gemini's solution
            other_solution: AgentFlow's solution
            debate_prompt_template: Template for debate prompt

        Returns:
            GeminiResponse with argumentation
        """
        prompt = debate_prompt_template.format(
            task=task,
            your_solution=your_solution,
            other_solution=other_solution
        )

        logger.info("gemini_debate_position")

        return await self.generate(prompt)

    async def counter_argument(
        self,
        disagreement: str,
        argument: str,
        counter_prompt_template: str
    ) -> GeminiResponse:
        """
        Provide counter-argument in debate

        Args:
            disagreement: The core disagreement
            argument: The argument to counter
            counter_prompt_template: Template for counter-argument

        Returns:
            GeminiResponse with counter-argument
        """
        prompt = counter_prompt_template.format(
            disagreement=disagreement,
            argument=argument
        )

        logger.info("gemini_counter_argument")

        return await self.generate(prompt)

    def get_context_limit(self) -> int:
        """Get the context window size for this model"""
        return self.model_config.get("context_limit", 2000000)

    def get_model_info(self) -> Dict:
        """Get information about the current model"""
        return {
            "model_name": self.model_name,
            "context_limit": self.get_context_limit(),
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens
        }
