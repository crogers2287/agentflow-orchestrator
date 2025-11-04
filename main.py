#!/usr/bin/env python3
"""
AgentFlow + Gemini Orchestration CLI

Main entry point for the collaborative AI orchestration system.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.markdown import Markdown
from rich import print as rprint

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agentflow_orchestrator.core.orchestrator import Orchestrator, WorkflowStage
from agentflow_orchestrator.utils.logger import setup_logging

console = Console()


def print_header():
    """Print application header"""
    header_text = """
# AgentFlow + Gemini Orchestrator

Intelligent AI collaboration system combining AgentFlow (efficient planning)
with Gemini 2.5 Pro (2M token context) for optimal solutions.

**Principle**: AgentFlow orchestrates, Gemini assists or handles heavy lifting.
"""
    console.print(Panel(Markdown(header_text), border_style="blue"))


def print_context_analysis(analysis: dict):
    """Print context analysis results"""
    table = Table(title="Context Analysis", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Token Count", f"{analysis['token_count']:,}")
    table.add_row("Context Size", analysis['context_size'])
    table.add_row("Routing Mode", analysis['routing_mode'])
    table.add_row("Estimated Cost", f"${analysis['estimated_cost']:.4f}")

    console.print(table)

    if analysis.get('recommendations'):
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in analysis['recommendations']:
            console.print(f"  • {rec}")


def print_workflow_stage(stage: WorkflowStage):
    """Print current workflow stage"""
    stage_icons = {
        WorkflowStage.INIT: "🔧",
        WorkflowStage.ANALYSIS: "🔍",
        WorkflowStage.ROUTING: "🧭",
        WorkflowStage.AGENTFLOW_PROCESSING: "🤖",
        WorkflowStage.GEMINI_PROCESSING: "✨",
        WorkflowStage.VERIFICATION: "🔬",
        WorkflowStage.DEBATE: "💬",
        WorkflowStage.SYNTHESIS: "🎯",
        WorkflowStage.COMPLETE: "✅",
        WorkflowStage.ERROR: "❌"
    }

    icon = stage_icons.get(stage, "⚙️")
    console.print(f"\n{icon} [bold]{stage.value.upper()}[/bold]")


def print_solution(solution: str, title: str = "Solution"):
    """Print solution in a nice format"""
    console.print(Panel(
        Markdown(solution),
        title=title,
        border_style="green"
    ))


def print_token_usage(usage: dict):
    """Print token usage statistics"""
    if not usage:
        return

    table = Table(title="Token Usage", show_header=True, header_style="bold yellow")
    table.add_column("Component", style="cyan")
    table.add_column("Tokens", style="magenta", justify="right")

    total = 0
    for component, tokens in usage.items():
        if tokens:
            table.add_row(component, f"{tokens:,}")
            total += tokens

    table.add_row("[bold]TOTAL[/bold]", f"[bold]{total:,}[/bold]")

    console.print(table)


@click.group()
def cli():
    """AgentFlow + Gemini Orchestration CLI"""
    pass


@cli.command()
@click.option("--task", "-t", required=True, help="Task description")
@click.option("--context", "-c", help="Additional context")
@click.option("--file", "-f", multiple=True, help="Files to include (can specify multiple)")
@click.option("--config", default="config/settings.yaml", help="Config file path")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def run(task: str, context: Optional[str], file: tuple, config: str, debug: bool):
    """Run a task through the orchestration system"""

    # Setup logging
    log_level = "DEBUG" if debug else "INFO"
    setup_logging(log_level=log_level)

    print_header()

    console.print(f"\n[bold cyan]Task:[/bold cyan] {task}\n")

    # Load files if specified
    attachments = []
    if file:
        for file_path in file:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    attachments.append(content)
                    console.print(f"✓ Loaded file: {file_path} ({len(content)} chars)")
            except Exception as e:
                console.print(f"[red]✗ Failed to load {file_path}: {e}[/red]")

    # Run the orchestration
    asyncio.run(_run_task(task, context, attachments, config))


async def _run_task(task: str, context: Optional[str], attachments: list, config_path: str):
    """Async task runner"""

    try:
        # Initialize orchestrator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task(description="Initializing orchestrator...", total=None)
            orchestrator = Orchestrator(config_path)

        # Run task
        console.print("\n[bold]Starting orchestration...[/bold]\n")

        state = await orchestrator.process_task(task, context, attachments)

        # Print context analysis
        if state.context_analysis:
            print_context_analysis(state.context_analysis)

        # Print workflow stages
        console.print("\n[bold]Workflow Progress:[/bold]")
        print_workflow_stage(state.stage)

        # Print solutions and analysis
        if state.agentflow_solution:
            console.print("\n" + "─" * 80)
            print_solution(state.agentflow_solution, "AgentFlow Solution")

        if state.gemini_critique:
            console.print("\n" + "─" * 80)
            print_solution(state.gemini_critique, "Gemini Critique")

        if state.gemini_analysis:
            console.print("\n" + "─" * 80)
            print_solution(state.gemini_analysis, "Gemini Analysis")

        if state.final_solution:
            console.print("\n" + "─" * 80)
            print_solution(state.final_solution, "Final Solution")

        # Print debate history if any
        if state.debate_history:
            console.print("\n[bold]Debate History:[/bold]")
            for debate in state.debate_history:
                console.print(f"\n[yellow]Round {debate['round']}:[/yellow]")
                console.print(debate.get('agentflow', ''))

        # Print token usage
        console.print("\n" + "─" * 80)
        print_token_usage(state.token_usage)

        # Print summary
        console.print("\n" + "=" * 80)
        console.print(f"[bold green]✓ Task completed successfully![/bold green]")
        console.print(f"Iterations: {state.iteration_count}")
        console.print("=" * 80 + "\n")

        # Cleanup
        await orchestrator.cleanup()

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        import traceback
        if "--debug" in sys.argv:
            console.print(traceback.format_exc())
        sys.exit(1)


@cli.command()
@click.option("--config", default="config/settings.yaml", help="Config file path")
def health(config: str):
    """Check health of all components"""
    console.print("[bold]Checking system health...[/bold]\n")

    try:
        orchestrator = Orchestrator(config)
        health_status = asyncio.run(orchestrator.health_check())

        table = Table(title="System Health", show_header=True, header_style="bold magenta")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")

        for component, status in health_status.items():
            icon = "✓" if "healthy" in status.lower() else "?"
            table.add_row(component, f"{icon} {status}")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Health check failed: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.option("--config", default="config/settings.yaml", help="Config file path")
def status(config: str):
    """Show system status and model information"""
    console.print("[bold]System Status[/bold]\n")

    try:
        orchestrator = Orchestrator(config)
        status_info = asyncio.run(orchestrator.get_status())

        # AgentFlow info
        console.print("[bold cyan]AgentFlow:[/bold cyan]")
        af_info = status_info["agentflow_info"]
        console.print(f"  Model: {af_info['model_name']}")
        console.print(f"  Context Limit: {af_info['context_limit']:,} tokens")
        console.print(f"  Endpoint: {af_info['vllm_endpoint']}")

        # Gemini info
        console.print("\n[bold cyan]Gemini:[/bold cyan]")
        gem_info = status_info["gemini_info"]
        console.print(f"  Model: {gem_info['model_name']}")
        console.print(f"  Context Limit: {gem_info['context_limit']:,} tokens")

        # Config
        console.print("\n[bold cyan]Configuration:[/bold cyan]")
        config_info = status_info["config"]
        console.print(f"  Max Iterations: {config_info['max_iterations']}")
        console.print(f"  Debate Rounds: {config_info['debate_rounds']}")
        console.print(f"  Verification: {'Enabled' if config_info['verification_enabled'] else 'Disabled'}")

    except Exception as e:
        console.print(f"[red]Failed to get status: {e}[/red]")
        sys.exit(1)


@cli.command()
def interactive():
    """Start interactive mode"""
    print_header()

    console.print("[yellow]Interactive mode - Type 'exit' or 'quit' to exit[/yellow]\n")

    orchestrator = None

    try:
        orchestrator = Orchestrator()
        console.print("[green]✓ Orchestrator initialized[/green]\n")

        while True:
            task = console.input("[bold cyan]Task>[/bold cyan] ")

            if task.lower() in ['exit', 'quit', 'q']:
                break

            if not task.strip():
                continue

            # Run task
            asyncio.run(_run_task(task, None, [], "config/settings.yaml"))

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
    finally:
        if orchestrator:
            asyncio.run(orchestrator.cleanup())


if __name__ == "__main__":
    cli()
