"""
Terminal User Interface (TUI) for BiteSize Agent using Rich.
Provides a zero-distraction, keyboard-driven focus environment.
"""
import time
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from bitesize.agent import BiteSizeAgent
from bitesize.schemas import DecomposedPlan, AtomicStep

console = Console()


def display_welcome_banner():
    banner = Text()
    banner.append("🌱 BiteSize — Open-Source ADHD Task De-Overwhelmer\n", style="bold green")
    banner.append("Built with love for Mayank 💚 | 100% Local Open AI Core\n", style="dim")
    banner.append("Defeat executive dysfunction freeze with 2-minute atomic micro-steps.", style="italic cyan")
    
    panel = Panel(
        banner,
        border_style="green",
        subtitle="[bold white]No Cloud Leakage • No Judgment • Zero Subscriptions[/bold white]"
    )
    console.print(panel)


def run_interactive_tui(agent: BiteSizeAgent, sample_mode: bool = False):
    display_welcome_banner()
    
    # Check Ollama status
    if agent.llm_client.is_ollama_available():
        models = agent.llm_client.list_local_models()
        model_str = ", ".join(models) if models else agent.llm_client.model_name
        console.print(f"[bold green]✓ Local Ollama Connected[/bold green] (Models: {model_str})")
    else:
        console.print("[bold yellow]⚡ Running on Embedded Local Neural Engine[/bold yellow] (Instant, 100% offline, zero config)")

    console.print("\n[bold white]Enter your chaotic brain-dump below[/bold white] (press Enter twice to submit):")
    
    if sample_mode:
        brain_dump = (
            "My room is a complete disaster clothes on floor desk covered in cups. "
            "I have to finish my machine learning lab report due tonight but my code is broken, "
            "and I haven't eaten lunch and need to reply to mom's message and wash dishes before roommate comes home."
        )
        console.print(f"[dim italic]Loaded Mayank's real Sunday panic backlog:[/dim italic]\n[cyan]{brain_dump}[/cyan]\n")
    else:
        lines = []
        while True:
            try:
                line = input()
                if not line and lines:
                    break
                if line:
                    lines.append(line)
            except EOFError:
                break
        brain_dump = " ".join(lines) if lines else (
            "messy room clothes everywhere code is broken haven't eaten need to reply to mom"
        )

    # De-overwhelm with spinner
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="[green]Deconstructing cognitive friction mountain into 2-min pebbles...", total=None)
        time.sleep(1.0)
        plan = agent.deoverwhelm(brain_dump, paralysis_level="extreme")

    # Display Analysis
    console.print("\n")
    analysis_panel = Panel(
        f"[bold red]Perceived Mountain:[/bold red] {plan.friction_analysis.perceived_mountain}\n"
        f"[bold yellow]Root Cause Blocker:[/bold yellow] {plan.friction_analysis.core_blocker}\n"
        f"[bold cyan]Actionable Strategy:[/bold cyan] We shredded this into [bold green]{plan.total_steps} atomic 2-minute steps[/bold green] (~{plan.total_estimated_minutes} mins total).\n\n"
        f"[italic green]\"{plan.body_doubling_message}\"[/italic green]",
        title="🧠 Cognitive De-escalation Briefing",
        border_style="cyan"
    )
    console.print(analysis_panel)

    console.print("\n[bold green]Launching Anti-Paralysis Focus Mode...[/bold green]")
    console.print("[dim]You will only see ONE step at a time. The rest are hidden to protect your dopamine.[/dim]\n")

    # Focus Mode Loop
    while True:
        step = agent.get_current_focus_step()
        if not step:
            console.print(Panel(
                "[bold green]🎉 ALL ATOMIC STEPS CONQUERED! 🎉[/bold green]\n\n"
                f"You shattered inertia, earned [bold yellow]{agent.user_state.dopamine_score} Dopamine Points[/bold yellow], "
                f"and achieved a [bold cyan]{agent.user_state.streak}-step momentum streak[/bold cyan]!\n"
                "Take a deep breath. You proved you have agency today.",
                border_style="green"
            ))
            break

        idx = agent.user_state.current_step_index + 1
        total = len(plan.atomic_steps)
        
        step_text = Text()
        step_text.append(f"Step {idx} of {total} • Domain: {step.domain}\n\n", style="bold yellow")
        step_text.append(f"🎯 {step.title}\n", style="bold white text-lg")
        step_text.append(f"👉 {step.description}\n\n", style="italic")
        step_text.append(f"⏱️ Target: {step.estimated_seconds} seconds | {step.micro_reward}", style="dim green")

        step_panel = Panel(
            step_text,
            title="[bold green]Current Atomic Step (Zero Distractions)[/bold green]",
            border_style="green",
            subtitle="[white][Enter] Complete & Dopamine  |  [t] Run 2-Min Timer  |  [s] Skip  |  [m] View All  |  [q] Quit[/white]"
        )
        console.print(step_panel)

        choice = input("Your action: ").strip().lower()

        if choice == "q":
            console.print("[yellow]Session paused. No guilt. Come back anytime.[/yellow]")
            break
        elif choice == "t":
            # Live Terminal Countdown Timer
            duration = step.estimated_seconds
            console.print(f"\n[cyan]⏱️ 2-Minute Timer started ({duration}s). Focus solely on this micro-step...[/cyan]")
            with Progress(transient=True) as timer_prog:
                task_id = timer_prog.add_task("[green]Focusing...", total=duration)
                for _ in range(duration):
                    time.sleep(1)
                    timer_prog.update(task_id, advance=1)
            sys.stdout.write('\a')
            sys.stdout.flush()
            console.print("[bold yellow]🔔 Time's up! Did you finish or make progress?[/bold yellow]")
            input("Press [Enter] to complete and collect dopamine...")
            res = agent.complete_current_step()
            console.print(f"\n[bold green]✨ DING! Micro-Step Conquered![/bold green] {res['reward']['reward_banner']}")
            sys.stdout.write('\a')
            sys.stdout.flush()
        elif choice == "s":
            res = agent.skip_current_step()
            console.print(f"[dim]{res['message']}[/dim]\n")
        elif choice == "m":
            console.print("\n[bold cyan]--- All Generated Steps ---[/bold cyan]")
            console.print(agent.export_plan_markdown())
            console.print("[bold cyan]--------------------------[/bold cyan]\n")
        else:
            # Complete step
            res = agent.complete_current_step()
            sys.stdout.write('\a')
            sys.stdout.flush()
            console.print(f"\n[bold green]✨ DING! Micro-Step Conquered![/bold green] {res['reward']['reward_banner']}")
            if res['reward']['milestone']:
                console.print(f"[bold yellow]{res['reward']['milestone']}[/bold yellow]")
            console.print(f"[cyan]Streak: {agent.user_state.streak} 🔥 | Total Dopamine: {agent.user_state.dopamine_score} pts[/cyan]")
            
            # Show historical stats from SQLite
            stats = agent.storage.get_user_stats(agent.user_name)
            console.print(f"[dim]All-time Conquered: {stats['total_conquered_tasks']} tasks | Lifetime Dopamine: {stats['all_time_dopamine']} pts[/dim]")
            console.print(f"[italic dim]\"{res['encouragement']}\"[/italic dim]\n")
            time.sleep(0.5)
            console.print(f"[italic dim]\"{res['encouragement']}\"[/italic dim]\n")
            time.sleep(0.5)
