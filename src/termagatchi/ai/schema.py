"""Pydantic models for structured LLM outputs and AI integration."""

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class PetAction(str, Enum):
    """Actions that the pet can perform, each mapped to an animation."""

    SMILE = "SMILE"
    LAUGH = "LAUGH"
    BLUSH = "BLUSH"
    HEART = "HEART"
    WAVE = "WAVE"
    WIGGLE = "WIGGLE"
    JUMP = "JUMP"
    EAT = "EAT"
    CLEAN = "CLEAN"
    PLAY = "PLAY"
    NAP = "NAP"
    SLEEPING = "SLEEPING"
    SAD = "SAD"
    CRY = "CRY"
    SICK = "SICK"
    HEAL = "HEAL"
    CONFUSED = "CONFUSED"
    THINK = "THINK"
    SURPRISED = "SURPRISED"
    THANKS = "THANKS"


class PetReply(BaseModel):
    """Structured response from the LLM representing the pet's reaction."""

    say: str = Field(
        ...,
        description="Short, cute pet-like sentence (≤12 words). Should be playful and endearing.",
        min_length=1,
        max_length=100,
    )
    action: PetAction = Field(
        ..., description="The action/animation the pet should perform in response."
    )

    @field_validator("say")
    @classmethod
    def limit_words(cls, v: str) -> str:
        """Ensure the pet's speech is concise (≤12 words)."""
        if not v or not v.strip():
            return "hi!"

        words = v.strip().split()
        if len(words) > 12:
            return " ".join(words[:12])
        return v.strip()

    @field_validator("action")
    @classmethod
    def validate_action(cls, v):
        """Ensure the action is a valid PetAction."""
        if isinstance(v, str):
            try:
                return PetAction(v.upper())
            except ValueError:
                return PetAction.SMILE  # Default fallback
        return v


class GameContext(BaseModel):
    """Context information passed to the LLM for generating responses."""

    stats: dict[str, float] = Field(
        ..., description="Current pet stats (hunger, happiness, energy, etc.)"
    )
    recent_events: list[str] = Field(
        default_factory=list, description="Recent game events and user actions"
    )
    last_user_input: str = Field(default="", description="The user's last input or command")
    time_of_day: str = Field(
        default="day", description="Current time context (morning, day, evening, night)"
    )
    pet_name: str = Field(default="Termagatchi", description="The pet's name")


class LLMConfig(BaseModel):
    """Configuration for LLM provider and model."""

    provider: str = Field(
        default="deterministic",
        description="LLM provider (openai, anthropic, google, ollama, etc.)",
    )
    model: str = Field(default="gpt-4o-mini", description="Model name for the selected provider")
    timeout_s: int = Field(default=4, description="Request timeout in seconds")
    max_retries: int = Field(default=2, description="Maximum number of retry attempts")
    temperature: float = Field(default=0.7, description="LLM temperature for response creativity")
    max_tokens: int = Field(default=64, description="Maximum tokens in LLM response")
