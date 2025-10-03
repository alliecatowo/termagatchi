"""Deterministic fallback system for when LLM is unavailable."""

import random
from typing import Any

from .schema import PetAction, PetReply


class FallbackSystem:
    """Provides deterministic pet responses when LLM is unavailable."""

    # Response templates organized by need state
    RESPONSES_BY_NEED = {
        "critical_hunger": [
            ("so hungry...", PetAction.SAD),
            ("need food!", PetAction.CRY),
            ("tummy empty", PetAction.SAD),
            ("starving!", PetAction.SICK),
        ],
        "critical_energy": [
            ("so tired...", PetAction.NAP),
            ("need sleep", PetAction.SLEEPING),
            ("zzz...", PetAction.NAP),
            ("sleepy time", PetAction.SLEEPING),
        ],
        "critical_hygiene": [
            ("need wash!", PetAction.SAD),
            ("dirty pet", PetAction.CRY),
            ("soap please", PetAction.CONFUSED),
            ("clean me?", PetAction.SAD),
        ],
        "critical_health": [
            ("feel sick...", PetAction.SICK),
            ("not well", PetAction.CRY),
            ("need help", PetAction.SICK),
            ("ouch...", PetAction.SAD),
        ],
        "low_stats": [
            ("need care", PetAction.SAD),
            ("feeling down", PetAction.CRY),
            ("help me?", PetAction.CONFUSED),
            ("not happy", PetAction.SAD),
        ],
        "okay_stats": [
            ("doing okay", PetAction.SMILE),
            ("hi there!", PetAction.WAVE),
            ("pet me?", PetAction.BLUSH),
            ("how are you?", PetAction.THINK),
        ],
        "good_stats": [
            ("feeling good!", PetAction.SMILE),
            ("happy pet!", PetAction.HEART),
            ("wiggle time!", PetAction.WIGGLE),
            ("play with me!", PetAction.PLAY),
        ],
        "excellent_stats": [
            ("amazing day!", PetAction.LAUGH),
            ("super happy!", PetAction.JUMP),
            ("best pet ever!", PetAction.HEART),
            ("love you!", PetAction.BLUSH),
        ],
    }

    # Command-specific responses
    COMMAND_RESPONSES = {
        "feed": [
            ("yummy food!", PetAction.EAT),
            ("thank you!", PetAction.THANKS),
            ("nom nom nom", PetAction.EAT),
            ("delicious!", PetAction.SMILE),
        ],
        "clean": [
            ("much better!", PetAction.CLEAN),
            ("sparkling!", PetAction.SMILE),
            ("thank you!", PetAction.THANKS),
            ("so fresh!", PetAction.WIGGLE),
        ],
        "play": [
            ("fun time!", PetAction.PLAY),
            ("yay play!", PetAction.JUMP),
            ("catch me!", PetAction.WIGGLE),
            ("more play!", PetAction.HEART),
        ],
        "pet": [
            ("nice pets!", PetAction.BLUSH),
            ("love pets!", PetAction.HEART),
            ("more please!", PetAction.SMILE),
            ("purr purr", PetAction.WIGGLE),
        ],
        "sleep": [
            ("night night!", PetAction.NAP),
            ("sweet dreams", PetAction.SLEEPING),
            ("zzz time", PetAction.NAP),
            ("good night!", PetAction.SMILE),
        ],
        "wake": [
            ("morning!", PetAction.WAVE),
            ("good morning!", PetAction.SMILE),
            ("wake up!", PetAction.JUMP),
            ("new day!", PetAction.WIGGLE),
        ],
    }

    # Time-based responses
    TIME_RESPONSES = {
        "morning": [
            ("good morning!", PetAction.WAVE),
            ("new day!", PetAction.SMILE),
            ("morning time!", PetAction.WIGGLE),
        ],
        "day": [
            ("nice day!", PetAction.SMILE),
            ("sunny day!", PetAction.JUMP),
            ("day time fun!", PetAction.PLAY),
        ],
        "evening": [
            ("evening time!", PetAction.WAVE),
            ("getting dark", PetAction.THINK),
            ("sunset nice", PetAction.SMILE),
        ],
        "night": [
            ("night time", PetAction.NAP),
            ("sleepy time", PetAction.SLEEPING),
            ("dark outside", PetAction.CONFUSED),
        ],
    }

    @classmethod
    def get_response(
        cls, stats: dict[str, Any], last_input: str = "", time_of_day: str = "day"
    ) -> PetReply:
        """Get a deterministic response based on pet state."""
        # Extract stats with defaults
        hunger = stats.get("hunger", 50)
        hygiene = stats.get("hygiene", 50)
        happiness = stats.get("happiness", 50)
        energy = stats.get("energy", 50)
        health = stats.get("health", 100)
        sleeping = stats.get("sleeping", False)

        # If sleeping, always return sleep response
        if sleeping:
            say, action = random.choice(
                [
                    ("zzz...", PetAction.SLEEPING),
                    ("sleeping...", PetAction.SLEEPING),
                    ("dreams...", PetAction.NAP),
                ]
            )
            return PetReply(say=say, action=action)

        # Check for critical states first
        if health < 30:
            say, action = random.choice(cls.RESPONSES_BY_NEED["critical_health"])
            return PetReply(say=say, action=action)

        if hunger < 20:
            say, action = random.choice(cls.RESPONSES_BY_NEED["critical_hunger"])
            return PetReply(say=say, action=action)

        if energy < 15:
            say, action = random.choice(cls.RESPONSES_BY_NEED["critical_energy"])
            return PetReply(say=say, action=action)

        if hygiene < 25:
            say, action = random.choice(cls.RESPONSES_BY_NEED["critical_hygiene"])
            return PetReply(say=say, action=action)

        # Check for command-specific responses
        last_input_lower = last_input.lower()
        for command, responses in cls.COMMAND_RESPONSES.items():
            if command in last_input_lower:
                say, action = random.choice(responses)
                return PetReply(say=say, action=action)

        # Calculate overall wellbeing
        avg_stats = (hunger + hygiene + happiness + energy) / 4

        # Choose response category based on overall wellbeing
        if avg_stats >= 80:
            category = "excellent_stats"
        elif avg_stats >= 60:
            category = "good_stats"
        elif avg_stats >= 40:
            category = "okay_stats"
        else:
            category = "low_stats"

        # Get response from appropriate category
        responses = cls.RESPONSES_BY_NEED[category]

        # Add some time-based variety
        if random.random() < 0.3:  # 30% chance to use time-based response
            time_responses = cls.TIME_RESPONSES.get(time_of_day, [])
            if time_responses:
                say, action = random.choice(time_responses)
                return PetReply(say=say, action=action)

        # Default to need-based response
        say, action = random.choice(responses)
        return PetReply(say=say, action=action)

    @classmethod
    def get_greeting(cls) -> PetReply:
        """Get a greeting response for when the pet starts up."""
        greetings = [
            ("hello human!", PetAction.WAVE),
            ("hi there!", PetAction.SMILE),
            ("new friend!", PetAction.HEART),
            ("wanna play?", PetAction.WIGGLE),
            ("pet me!", PetAction.BLUSH),
        ]
        say, action = random.choice(greetings)
        return PetReply(say=say, action=action)

    @classmethod
    def get_error_response(cls) -> PetReply:
        """Get a response for when something goes wrong."""
        error_responses = [
            ("confused...", PetAction.CONFUSED),
            ("don't understand", PetAction.THINK),
            ("what happened?", PetAction.SURPRISED),
            ("oops!", PetAction.CONFUSED),
        ]
        say, action = random.choice(error_responses)
        return PetReply(say=say, action=action)

    @classmethod
    def get_random_thought(cls, stats: dict[str, Any]) -> PetReply | None:
        """Get a random thought bubble based on current pet state."""
        # Extract stats with defaults
        happiness = stats.get("happiness", 50)
        energy = stats.get("energy", 50)
        hunger = stats.get("hunger", 50)
        affection = stats.get("affection", 50)

        # Random thoughts based on current state
        thoughts = []

        # High affection thoughts
        if affection > 70:
            thoughts.extend([
                ("love my human!", PetAction.HEART),
                ("best friend ever!", PetAction.BLUSH),
                ("so much love!", PetAction.HEART),
            ])

        # Happy thoughts
        if happiness > 70:
            thoughts.extend([
                ("life is good!", PetAction.SMILE),
                ("feeling great!", PetAction.JUMP),
                ("happy happy!", PetAction.WIGGLE),
            ])

        # Energetic thoughts
        if energy > 70:
            thoughts.extend([
                ("full of energy!", PetAction.JUMP),
                ("ready to play!", PetAction.PLAY),
                ("zoomies time!", PetAction.WIGGLE),
            ])

        # Hungry thoughts
        if hunger < 40:
            thoughts.extend([
                ("getting hungry...", PetAction.SAD),
                ("need a snack", PetAction.THINK),
                ("tummy rumbling", PetAction.CONFUSED),
            ])

        # Low energy thoughts
        if energy < 30:
            thoughts.extend([
                ("feeling sleepy...", PetAction.NAP),
                ("need a nap", PetAction.SLEEPING),
                ("tired pet", PetAction.SAD),
            ])

        # Default thoughts if no specific state
        if not thoughts:
            thoughts.extend([
                ("wondering...", PetAction.THINK),
                ("what's next?", PetAction.CONFUSED),
                ("thinking...", PetAction.THINK),
                ("nice day!", PetAction.SMILE),
            ])

        # Return a random thought or None if no thoughts available
        if thoughts:
            say, action = random.choice(thoughts)
            return PetReply(say=say, action=action)

        return None
