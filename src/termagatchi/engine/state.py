"""Game state management and persistence."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import GameConfig, GameState


class StateManager:
    """Manages game state persistence and loading."""

    def __init__(self, save_dir: Path | None = None):
        if save_dir is None:
            # Default to ~/.termagatchi/
            save_dir = Path.home() / ".termagatchi"

        self.save_dir = Path(save_dir)
        self.save_file = self.save_dir / "save.json"
        self.backup_file = self.save_dir / "save.json.bak"
        self.config_file = self.save_dir / "config.toml"

        # Ensure directory exists
        self.save_dir.mkdir(exist_ok=True)

    def save_state(self, state: GameState) -> bool:
        """Save game state to JSON file."""
        try:
            # Create backup of existing save
            if self.save_file.exists():
                self.save_file.rename(self.backup_file)

            # Prepare state data for serialization
            state_dict = state.model_dump()

            # Convert datetime objects to ISO strings for ALL fields
            state_dict = self._serialize_datetimes(state_dict)

            # Write to file
            with open(self.save_file, "w", encoding="utf-8") as f:
                json.dump(state_dict, f, indent=2, ensure_ascii=False)

            print(f"Game saved to {self.save_file}")
            return True

        except Exception as e:
            print(f"Failed to save game state: {e}")
            # Restore backup if save failed
            if self.backup_file.exists():
                self.backup_file.rename(self.save_file)
            return False

    def load_state(self) -> GameState | None:
        """Load game state from JSON file."""
        # Try main save file first
        if self.save_file.exists():
            state = self._load_from_file(self.save_file)
            if state:
                return state

        # Fall back to backup
        if self.backup_file.exists():
            print("Main save corrupted, loading from backup...")
            state = self._load_from_file(self.backup_file)
            if state:
                # Restore backup as main save
                self.backup_file.rename(self.save_file)
                return state

        # No valid save found
        print("No save file found, starting new game")
        return None

    def _load_from_file(self, file_path: Path) -> GameState | None:
        """Load state from a specific file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Deserialize datetime objects
            data = self._deserialize_datetimes(data)

            # Create GameState object
            return GameState(**data)

        except Exception as e:
            print(f"Failed to load from {file_path}: {e}")
            return None

    def _serialize_datetimes(self, data: Any) -> Any:
        """Convert datetime objects to ISO strings for JSON serialization."""
        if isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, dict):
            return {key: self._serialize_datetimes(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._serialize_datetimes(item) for item in data]
        else:
            return data

    def _deserialize_datetimes(self, data: Any) -> Any:
        """Convert ISO strings back to datetime objects."""
        if isinstance(data, str):
            # Try to parse as datetime
            for fmt in ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(data, fmt)
                except ValueError:
                    continue
            return data
        elif isinstance(data, dict):
            # Special handling for chat_history - keep timestamps as strings
            if "chat_history" in data:
                result = {}
                for key, value in data.items():
                    if key == "chat_history":
                        # Keep chat_history timestamps as strings for the UI
                        result[key] = value
                    else:
                        result[key] = self._deserialize_datetimes(value)
                return result
            else:
                return {key: self._deserialize_datetimes(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._deserialize_datetimes(item) for item in data]
        else:
            return data

    def create_new_state(self) -> GameState:
        """Create a new game state with default values."""
        return GameState()

    def get_save_info(self) -> dict[str, Any] | None:
        """Get information about the save file."""
        if not self.save_file.exists():
            return None

        try:
            stat = self.save_file.stat()
            with open(self.save_file, encoding="utf-8") as f:
                data = json.load(f)

            return {
                "file_size": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime),
                "created_at": data.get("created_at"),
                "total_play_time_s": data.get("total_play_time_s", 0),
                "events_count": len(data.get("events", [])),
                "chat_count": len(data.get("chat_history", [])),
            }

        except Exception:
            return None


class GameEngine:
    """Core game logic and state management."""

    def __init__(self, config: GameConfig, state_manager: StateManager):
        self.config = config
        self.state_manager = state_manager
        self.state = state_manager.load_state() or state_manager.create_new_state()
        self.last_autosave = datetime.now()

    def tick(self) -> None:
        """Process one game tick (stat decay, checks, etc.)."""
        now = datetime.now()
        time_since_last = (now - self.state.last_tick).total_seconds()

        # Update play time
        self.state.total_play_time_s += time_since_last

        # Apply stat decay
        self._apply_decay()

        # Check for negative effects
        self._check_negative_effects()

        # Update last tick time
        self.state.last_tick = now

        # Auto-save if needed
        if (now - self.last_autosave).total_seconds() >= self.config.autosave_interval_s:
            self.save()
            self.last_autosave = now

    def _apply_decay(self) -> None:
        """Apply stat decay over time."""
        stats = self.state.stats

        # Hunger always decays
        stats.hunger = max(0, stats.hunger - self.config.hunger_decay)

        # Hygiene always decays (slower)
        stats.hygiene = max(0, stats.hygiene - self.config.hygiene_decay)

        # Energy decay depends on sleep state
        if stats.sleeping:
            # Recover energy while sleeping
            stats.energy = min(100, stats.energy + self.config.energy_recovery_sleeping)
        else:
            # Lose energy while awake
            stats.energy = max(0, stats.energy - self.config.energy_decay_awake)

        # Record decay event
        self.state.add_event("decay", "Time passes...")

    def _check_negative_effects(self) -> None:
        """Check for and apply negative effects from low stats."""
        stats = self.state.stats

        # Mood effects from low basic needs
        if (
            stats.hunger < self.config.low_hunger_threshold
            or stats.hygiene < self.config.low_hygiene_threshold
        ):
            stats.happiness = max(0, stats.happiness - self.config.mood_decay_rate)

        # Sickness from critical states
        critical_conditions = [
            stats.hunger < self.config.critical_hunger_threshold,
            stats.hygiene < self.config.critical_hygiene_threshold,
            stats.energy < self.config.critical_energy_threshold,
        ]

        if any(critical_conditions):
            import random

            if random.random() < self.config.sickness_chance:
                stats.health = max(0, stats.health - self.config.health_loss_sick)
                self.state.add_event("sickness", "Pet got sick from neglect!")
                self.state.add_notification("Termagatchi is sick!")

    def command_feed(self, item_name: str | None = None) -> str:
        """Handle the /feed command."""
        from .items import ItemManager

        item_manager = ItemManager()
        item_name = item_name or "kibble"  # Default food

        # Check if item exists and is a food item
        item = item_manager.get_item("food", item_name)
        if not item:
            return f"Don't have any {item_name}!"

        # Check cooldown
        item_id = f"food_{item_name}"
        if self.state.is_item_on_cooldown(item_id, item.cooldown_s):
            return f"{item.name} is on cooldown!"

        # Apply effects
        self.state.stats.apply_effects(item.effects)
        self.state.use_item(item_id)

        # Record event
        self.state.add_event("command", f"Fed {item.name}")
        self.state.add_notification(f"Fed {item.name}")

        return f"Fed {item.name}! {item.description}"

    def command_clean(self, item_name: str | None = None) -> str:
        """Handle the /clean command."""
        from .items import ItemManager

        item_manager = ItemManager()
        item_name = item_name or "soap"  # Default cleaning item

        # Check if item exists and is a cleaning item
        item = item_manager.get_item("cleaning", item_name)
        if not item:
            return f"Don't have any {item_name}!"

        # Check cooldown
        item_id = f"cleaning_{item_name}"
        if self.state.is_item_on_cooldown(item_id, item.cooldown_s):
            return f"{item.name} is on cooldown!"

        # Apply effects
        self.state.stats.apply_effects(item.effects)
        self.state.use_item(item_id)

        # Record event
        self.state.add_event("command", f"Used {item.name}")
        self.state.add_notification(f"Cleaned with {item.name}")

        return f"Cleaned with {item.name}! {item.description}"

    def command_play(self, item_name: str | None = None) -> str:
        """Handle the /play command."""
        from .items import ItemManager

        item_manager = ItemManager()
        item_name = item_name or "ball"  # Default toy

        # Check if item exists and is a toy
        item = item_manager.get_item("toys", item_name)
        if not item:
            return f"Don't have any {item_name}!"

        # Check cooldown
        item_id = f"toy_{item_name}"
        if self.state.is_item_on_cooldown(item_id, item.cooldown_s):
            return f"{item.name} is on cooldown!"

        # Apply effects
        self.state.stats.apply_effects(item.effects)
        self.state.use_item(item_id)

        # Record event
        self.state.add_event("command", f"Played with {item.name}")
        self.state.add_notification(f"Played with {item.name}")

        return f"Played with {item.name}! {item.description}"

    def command_sleep(self, action: str = "toggle") -> str:
        """Handle the /sleep command."""
        if action.lower() in ["on", "true", "yes"]:
            self.state.stats.sleeping = True
            self.state.add_event("command", "Pet went to sleep")
            return "Pet is now sleeping. Zzz..."
        elif action.lower() in ["off", "false", "no"]:
            self.state.stats.sleeping = False
            self.state.add_event("command", "Pet woke up")
            return "Pet woke up!"
        else:
            # Toggle
            self.state.stats.sleeping = not self.state.stats.sleeping
            if self.state.stats.sleeping:
                self.state.add_event("command", "Pet went to sleep")
                return "Pet is now sleeping. Zzz..."
            else:
                self.state.add_event("command", "Pet woke up")
                return "Pet woke up!"

    def command_pet(self) -> str:
        """Handle the /pet command."""
        # Simple affection boost
        self.state.stats.affection = min(100, self.state.stats.affection + 5)
        self.state.stats.happiness = min(100, self.state.stats.happiness + 3)

        self.state.add_event("command", "Pet was petted")
        return "Pet loves the attention!"

    def command_status(self) -> str:
        """Handle the /status command."""
        stats = self.state.stats
        status_lines = [
            f"Hunger: {stats.hunger:.0f}/100",
            f"Hygiene: {stats.hygiene:.0f}/100",
            f"Happiness: {stats.happiness:.0f}/100",
            f"Energy: {stats.energy:.0f}/100",
            f"Affection: {stats.affection:.0f}/100",
            f"Health: {stats.health:.0f}/100",
            f"Sleeping: {'Yes' if stats.sleeping else 'No'}",
            f"Play time: {self.state.total_play_time_s / 3600:.1f} hours",
        ]
        return "\n".join(status_lines)

    def save(self) -> bool:
        """Save the current game state."""
        return self.state_manager.save_state(self.state)

    def get_current_stats(self) -> dict[str, Any]:
        """Get current stats for LLM context."""
        return self.state.stats.to_dict()

    def get_recent_events(self, count: int = 6) -> list[str]:
        """Get recent events for LLM context."""
        return [str(event) for event in self.state.events[-count:]]

    def add_chat_message(self, sender: str, message: str) -> None:
        """Add a chat message to the history."""
        self.state.add_chat_message(sender, message)
