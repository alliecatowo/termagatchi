"""Main Textual application for Termagatchi."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Header, Footer
from textual.timer import Timer
from textual import work

from .widgets.status import StatusPanel
from .widgets.sprite import SpriteWidget
from .widgets.notifications import NotificationsPanel
from .widgets.chat import ChatLog
from .widgets.input import CommandInput, CommandsPanel

from .engine import StateManager, GameEngine, GameConfig
from .ai import GameContext, create_client_from_env, FallbackSystem


class TermagatchiApp(App):
    """Main Termagatchi application."""

    CSS_PATH = "themes/termagatchi.tcss"
    TITLE = "Termagatchi"
    SUB_TITLE = "Your AI-powered terminal pet"

    def __init__(self, save_dir: Optional[Path] = None, **kwargs):
        super().__init__(**kwargs)

        # Initialize game components
        self.config = GameConfig()
        self.state_manager = StateManager(save_dir)
        self.game_engine = GameEngine(self.config, self.state_manager)

        # Initialize AI client
        try:
            self.ai_client = create_client_from_env()
            self.ai_available = self.ai_client.test_connection()
        except Exception:
            self.ai_client = None
            self.ai_available = False

        # UI components
        self.status_panel: Optional[StatusPanel] = None
        self.sprite_widget: Optional[SpriteWidget] = None
        self.notifications_panel: Optional[NotificationsPanel] = None
        self.chat_log: Optional[ChatLog] = None
        self.command_input: Optional[CommandInput] = None
        self.commands_panel: Optional[CommandsPanel] = None

        # Game timers
        self.tick_timer: Optional[Timer] = None
        self.autosave_timer: Optional[Timer] = None

    def compose(self) -> ComposeResult:
        """Compose the main application layout."""
        yield Header()

        # Main layout container
        with Container(id="main-container"):
            # Top row: Status bars
            with Container(id="status-row"):
                yield StatusPanel(id="status-panel")

            # Middle row: Sprite and Notifications
            with Horizontal(id="middle-row"):
                # Left: Sprite area
                with Container(id="sprite-area", classes="border-cyan"):
                    yield SpriteWidget(id="sprite")

                # Right: Notifications
                with Container(id="notifications-area", classes="border-cyan"):
                    yield NotificationsPanel(id="notifications")

            # Bottom row: Chat and Commands
            with Horizontal(id="bottom-row"):
                # Left: Chat log
                with Vertical(id="chat-area", classes="border-cyan"):
                    yield ChatLog(id="chat-log")
                    yield CommandInput(id="command-input")

                # Right: Commands panel
                with Container(id="commands-area", classes="border-cyan"):
                    yield CommandsPanel(id="commands-panel")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application when mounted."""
        # Store widget references
        self.status_panel = self.query_one("#status-panel", StatusPanel)
        self.sprite_widget = self.query_one("#sprite", SpriteWidget)
        self.notifications_panel = self.query_one("#notifications", NotificationsPanel)
        self.chat_log = self.query_one("#chat-log", ChatLog)
        self.command_input = self.query_one("#command-input", CommandInput)
        self.commands_panel = self.query_one("#commands-panel", CommandsPanel)

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

    def start_timers(self) -> None:
        """Start the game tick and autosave timers."""
        # Game tick timer (every 60 seconds)
        self.tick_timer = self.set_interval(
            self.config.tick_interval_s,
            self.game_tick,
            pause=False
        )

        # Autosave timer (every 30 seconds)
        self.autosave_timer = self.set_interval(
            self.config.autosave_interval_s,
            self.autosave,
            pause=False
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

    def update_ui(self) -> None:
        """Update all UI components with current game state."""
        if not self.status_panel:
            return

        # Update status bars
        self.status_panel.update_stats(self.game_engine.state.stats)

        # Update sprite if sleeping
        if self.game_engine.state.stats.sleeping:
            # This will be handled by animation system
            pass

    def show_greeting(self) -> None:
        """Show initial greeting from the pet."""
        greeting = FallbackSystem.get_greeting()
        self.chat_log.add_pet_message(greeting.say, greeting.action.value)
        self.sprite_widget.play_animation(greeting.action)

    @work
    async def process_ai_response(self, user_input: str) -> None:
        """Process user input and get AI response."""
        try:
            # Build context for AI
            context = GameContext(
                stats=self.game_engine.get_current_stats(),
                recent_events=self.game_engine.get_recent_events(),
                last_user_input=user_input,
                time_of_day=self.get_time_of_day(),
                pet_name="Termagatchi"
            )

            # Get AI response
            if self.ai_available and self.ai_client:
                response = self.ai_client.get_pet_reply(context)
            else:
                response = FallbackSystem.get_response(
                    context.stats,
                    user_input,
                    context.time_of_day
                )

            # Display response
            self.chat_log.add_pet_message(response.say, response.action.value)
            self.sprite_widget.play_animation(response.action)

            # Save to chat history
            self.game_engine.add_chat_message("pet", response.say)

        except Exception as e:
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


def run_app(save_dir: Optional[Path] = None) -> None:
    """Run the Termagatchi application."""
    app = TermagatchiApp(save_dir=save_dir)
    app.run()