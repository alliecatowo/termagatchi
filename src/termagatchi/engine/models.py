"""Pydantic models for game state and engine data structures."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class StatType(str, Enum):
    """Types of pet stats that can be tracked."""

    HUNGER = "hunger"
    HYGIENE = "hygiene"
    HAPPINESS = "happiness"
    ENERGY = "energy"
    AFFECTION = "affection"
    HEALTH = "health"


class PetStats(BaseModel):
    """Pet statistics and status."""

    hunger: float = Field(default=50.0, ge=0.0, le=100.0, description="Hunger level (0-100)")
    hygiene: float = Field(default=50.0, ge=0.0, le=100.0, description="Hygiene level (0-100)")
    happiness: float = Field(default=50.0, ge=0.0, le=100.0, description="Happiness level (0-100)")
    energy: float = Field(default=50.0, ge=0.0, le=100.0, description="Energy level (0-100)")
    affection: float = Field(default=50.0, ge=0.0, le=100.0, description="Affection level (0-100)")
    health: float = Field(default=100.0, ge=0.0, le=100.0, description="Health level (0-100)")
    sleeping: bool = Field(default=False, description="Whether the pet is sleeping")

    @field_validator("hunger", "hygiene", "happiness", "energy", "affection", "health")
    @classmethod
    def clamp_stat(cls, v: float) -> float:
        """Ensure stats stay within 0-100 range."""
        return max(0.0, min(100.0, v))

    def to_dict(self) -> dict[str, float]:
        """Convert stats to dictionary for LLM context."""
        return {
            "hunger": self.hunger,
            "hygiene": self.hygiene,
            "happiness": self.happiness,
            "energy": self.energy,
            "affection": self.affection,
            "health": self.health,
            "sleeping": self.sleeping,
        }

    def apply_effects(self, effects: dict[str, float]) -> None:
        """Apply stat changes from items or actions."""
        for stat_name, change in effects.items():
            if hasattr(self, stat_name):
                current_value = getattr(self, stat_name)
                if isinstance(current_value, bool):
                    continue  # Skip boolean stats like sleeping
                new_value = max(0.0, min(100.0, current_value + change))
                setattr(self, stat_name, new_value)


class GameEvent(BaseModel):
    """Represents a game event for logging and LLM context."""

    timestamp: datetime = Field(default_factory=datetime.now)
    event_type: str = Field(..., description="Type of event (command, decay, etc.)")
    description: str = Field(..., description="Human-readable event description")
    data: dict[str, Any] | None = Field(default=None, description="Additional event data")

    def __str__(self) -> str:
        return f"[{self.timestamp.strftime('%H:%M')}] {self.description}"


class ItemDefinition(BaseModel):
    """Definition of an item that can be used with commands."""

    name: str = Field(..., description="Display name of the item")
    description: str = Field(..., description="Description of the item")
    effects: dict[str, float] = Field(
        default_factory=dict, description="Stat effects when using this item"
    )
    cooldown_s: int = Field(default=300, description="Cooldown in seconds before reuse")


class GameConfig(BaseModel):
    """Game configuration and settings."""

    # Decay rates (per tick, every 60 seconds)
    hunger_decay: float = Field(default=1.0, description="Hunger decay per tick")
    hygiene_decay: float = Field(default=0.5, description="Hygiene decay per tick")
    energy_decay_awake: float = Field(default=0.5, description="Energy decay when awake")
    energy_recovery_sleeping: float = Field(
        default=1.0, description="Energy recovery when sleeping"
    )

    # Thresholds for negative effects
    low_hunger_threshold: float = Field(
        default=40.0, description="Hunger threshold for mood effects"
    )
    low_hygiene_threshold: float = Field(
        default=40.0, description="Hygiene threshold for mood effects"
    )
    critical_hunger_threshold: float = Field(
        default=20.0, description="Critical hunger for sickness"
    )
    critical_hygiene_threshold: float = Field(
        default=20.0, description="Critical hygiene for sickness"
    )
    critical_energy_threshold: float = Field(
        default=10.0, description="Critical energy for sickness"
    )

    # Game mechanics
    mood_decay_rate: float = Field(default=0.2, description="Mood decay when needs are low")
    sickness_chance: float = Field(default=0.05, description="Chance of getting sick when critical")
    health_loss_sick: float = Field(default=3.0, description="Health loss when sick")

    # Autosave and UI
    autosave_interval_s: int = Field(default=30, description="Autosave interval in seconds")
    tick_interval_s: int = Field(default=60, description="Game tick interval in seconds")
    max_chat_history: int = Field(default=200, description="Maximum chat log entries")
    max_events_history: int = Field(default=50, description="Maximum event history")
    max_notifications: int = Field(default=5, description="Maximum notifications displayed")

    # Animation settings
    animation_fps: int = Field(default=8, description="Animation frames per second")
    animation_duration_ms: int = Field(
        default=700, description="Animation duration in milliseconds"
    )


class GameState(BaseModel):
    """Complete game state for saving and loading."""

    stats: PetStats = Field(default_factory=PetStats)
    events: list[GameEvent] = Field(default_factory=list)
    chat_history: list[dict[str, str]] = Field(default_factory=list)
    notifications: list[str] = Field(default_factory=list)
    item_cooldowns: dict[str, datetime] = Field(default_factory=dict)
    last_tick: datetime = Field(default_factory=datetime.now)
    created_at: datetime = Field(default_factory=datetime.now)
    total_play_time_s: float = Field(default=0.0)

    def add_event(
        self, event_type: str, description: str, data: dict[str, Any] | None = None
    ) -> None:
        """Add a new event to the game history."""
        event = GameEvent(event_type=event_type, description=description, data=data)
        self.events.append(event)

        # Keep events list size manageable
        if len(self.events) > 100:
            self.events = self.events[-50:]

    def add_chat_message(self, sender: str, message: str) -> None:
        """Add a chat message to the history."""
        self.chat_history.append(
            {"sender": sender, "message": message, "timestamp": datetime.now().isoformat()}
        )

        # Keep chat history size manageable
        if len(self.chat_history) > 200:
            self.chat_history = self.chat_history[-100:]

    def add_notification(self, message: str) -> None:
        """Add a notification message."""
        self.notifications.append(message)

        # Keep only recent notifications
        if len(self.notifications) > 10:
            self.notifications = self.notifications[-5:]

    def is_item_on_cooldown(self, item_id: str, cooldown_s: int) -> bool:
        """Check if an item is on cooldown."""
        if item_id not in self.item_cooldowns:
            return False

        time_since_use = datetime.now() - self.item_cooldowns[item_id]
        return time_since_use.total_seconds() < cooldown_s

    def use_item(self, item_id: str) -> None:
        """Mark an item as used (start cooldown)."""
        self.item_cooldowns[item_id] = datetime.now()
