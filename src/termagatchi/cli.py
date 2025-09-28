"""CLI interface for Termagatchi using Typer."""

import os
import sys
from pathlib import Path
from typing import Optional, Annotated

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .app import run_app
from .engine import StateManager

# Create the main Typer app
app = typer.Typer(
    name="termagatchi",
    help="🐾 Termagatchi - Your AI-powered terminal pet",
    epilog="For more information, visit: https://github.com/your-username/termagatchi",
    no_args_is_help=True,
    rich_markup_mode="rich"
)

console = Console()


@app.command()
def run(
    save_dir: Annotated[
        Optional[Path],
        typer.Option("--save-dir", "-s", help="Directory for save files")
    ] = None,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable debug mode")
    ] = False,
) -> None:
    """🎮 Run the Termagatchi application."""

    if debug:
        console.print("= [yellow]Debug mode enabled[/yellow]")

    try:
        # Welcome message
        welcome_panel = Panel(
            Text("Welcome to Termagatchi!\n🐾 Your AI-powered terminal pet", justify="center"),
            title="< Termagatchi",
            border_style="cyan"
        )
        console.print(welcome_panel)

        # Check AI configuration
        check_ai_config()

        # Run the app
        run_app(save_dir=save_dir)

    except KeyboardInterrupt:
        console.print("\n=K [yellow]Goodbye! Your pet will miss you![/yellow]")
        sys.exit(0)
    except Exception as e:
        if debug:
            console.print_exception()
        else:
            console.print(f"L [red]Error starting Termagatchi: {e}[/red]")
        sys.exit(1)


@app.command()
def config(
    edit: Annotated[
        bool,
        typer.Option("--edit", "-e", help="Open config file in editor")
    ] = False,
    show: Annotated[
        bool,
        typer.Option("--show", "-s", help="Show current configuration")
    ] = False,
    provider: Annotated[
        Optional[str],
        typer.Option("--provider", "-p", help="Set AI provider (openai, anthropic, google, ollama)")
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="Set AI model name")
    ] = None,
) -> None:
    """� Manage Termagatchi configuration."""

    config_dir = Path.home() / ".termagatchi"
    config_file = config_dir / "config.toml"

    if edit:
        edit_config_file(config_file)
    elif show:
        show_current_config()
    elif provider or model:
        update_config(config_file, provider, model)
    else:
        # Interactive configuration
        interactive_config(config_file)


@app.command()
def status(
    save_dir: Annotated[
        Optional[Path],
        typer.Option("--save-dir", "-s", help="Directory for save files")
    ] = None,
) -> None:
    """=� Show pet status and game information."""

    try:
        state_manager = StateManager(save_dir)
        game_state = state_manager.load_state()

        if not game_state:
            console.print("L [red]No save file found. Start a new game with 'termagatchi run'[/red]")
            return

        # Create status table
        table = Table(title="=> Pet Status", border_style="cyan")
        table.add_column("Stat", style="yellow")
        table.add_column("Value", style="green")
        table.add_column("Status", style="cyan")

        stats = game_state.stats

        def get_status_emoji(value: float) -> str:
            if value >= 80:
                return "=� Excellent"
            elif value >= 60:
                return "=� Good"
            elif value >= 40:
                return "=� Okay"
            elif value >= 20:
                return "=4 Poor"
            else:
                return "=� Critical"

        table.add_row("Hunger", f"{stats.hunger:.0f}/100", get_status_emoji(stats.hunger))
        table.add_row("Hygiene", f"{stats.hygiene:.0f}/100", get_status_emoji(stats.hygiene))
        table.add_row("Happiness", f"{stats.happiness:.0f}/100", get_status_emoji(stats.happiness))
        table.add_row("Energy", f"{stats.energy:.0f}/100", get_status_emoji(stats.energy))
        table.add_row("Affection", f"{stats.affection:.0f}/100", get_status_emoji(stats.affection))
        table.add_row("Health", f"{stats.health:.0f}/100", get_status_emoji(stats.health))
        table.add_row("Sleeping", "Yes" if stats.sleeping else "No", "=4" if stats.sleeping else "=A")

        console.print(table)

        # Additional info
        play_time_hours = game_state.total_play_time_s / 3600
        console.print(f"\n� [cyan]Total play time:[/cyan] {play_time_hours:.1f} hours")
        console.print(f"=� [cyan]Chat messages:[/cyan] {len(game_state.chat_history)}")
        console.print(f"=� [cyan]Events logged:[/cyan] {len(game_state.events)}")

    except Exception as e:
        console.print(f"L [red]Error reading save file: {e}[/red]")


@app.command()
def reset(
    save_dir: Annotated[
        Optional[Path],
        typer.Option("--save-dir", "-s", help="Directory for save files")
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Force reset without confirmation")
    ] = False,
) -> None:
    """= Reset game state (start over)."""

    if not force:
        confirm = typer.confirm("�  This will delete your current pet and start over. Are you sure?")
        if not confirm:
            console.print("L [yellow]Reset cancelled[/yellow]")
            return

    try:
        state_manager = StateManager(save_dir)

        # Remove save files
        if state_manager.save_file.exists():
            state_manager.save_file.unlink()
            console.print("=� [green]Main save file deleted[/green]")

        if state_manager.backup_file.exists():
            state_manager.backup_file.unlink()
            console.print("=� [green]Backup save file deleted[/green]")

        console.print(" [green]Game reset successfully! Start a new game with 'termagatchi run'[/green]")

    except Exception as e:
        console.print(f"❌ [red]Error resetting game: {e}[/red]")


@app.command()
def demo() -> None:
    """🎬 Run a demonstration of Termagatchi features."""

    console.print(Panel(
        "🎬 [cyan]Termagatchi Demo[/cyan]\n\n"
        "This would show a scripted demo of the game features:\n"
        "• AI-powered pet interactions\n"
        "• Stat management and care commands\n"
        "• Multiple LLM provider support\n"
        "• Real-time animations and responses\n\n"
        "💡 [yellow]Demo mode not yet implemented[/yellow]\n"
        "Use 'termagatchi run' to start the real game!",
        title="Demo Mode",
        border_style="yellow"
    ))


def check_ai_config() -> None:
    """Check and display AI configuration status."""

    # Check for common environment variables
    ai_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Google": os.getenv("GOOGLE_API_KEY"),
        "Ollama": os.getenv("OPENAI_API_BASE") and "ollama" in os.getenv("OPENAI_API_BASE", "").lower(),
    }

    configured_providers = [name for name, key in ai_keys.items() if key]

    if configured_providers:
        console.print(f"> [green]AI providers available:[/green] {', '.join(configured_providers)}")
    else:
        console.print("� [yellow]No AI providers configured. Running in offline mode.[/yellow]")
        console.print("=� [dim]Set API keys as environment variables or use 'termagatchi config' to set up AI.[/dim]")


def show_current_config() -> None:
    """Show current configuration."""

    table = Table(title="=' Current Configuration", border_style="cyan")
    table.add_column("Setting", style="yellow")
    table.add_column("Value", style="green")
    table.add_column("Status", style="cyan")

    # Check environment variables
    env_vars = [
        ("OPENAI_API_KEY", "OpenAI API Key"),
        ("ANTHROPIC_API_KEY", "Anthropic API Key"),
        ("GOOGLE_API_KEY", "Google API Key"),
        ("OPENAI_API_BASE", "Custom API Base"),
        ("LLM_PROVIDER", "Default Provider"),
        ("LLM_MODEL", "Default Model"),
        ("LLM_TIMEOUT", "Request Timeout"),
        ("LLM_TEMPERATURE", "AI Temperature"),
    ]

    for env_var, description in env_vars:
        value = os.getenv(env_var)
        if value:
            # Mask API keys for security
            if "KEY" in env_var and len(value) > 8:
                display_value = value[:4] + "..." + value[-4:]
            else:
                display_value = value
            status = " Set"
        else:
            display_value = "[dim]Not set[/dim]"
            status = "L Missing"

        table.add_row(description, display_value, status)

    console.print(table)


def edit_config_file(config_file: Path) -> None:
    """Open config file in editor."""

    if not config_file.exists():
        # Create basic config file
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w') as f:
            f.write("""# Termagatchi Configuration

[lm]
provider = "openai"           # "anthropic" | "openai" | "google" | "ollama" | ...
model = "gpt-4o-mini"         # "claude-3-haiku" | "gpt-4o-mini" | "gemini-1.5-flash" ...
timeout_s = 4
max_retries = 2
temperature = 0.7

[theme]
mode = "auto"

# Set your API keys as environment variables:
# export OPENAI_API_KEY="your-key-here"
# export ANTHROPIC_API_KEY="your-key-here"
# export GOOGLE_API_KEY="your-key-here"
""")

    # Try to open in editor
    editor = os.getenv("EDITOR", "nano")
    os.system(f"{editor} {config_file}")


def update_config(config_file: Path, provider: Optional[str], model: Optional[str]) -> None:
    """Update configuration with new values."""

    console.print("� [yellow]Configuration update not yet implemented[/yellow]")
    console.print("=� [dim]Use 'termagatchi config --edit' to manually edit the config file[/dim]")


def interactive_config(config_file: Path) -> None:
    """Interactive configuration setup."""

    console.print(Panel(
        "🔧 [cyan]Interactive Configuration Setup[/cyan]\n\n"
        "This would guide you through setting up:\n"
        "• AI provider selection\n"
        "• API key configuration\n"
        "• Model preferences\n"
        "• Theme settings\n\n"
        "💡 [yellow]Interactive config not yet implemented[/yellow]\n"
        "Use 'termagatchi config --edit' for manual configuration.",
        title="Configuration Setup",
        border_style="yellow"
    ))


if __name__ == "__main__":
    app()