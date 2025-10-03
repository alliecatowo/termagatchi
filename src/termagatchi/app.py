"""Main Textual application for Termagatchi."""

import os
import tomllib
from datetime import datetime
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.timer import Timer
from textual.widgets import Footer, Header

from .ai import FallbackSystem, GameContext, LLMConfig, create_client_from_config, create_client_from_env
from .engine import GameConfig, GameEngine, StateManager
from .widgets.chat import ChatLog
from .widgets.input import CommandInput
from .widgets.notifications import NotificationsPanel
from .widgets.sprite import SpriteWidget
from .widgets.status import StatusPanel


def load_environment() -> None:
    """Load environment variables from .env file if it exists."""
    env_file = Path(".env")
    if env_file.exists():
        # TODO: Use python-dotenv library for proper .env loading
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
                    print(f"DEBUG: Loaded {key.strip()}={value.strip()[:10]}...")
    else:
        print("DEBUG: .env file not found")


def load_llm_config() -> LLMConfig:
    """Load LLM configuration from config file or environment."""
    config_dir = Path.home() / ".termagatchi"
    config_file = config_dir / "config.toml"

    if config_file.exists():
        try:
            with open(config_file, "rb") as f:
                data = tomllib.load(f)
            if "lm" in data:
                lm_config = data["lm"]
                print(f"Loaded config from file: {lm_config}")
                return LLMConfig(**lm_config)
        except Exception as e:
            print(f"Error loading config: {e}")

    # Fall back to environment variables
    config = LLMConfig(
        provider=os.getenv("LLM_PROVIDER", "deterministic"),
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        timeout_s=int(os.getenv("LLM_TIMEOUT", "4")),
        max_retries=int(os.getenv("LLM_MAX_RETRIES", "2")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "64")),
    )
    print(f"Using fallback config: {config}")
    return config


class TermagatchiApp(App):
    """Main Termagatchi application."""

    CSS_PATH = "themes/termagatchi.tcss"
    TITLE = "Termagatchi"
    SUB_TITLE = "Your AI-powered terminal pet"

    def __init__(self, save_dir: Path | None = None, **kwargs):
        super().__init__(**kwargs)

        # Environment variables should be loaded by mise automatically
        # TODO: Remove manual load_environment() since we're using mise

        # Initialize game components
        self.config = GameConfig()
        self.state_manager = StateManager(save_dir)
        self.game_engine = GameEngine(self.config, self.state_manager)

        # Initialize AI client
        try:
            llm_config = load_llm_config()
            self.ai_client = create_client_from_config(llm_config)
            self.ai_available = self.ai_client.test_connection()
        except Exception:
            self.ai_client = None
            self.ai_available = False

        # UI components
        self.status_panel: StatusPanel | None = None
        self.sprite_widget: SpriteWidget | None = None
        self.notifications_panel: NotificationsPanel | None = None
        self.chat_log: ChatLog | None = None
        self.command_input: CommandInput | None = None

        # Game timers
        self.tick_timer: Timer | None = None
        self.autosave_timer: Timer | None = None
        self.idle_animation_timer: Timer | None = None
        self.thought_timer: Timer | None = None

    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header()

        # Main layout container
        with Container(id="main-container"):
            # Top section: Status bars with progress bars
            with Horizontal(id="status-section"):
                yield StatusPanel(id="status-panel")
                # Spacer for notifications
                with Container(id="notifications-spacer"):
                    yield NotificationsPanel(id="notifications")

            # Main content: Sprite (left) and Chat (right/bottom)
            with Horizontal(id="content-section"):
                # Left: Large sprite area
                with Container(id="sprite-container"):
                    yield SpriteWidget(id="sprite")

                # Right: Chat area (full height)
                with Container(id="chat-container"):
                    yield ChatLog(id="chat-log")

            # Bottom: Input area
            with Container(id="input-section"):
                yield CommandInput(id="command-input")


    def on_mount(self) -> None:
        """Initialize the application when mounted."""
        # Store widget references
        self.status_panel = self.query_one("#status-panel", StatusPanel)
        self.sprite_widget = self.query_one("#sprite", SpriteWidget)
        self.notifications_panel = self.query_one("#notifications", NotificationsPanel)
        self.chat_log = self.query_one("#chat-log", ChatLog)
        self.command_input = self.query_one("#command-input", CommandInput)

        # Load saved chat history
        self.chat_log.load_chat_history(self.game_engine.state.chat_history)

        # Update UI with current state
        self.update_ui()

        # Add startup notification
        if self.ai_available:
            self.notifications_panel.add_notification("AI connected!")
        else:
            self.notifications_panel.add_notification("Offline mode (AI unavailable)")

        # Start game timers
        self.start_timers()

        # Show greeting
        self.show_greeting()

        # Focus input
        if self.command_input:
            self.set_focus(self.command_input.input_field)

    def start_timers(self) -> None:
        """Start the game tick and autosave timers."""
        # Game tick timer (every 60 seconds)
        self.tick_timer = self.set_interval(
            self.config.tick_interval_s, self.game_tick, pause=False
        )

        # Autosave timer (every 30 seconds)
        self.autosave_timer = self.set_interval(
            self.config.autosave_interval_s, self.autosave, pause=False
        )

        # Idle animation timer (every 8-15 seconds)
        self.idle_animation_timer = self.set_interval(
            8 + (self.game_engine.state.stats.happiness / 10), self.idle_animation, pause=False
        )

        # Thought timer (every 20-40 seconds)
        self.thought_timer = self.set_interval(
            20 + (self.game_engine.state.stats.energy / 5), self.random_thought, pause=False
        )

    def game_tick(self) -> None:
        """Process one game tick."""
        self.game_engine.tick()
        self.update_ui()

        # Update notifications with any new ones
        for notification in self.game_engine.state.notifications:
            self.notifications_panel.add_notification(notification)

        # Clear processed notifications
        self.game_engine.state.notifications.clear()

    def autosave(self) -> None:
        """Automatically save the game state."""
        if self.game_engine.save():
            self.notifications_panel.add_notification("Game saved")

    def idle_animation(self) -> None:
        """Trigger a random idle animation for the pet."""
        import random
        from .ai.schema import PetAction

        # Only play idle animations if not sleeping
        if self.game_engine.state.stats.sleeping:
            return

        # Random idle actions
        idle_actions = [
            PetAction.WIGGLE,
            PetAction.WAVE,
            PetAction.SMILE,
            PetAction.THINK,
        ]

        action = random.choice(idle_actions)
        self.sprite_widget.play_animation(action)

        # Add a subtle visual indicator that the pet is active
        if self.sprite_widget:
            # This could trigger a small animation or effect
            pass

    def random_thought(self) -> None:
        """Generate and display a random thought from the pet."""
        from .ai import FallbackSystem

        # Get a random thought based on current state
        thought = FallbackSystem.get_random_thought(self.game_engine.get_current_stats())

        if thought:
            self.chat_log.add_pet_message(thought.say, thought.action.value)
            self.sprite_widget.play_animation(thought.action)

            # Save to chat history
            self.game_engine.add_chat_message("pet", thought.say)

    def update_ui(self) -> None:
        """Update all UI components with current game state."""
        if not self.status_panel:
            return

        # Update status bars
        self.status_panel.update_stats(self.game_engine.state.stats)

        # Update sprite animation engine with current stats
        if self.sprite_widget:
            self.sprite_widget.update_stats(self.game_engine.state.stats)

    def show_greeting(self) -> None:
        """Show initial greeting from the pet."""
        greeting = FallbackSystem.get_greeting()
        self.chat_log.add_pet_message(greeting.say, greeting.action.value)
        self.sprite_widget.play_animation(greeting.action)

    @work
    async def process_ai_response(self, user_input: str) -> None:
        """Process user input and get AI response."""
        try:
            # Start thinking animation
            if self.sprite_widget:
                self.sprite_widget.animation_engine.start_thinking()

            # Add thinking indicator to chat
            self.chat_log.add_thinking_indicator()

            # Build context for AI
            context = GameContext(
                stats=self.game_engine.get_current_stats(),
                recent_events=self.game_engine.get_recent_events(),
                last_user_input=user_input,
                time_of_day=self.get_time_of_day(),
                pet_name="Termagatchi",
            )

            # Get AI response
            if self.ai_available and self.ai_client:
                response = self.ai_client.get_pet_reply(context)
            else:
                response = FallbackSystem.get_response(
                    context.stats, user_input, context.time_of_day
                )

            # Stop thinking animation
            if self.sprite_widget:
                self.sprite_widget.animation_engine.stop_thinking()

            # Display response
            self.chat_log.add_pet_message(response.say, response.action.value)
            self.sprite_widget.play_animation(response.action)

            # Save to chat history
            self.game_engine.add_chat_message("pet", response.say)

        except Exception as e:
            # Stop thinking animation on error
            if self.sprite_widget:
                self.sprite_widget.animation_engine.stop_thinking()

            self.chat_log.add_error_message(f"AI error: {e}")
            # Use fallback
            fallback = FallbackSystem.get_error_response()
            self.chat_log.add_pet_message(fallback.say, fallback.action.value)
            self.sprite_widget.play_animation(fallback.action)

    def get_time_of_day(self) -> str:
        """Get current time of day for context."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "day"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    def on_command_input_submitted(self, event: CommandInput.Submitted) -> None:
        """Handle submitted user input."""
        value = event.value
        is_command = event.is_command

        # Add to chat log
        self.chat_log.add_user_message(value)

        # Save to chat history
        self.game_engine.add_chat_message("user", value)

        if is_command:
            # Process command
            self.process_command(value)
        else:
            # Process as chat message
            self.process_ai_response(value)

    def process_command(self, command: str) -> None:
        """Process a game command."""
        parts = command[1:].split()  # Remove '/' and split
        if not parts:
            return

        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        try:
            if cmd == "feed":
                item = args[0] if args else None
                result = self.game_engine.command_feed(item)
                self.chat_log.add_system_message(result)

            elif cmd == "clean":
                item = args[0] if args else None
                result = self.game_engine.command_clean(item)
                self.chat_log.add_system_message(result)

            elif cmd == "play":
                item = args[0] if args else None
                result = self.game_engine.command_play(item)
                self.chat_log.add_system_message(result)

            elif cmd == "sleep":
                action = args[0] if args else "toggle"
                result = self.game_engine.command_sleep(action)
                self.chat_log.add_system_message(result)

            elif cmd == "pet":
                result = self.game_engine.command_pet()
                self.chat_log.add_system_message(result)

            elif cmd == "status":
                result = self.game_engine.command_status()
                self.chat_log.add_system_message(result)

            elif cmd == "save":
                if self.game_engine.save():
                    self.chat_log.add_system_message("Game saved successfully!")
                else:
                    self.chat_log.add_system_message("Failed to save game!")

            elif cmd == "quit" or cmd == "exit":
                self.exit()

            elif cmd == "help":
                help_text = (
                    "Available commands:\n"
                    "/feed [item] - Feed your pet\n"
                    "/clean [item] - Clean your pet\n"
                    "/play [item] - Play with your pet\n"
                    "/sleep [on|off] - Make pet sleep or wake up\n"
                    "/pet - Pet your companion\n"
                    "/status - Show pet stats\n"
                    "/save - Save game\n"
                    "/quit - Exit game"
                )
                self.chat_log.add_system_message(help_text)

            else:
                self.chat_log.add_system_message(f"Unknown command: /{cmd}")

        except Exception as e:
            self.chat_log.add_error_message(f"Command error: {e}")

        # Update UI after command
        self.update_ui()

    def action_quit(self) -> None:
        """Handle quit action."""
        # Save before quitting
        self.game_engine.save()
        self.exit()

    def on_key(self, event) -> None:
        """Handle key presses."""
        if event.key == "ctrl+c":
            self.action_quit()
        elif event.key == "escape":
            # Focus input
            if self.command_input:
                self.command_input.focus_input()


def run_app(save_dir: Path | None = None) -> None:
    """Run the Termagatchi application."""
    app = TermagatchiApp(save_dir=save_dir)
    app.run()
