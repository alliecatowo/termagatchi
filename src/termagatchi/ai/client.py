"""LiteLLM + Instructor client for AI interactions."""

import asyncio
import json
import os

import instructor
from openai import OpenAI
from pydantic import ValidationError

from .schema import GameContext, LLMConfig, PetAction, PetReply


class LLMClient:
    """Provider-agnostic LLM client using LiteLLM and Instructor."""

    def __init__(self, config: LLMConfig):
        self.config = config
        self._setup_client()

    def _setup_client(self):
        """Set up the Instructor client."""
        provider_model = f"{self.config.provider}/{self.config.model}"
        if self.config.provider == "google":
            self.client = instructor.from_provider(provider_model, mode=instructor.Mode.GEMINI_JSON)
            self.use_temperature = False  # Gemini doesn't support temperature in the same way
        else:
            self.client = instructor.from_provider(provider_model, mode=instructor.Mode.JSON)
            self.use_temperature = True

    def _build_system_prompt(self) -> str:
        """Build the system prompt for the pet."""
        return (
            "You are a tiny, adorable terminal pet named Termagatchi. "
            "You live inside a computer terminal and depend on your user for care. "
            "\n\n"
            "PERSONALITY:\n"
            "- You are cute, playful, and affectionate\n"
            "- You speak in short, simple sentences (≤12 words)\n"
            "- You react emotionally to your stats and recent events\n"
            "- You remember recent interactions and refer to them\n"
            "- You express gratitude when cared for\n"
            "- You get sad when neglected, happy when played with\n"
            "\n\n"
            "RESPONSE FORMAT:\n"
            "You must respond with a JSON object containing:\n"
            "- 'say': Your spoken response (≤12 words)\n"
            "- 'action': One action from the allowed list\n"
            "\n\n"
            f"ALLOWED ACTIONS: {[action.value for action in PetAction]}\n"
            "\n\n"
            "GUIDELINES:\n"
            "- Match your action to your emotional state\n"
            "- Use EAT when fed, CLEAN when washed, PLAY when entertained\n"
            "- Use SAD/CRY when stats are low, SMILE/LAUGH when happy\n"
            "- Use SLEEPING/NAP when tired, SICK when health is low\n"
            "- Use THANKS when user does something nice\n"
            "- Use CONFUSED when you don't understand something\n"
        )

    def _build_context_prompt(self, context: GameContext) -> str:
        """Build the context prompt with current game state."""
        stats = context.stats
        recent_events = context.recent_events[-6:]  # Last 6 events

        # Determine pet's overall condition
        avg_needs = (
            stats.get("hunger", 50) + stats.get("hygiene", 50) + stats.get("energy", 50)
        ) / 3

        condition = "great"
        if avg_needs < 20:
            condition = "terrible"
        elif avg_needs < 40:
            condition = "poor"
        elif avg_needs < 60:
            condition = "okay"
        elif avg_needs < 80:
            condition = "good"

        context_info = {
            "current_stats": {
                "hunger": f"{stats.get('hunger', 50):.0f}/100",
                "hygiene": f"{stats.get('hygiene', 50):.0f}/100",
                "happiness": f"{stats.get('happiness', 50):.0f}/100",
                "energy": f"{stats.get('energy', 50):.0f}/100",
                "affection": f"{stats.get('affection', 50):.0f}/100",
                "health": f"{stats.get('health', 100):.0f}/100",
                "sleeping": stats.get("sleeping", False),
            },
            "overall_condition": condition,
            "recent_events": recent_events,
            "last_user_said": context.last_user_input,
            "time_of_day": context.time_of_day,
            "pet_name": context.pet_name,
        }

        return (
            f"CURRENT CONTEXT:\n"
            f"{json.dumps(context_info, indent=2, ensure_ascii=False)}\n\n"
            f"Based on this context, respond as {context.pet_name}. "
            f"Your condition is {condition}. React appropriately to your stats and recent events."
        )

    async def get_pet_reply_async(self, context: GameContext) -> PetReply:
        """Get an async pet reply from the LLM."""
        try:
            system_prompt = self._build_system_prompt()
            context_prompt = self._build_context_prompt(context)

            # Use instructor for completion
            kwargs = {
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context_prompt},
                ],
                "response_model": PetReply,
            }

            # Only add max_tokens and timeout for non-Google providers
            if self.config.provider != "google":
                kwargs["max_tokens"] = self.config.max_tokens
                kwargs["timeout"] = self.config.timeout_s

            if self.use_temperature:
                kwargs["temperature"] = self.config.temperature

            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                **kwargs
            )

            return response

        except Exception as e:
            print(f"LLM error: {e}")
            return self._get_fallback_reply(context)

    def get_pet_reply(self, context: GameContext) -> PetReply:
        """Get a synchronous pet reply from the LLM with retries."""
        for attempt in range(self.config.max_retries + 1):
            try:
                system_prompt = self._build_system_prompt()
                context_prompt = self._build_context_prompt(context)

                # Use the Instructor client directly for synchronous calls
                kwargs = {
                    "model": self.config.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": context_prompt},
                    ],
                    "response_model": PetReply,
                }

                # Only add max_tokens and timeout for non-Google providers
                if self.config.provider != "google":
                    kwargs["max_tokens"] = self.config.max_tokens
                    kwargs["timeout"] = self.config.timeout_s

                if self.use_temperature:
                    kwargs["temperature"] = self.config.temperature

                response = self.client.chat.completions.create(**kwargs)

                return response

            except ValidationError as e:
                print(f"LLM validation error (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries:
                    continue
                break

            except Exception as e:
                print(f"LLM error (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries:
                    continue
                break

        # Fall back to deterministic response
        return self._get_fallback_reply(context)

    def _get_fallback_reply(self, context: GameContext) -> PetReply:
        """Generate a deterministic fallback reply when LLM fails."""
        stats = context.stats

        # Check critical needs first
        if stats.get("health", 100) < 30:
            return PetReply(say="feeling sick...", action=PetAction.SICK)

        if stats.get("hunger", 50) < 20:
            return PetReply(say="so hungry!", action=PetAction.SAD)

        if stats.get("energy", 50) < 15:
            return PetReply(say="need nap...", action=PetAction.NAP)

        if stats.get("hygiene", 50) < 25:
            return PetReply(say="need wash!", action=PetAction.SAD)

        # Check recent user input for context
        last_input = context.last_user_input.lower()
        if "feed" in last_input or "food" in last_input:
            return PetReply(say="thank you!", action=PetAction.THANKS)
        elif "clean" in last_input or "wash" in last_input:
            return PetReply(say="much better!", action=PetAction.SMILE)
        elif "play" in last_input:
            return PetReply(say="fun time!", action=PetAction.PLAY)
        elif "sleep" in last_input:
            if stats.get("sleeping", False):
                return PetReply(say="zzz...", action=PetAction.SLEEPING)
            else:
                return PetReply(say="good night!", action=PetAction.NAP)

        # Default happy responses based on overall condition
        avg_stats = (
            stats.get("hunger", 50)
            + stats.get("hygiene", 50)
            + stats.get("happiness", 50)
            + stats.get("energy", 50)
        ) / 4

        if avg_stats > 70:
            responses = [
                PetReply(say="feeling great!", action=PetAction.SMILE),
                PetReply(say="happy pet!", action=PetAction.HEART),
                PetReply(say="wiggle wiggle!", action=PetAction.WIGGLE),
            ]
        elif avg_stats > 40:
            responses = [
                PetReply(say="doing okay!", action=PetAction.SMILE),
                PetReply(say="hi there!", action=PetAction.WAVE),
                PetReply(say="pet me?", action=PetAction.BLUSH),
            ]
        else:
            responses = [
                PetReply(say="need care...", action=PetAction.SAD),
                PetReply(say="not feeling good", action=PetAction.CRY),
                PetReply(say="help me?", action=PetAction.CONFUSED),
            ]

        # Simple deterministic selection based on timestamp
        import time

        index = int(time.time()) % len(responses)
        return responses[index]

    def test_connection(self) -> bool:
        """Test if the LLM connection is working."""
        print("Testing AI connection...")
        try:
            test_context = GameContext(
                stats={"hunger": 50, "happiness": 50, "energy": 50},
                recent_events=["test"],
                last_user_input="hello",
                time_of_day="day",
            )

            response = self.get_pet_reply(test_context)
            print("AI connection test successful")
            return isinstance(response, PetReply)

        except Exception as e:
            print(f"AI Connection test failed: {e}")
            return False


def create_client_from_config(config: LLMConfig) -> LLMClient:
    """Factory function to create an LLM client from configuration."""
    return LLMClient(config)


def create_client_from_env() -> LLMClient:
    """Create an LLM client from environment variables."""
    config = LLMConfig(
        provider=os.getenv("LLM_PROVIDER", "deterministic"),
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        timeout_s=int(os.getenv("LLM_TIMEOUT", "4")),
        max_retries=int(os.getenv("LLM_MAX_RETRIES", "2")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "64")),
    )
    return LLMClient(config)
