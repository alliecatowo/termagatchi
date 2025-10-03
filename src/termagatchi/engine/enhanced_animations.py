"""Enhanced animation system for dynamic, expressive pet animations."""

import asyncio
import random
import textwrap
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

from ..ai.schema import PetAction


class CreatureExpression(Enum):
    """Different facial expressions for the creature."""
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    SLEEPY = "sleepy"
    SURPRISED = "surprised"
    ANGRY = "angry"
    CONFUSED = "confused"
    LOVING = "loving"


class CreaturePose(Enum):
    """Different body poses for the creature."""
    STANDING = "standing"
    SITTING = "sitting"
    LYING_DOWN = "lying_down"
    JUMPING = "jumping"
    DANCING = "dancing"
    WALKING = "walking"
    BOUNCING = "bouncing"
    EATING = "eating"


class ParticleType(Enum):
    """Types of particle effects."""
    HEARTS = "hearts"
    SPARKLES = "sparkles"
    RAIN_CLOUD = "rain_cloud"
    LIGHTNING = "lightning"
    SLEEP_ZZ = "sleep_zz"
    FOOD_CRUMBS = "food_crumbs"
    STARS = "stars"
    TEARS = "tears"


@dataclass
class Particle:
    """A single particle in an effect."""
    symbol: str
    x: int
    y: int
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    life: float = 1.0
    decay: float = 0.1


@dataclass
class AnimationLayer:
    """A single layer of animation (background, creature, effects, etc.)."""
    content: str
    x_offset: int = 0
    y_offset: int = 0
    layer_type: str = "creature"  # creature, background, effects, items


@dataclass
class EnhancedAnimationFrame:
    """An enhanced animation frame with multiple layers and effects."""
    layers: List[AnimationLayer]
    particles: List[Particle]
    duration_ms: int = 100


class DynamicCreatureRenderer:
    """Renders dynamic creature animations with expressions and poses."""

    # Face expressions - mapped to individual facial features so templates can stay aligned
    EXPRESSIONS = {
        CreatureExpression.HAPPY: {
            "left_eye": "◕‿◕",
            "right_eye": "◕‿◕",
            "nose": "•",
            "mouth_line": "◡‿◡",
            "whisker_left": "≋",
            "whisker_right": "≋",
            "cheek_left": "❀",
            "cheek_right": "❀",
        },
        CreatureExpression.SAD: {
            "left_eye": "◕︵◕",
            "right_eye": "◕︵◕",
            "nose": "•",
            "mouth_line": "︵︵︵",
            "whisker_left": "≋",
            "whisker_right": "≋",
            "cheek_left": "😢",
            "cheek_right": "😢",
        },
        CreatureExpression.EXCITED: {
            "left_eye": "✨◡✨",
            "right_eye": "✨◡✨",
            "nose": "•",
            "mouth_line": "◕‿◕",
            "whisker_left": "≋",
            "whisker_right": "≋",
            "cheek_left": "❀",
            "cheek_right": "❀",
        },
        CreatureExpression.SLEEPY: {
            "left_eye": "◡◡",
            "right_eye": "◡◡",
            "nose": "•",
            "mouth_line": "◡◡◡",
            "whisker_left": "~",
            "whisker_right": "~",
            "cheek_left": "💤",
            "cheek_right": "💤",
        },
        CreatureExpression.SURPRISED: {
            "left_eye": "⊙⊙",
            "right_eye": "⊙⊙",
            "nose": "•",
            "mouth_line": "⊙⊙⊙",
            "whisker_left": "≋",
            "whisker_right": "≋",
            "cheek_left": "😮",
            "cheek_right": "😮",
        },
        CreatureExpression.ANGRY: {
            "left_eye": "ಠ益ಠ",
            "right_eye": "ಠ益ಠ",
            "nose": "•",
            "mouth_line": "ಠ_ಠ",
            "whisker_left": "≋",
            "whisker_right": "≋",
            "cheek_left": "💢",
            "cheek_right": "💢",
        },
        CreatureExpression.CONFUSED: {
            "left_eye": "◐‿◑",
            "right_eye": "◐‿◑",
            "nose": "•",
            "mouth_line": "◔‿◕",
            "whisker_left": "~",
            "whisker_right": "≋",
            "cheek_left": "😕",
            "cheek_right": "😕",
        },
        CreatureExpression.LOVING: {
            "left_eye": "♥‿♥",
            "right_eye": "♥‿♥",
            "nose": "♡",
            "mouth_line": "♥‿♥",
            "whisker_left": "≋",
            "whisker_right": "≋",
            "cheek_left": "💕",
            "cheek_right": "💕",
        },
    }

    # Base creature templates for different poses - designed to look like a chinchilla
    CREATURE_TEMPLATES = {
        CreaturePose.STANDING: textwrap.dedent(
            """
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣖⣶⣶⣦⣄⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡿⣏⡝⠛⠯⢿⣯⣆⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⠏⠀⠀⠀⠙⡟⣿⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠤⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠖⠲⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢏⡟⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠉⢆⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠁⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⣴⠾⠛⠋⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⣶⡄⠀⠀⠱⡀⢾⠛⢦⣶⠛⣧⠀⡇⠀⠀⠀⡤⡲⣅⡇⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠘⣿⣿⢦⠀⠀⠁⠘⠳⢾⣿⠾⠟⠙⠀⠀⢀⣯⣟⣬⠏⠀⠀⠀⠀⠈⠛⠃⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠙⡿⠁⠁⠀⠀⠀⠠⠟⠋⠛⠆⠀⠀⠀⠀⠻⡿⠵⠀⠀⠀⠀⠀⢿⣦⡄⣯⣷
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠃⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⢠⣤⡀⠀⠈⠧⡄⠀⠀⠀⠀⠀⠈⠛⡛⠁
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠁⠀⠀⠀⣿⡏⢳⠀⠀⠀⠀⠀⠀⣿⡍⢹⠀⠀⠀⠙⡄
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠀⢀⢀⠈⠛⠇⠀⠀⠠⣤⠀⠀⠈⠙⠃⢀⡀⠀⣸
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠙⠉⠀⠀⠀⠀⠀⠴⠋⠙⠦⠀⠀⠀⠀⢉⡥⠋
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡹⢲⡤⠤⢄⣀⣀⣀⣀⣀⣠⠤⠖⢋⣅⡀
                  ⠀⠀⠀⠀⠀⣠⠞⠉⠉⠉⠳⡄⡠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠆
                  ⠀⠀⠀⢠⠏⠀⢀⣀⣤⡀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠒⢦⡄⠀⠀⠀⠀⠀⠀⣴⡍⠀⠀⠀⢳
                  ⠀⠀⢠⠇⠀⢸⠁⠀⠀⠈⡇⡸⠀⠀⠀⠀⠀⠀⠀⠀⠉⢯⣧⠶⠚⠛⢧⡟⠀⠀⠀⠀⠀⠘⡄
                  ⠀⠀⢸⠀⠀⠸⡀⠀⠙⠋⠁⢯⠀⠀⠀⠀⠀⠀⠲⣄⣀⣠⡇⠀⠀⠀⠘⣧⣄⣀⡤⠀⠀⡇
                  ⠀⠀⠘⡄⠀⠀⠑⠦⣄⣀⡤⢼⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⣧⠀⠀⠀⢀⡴⠈⠉⠁⠀⠀⠀⠇
                  ⠀⠀⠀⠱⡄⠀⠀⠀⠀⠀⠀⠀⢨⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠋⠁
                  ⠀⠀⠀⠀⠉⠣⡄⠀⠀⠀⠀⠀⠀⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀
                  ⠀⠀⠀⠀⠀⠀⠈⠉⠢⠤⠤⠤⠖⠋⠉⢀⡀⠀⠀⠀⠀⠀⠀⠀⡇⠀⡤
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠒⠒⠒⠒⠋⠈⠁⠉⠓⠒⠒⠒⠉⠁
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            """
        ).strip(),

        CreaturePose.SITTING: textwrap.dedent(
            """
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣖⣶⣶⣦⣄⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡿⣏⡝⠛⠯⢿⣯⣆⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⠏⠀⠀⠀⠙⡟⣿⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠤⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠖⠲⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢏⡟⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠉⢆⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠁⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⣴⠾⠛⠋⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⣶⡄⠀⠀⠱⡀⢾⠛⢦⣶⠛⣧⠀⡇⠀⠀⠀⡤⡲⣅⡇⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠘⣿⣿⢦⠀⠀⠁⠘⠳⢾⣿⠾⠟⠙⠀⠀⢀⣯⣟⣬⠏⠀⠀⠀⠀⠈⠛⠃⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠙⡿⠁⠁⠀⠀⠀⠠⠟⠋⠛⠆⠀⠀⠀⠀⠻⡿⠵⠀⠀⠀⠀⠀⢿⣦⡄⣯⣷
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠃⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⢠⣤⡀⠀⠈⠧⡄
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠁⠀⠀⠀⣿⡏⢳⠀⠀⠀⠀⠀⠀⣿⡍⢹
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠀⢀⢀⠈⠛⠇⠀⠀⠠⣤⠀⠀⠈⠙⠃⢀⡀⠀⣸
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠙⠉⠀⠀⠀⠀⠀⠴⠋⠙⠦⠀⠀⠀⠀⢉⡥⠋
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡹⢲⡤⠤⢄⣀⣀⣀⣀⣀⣠⠤⠖⢋⣅⡀
                  ⠀⠀⠀⠀⠀⣠⠞⠉⠉⠉⠳⡄⡠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠆
                  ⠀⠀⠀⢠⠏⠀⢀⣀⣤⡀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠒⢦⡄⠀⠀⠀⠀⠀⠀⣴⡍⠀⠀⠀⢳
                  ⠀⠀⢠⠇⠀⢸⠁⠀⠀⠈⡇⡸⠀⠀⠀⠀⠀⠀⠀⠀⠉⢯⣧⠶⠚⠛⢧⡟⠀⠀⠀⠀⠀⠘⡄
                  ⠀⠀⢸⠀⠀⠸⡀⠀⠙⠋⠁⢯⠀⠀⠀⠀⠀⠀⠲⣄⣀⣠⡇⠀⠀⠀⠘⣧⣄⣀⡤⠀⠀⡇
                  ⠀⠀⠘⡄⠀⠀⠑⠦⣄⣀⡤⢼⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⣧⠀⠀⠀⢀⡴⠈⠉⠁⠀⠀⠀⠇
                  ⠀⠀⠀⠱⡄⠀⠀⠀⠀⠀⠀⠀⢨⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠋⠁
                  ⠀⠀⠀⠀⠉⠣⡄⠀⠀⠀⠀⠀⠀⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀
                  ⠀⠀⠀⠀⠀⠀⠈⠉⠢⠤⠤⠤⠖⠋⠉⢀⡀⠀⠀⠀⠀⠀⠀⠀⡇⠀⡤
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠒⠒⠒⠒⠋⠈⠁⠉⠓⠒⠒⠒⠉⠁
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            """
        ).strip(),

        CreaturePose.JUMPING: textwrap.dedent(
            """
                    ✧    ✧
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣖⣶⣶⣦⣄⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡿⣏⡝⠛⠯⢿⣯⣆⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⠏⠀⠀⠀⠙⡟⣿⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠤⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠖⠲⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢏⡟⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠉⢆⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠁⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⣴⠾⠛⠋⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⣶⡄⠀⠀⠱⡀⢾⠛⢦⣶⠛⣧⠀⡇⠀⠀⠀⡤⡲⣅⡇⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠘⣿⣿⢦⠀⠀⠁⠘⠳⢾⣿⠾⠟⠙⠀⠀⢀⣯⣟⣬⠏⠀⠀⠀⠀⠈⠛⠃⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠙⡿⠁⠁⠀⠀⠀⠠⠟⠋⠛⠆⠀⠀⠀⠀⠻⡿⠵⠀⠀⠀⠀⠀⢿⣦⡄⣯⣷
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠃⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⢠⣤⡀⠀⠈⠧⡄
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠁⠀⠀⠀⣿⡏⢳⠀⠀⠀⠀⠀⠀⣿⡍⢹
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠀⢀⢀⠈⠛⠇⠀⠀⠠⣤⠀⠀⠈⠙⠃⢀⡀⠀⣸
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠙⠉⠀⠀⠀⠀⠀⠴⠋⠙⠦⠀⠀⠀⠀⢉⡥⠋
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡹⢲⡤⠤⢄⣀⣀⣀⣀⣀⣠⠤⠖⢋⣅⡀
                  ⠀⠀⠀⠀⠀⣠⠞⠉⠉⠉⠳⡄⡠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠆
                  ⠀⠀⠀⢠⠏⠀⢀⣀⣤⡀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠒⢦⡄⠀⠀⠀⠀⠀⠀⣴⡍⠀⠀⠀⢳
                  ⠀⠀⢠⠇⠀⢸⠁⠀⠀⠈⡇⡸⠀⠀⠀⠀⠀⠀⠀⠀⠉⢯⣧⠶⠚⠛⢧⡟⠀⠀⠀⠀⠀⠘⡄
                  ⠀⠀⢸⠀⠀⠸⡀⠀⠙⠋⠁⢯⠀⠀⠀⠀⠀⠀⠲⣄⣀⣠⡇⠀⠀⠀⠘⣧⣄⣀⡤⠀⠀⡇
                  ⠀⠀⠘⡄⠀⠀⠑⠦⣄⣀⡤⢼⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⣧⠀⠀⠀⢀⡴⠈⠉⠁⠀⠀⠀⠇
                  ⠀⠀⠀⠱⡄⠀⠀⠀⠀⠀⠀⠀⢨⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠋⠁
                  ⠀⠀⠀⠀⠉⠣⡄⠀⠀⠀⠀⠀⠀⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀
                  ⠀⠀⠀⠀⠀⠀⠈⠉⠢⠤⠤⠤⠖⠋⠉⢀⡀⠀⠀⠀⠀⠀⠀⠀⡇⠀⡤
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠒⠒⠒⠒⠋⠈⠁⠉⠓⠒⠒⠒⠉⠁
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                    ✧         ✧
            """
        ).strip(),

        CreaturePose.DANCING: textwrap.dedent(
            """
                ♪   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ♫
                   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣖⣶⣶⣦⣄⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡿⣏⡝⠛⠯⢿⣯⣆⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⠏⠀⠀⠀⠙⡟⣿⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠤⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠖⠲⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢏⡟⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠉⢆⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠁⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⣴⠾⠛⠋⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⣶⡄⠀⠀⠱⡀⢾⠛⢦⣶⠛⣧⠀⡇⠀⠀⠀⡤⡲⣅⡇⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠘⣿⣿⢦⠀⠀⠁⠘⠳⢾⣿⠾⠟⠙⠀⠀⢀⣯⣟⣬⠏⠀⠀⠀⠀⠈⠛⠃⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠙⡿⠁⠁⠀⠀⠀⠠⠟⠋⠛⠆⠀⠀⠀⠀⠻⡿⠵⠀⠀⠀⠀⠀⢿⣦⡄⣯⣷
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠃⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⢠⣤⡀⠀⠈⠧⡄
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠁⠀⠀⠀⣿⡏⢳⠀⠀⠀⠀⠀⠀⣿⡍⢹
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠀⢀⢀⠈⠛⠇⠀⠀⠠⣤⠀⠀⠈⠙⠃⢀⡀⠀⣸
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠙⠉⠀⠀⠀⠀⠀⠴⠋⠙⠦⠀⠀⠀⠀⢉⡥⠋
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡹⢲⡤⠤⢄⣀⣀⣀⣀⣀⣠⠤⠖⢋⣅⡀
                  ⠀⠀⠀⠀⠀⣠⠞⠉⠉⠉⠳⡄⡠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠆
                  ⠀⠀⠀⢠⠏⠀⢀⣀⣤⡀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠒⢦⡄⠀⠀⠀⠀⠀⠀⣴⡍⠀⠀⠀⢳
                  ⠀⠀⢠⠇⠀⢸⠁⠀⠀⠈⡇⡸⠀⠀⠀⠀⠀⠀⠀⠀⠉⢯⣧⠶⠚⠛⢧⡟⠀⠀⠀⠀⠀⠘⡄
                  ⠀⠀⢸⠀⠀⠸⡀⠀⠙⠋⠁⢯⠀⠀⠀⠀⠀⠀⠲⣄⣀⣠⡇⠀⠀⠀⠘⣧⣄⣀⡤⠀⠀⡇
                  ⠀⠀⠘⡄⠀⠀⠑⠦⣄⣀⡤⢼⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⣧⠀⠀⠀⢀⡴⠈⠉⠁⠀⠀⠀⠇
                  ⠀⠀⠀⠱⡄⠀⠀⠀⠀⠀⠀⠀⢨⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠋⠁
                  ⠀⠀⠀⠀⠉⠣⡄⠀⠀⠀⠀⠀⠀⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀
                  ⠀⠀⠀⠀⠀⠀⠈⠉⠢⠤⠤⠤⠖⠋⠉⢀⡀⠀⠀⠀⠀⠀⠀⠀⡇⠀⡤
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠒⠒⠒⠒⠋⠈⠁⠉⠓⠒⠒⠒⠉⠁
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀
                ♫   ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ♪
            """
        ).strip(),

        CreaturePose.LYING_DOWN: textwrap.dedent(
            """
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣖⣶⣶⣦⣄⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡿⣏⡝⠛⠯⢿⣯⣆⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⠏⠀⠀⠀⠙⡟⣿⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠤⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠖⠲⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢏⡟⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠉⢆⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠁⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⣴⠾⠛⠋⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⣶⡄⠀⠀⠱⡀⢾⠛⢦⣶⠛⣧⠀⡇⠀⠀⠀⡤⡲⣅⡇⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠘⣿⣿⢦⠀⠀⠁⠘⠳⢾⣿⠾⠟⠙⠀⠀⢀⣯⣟⣬⠏⠀⠀⠀⠀⠈⠛⠃⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠙⡿⠁⠁⠀⠀⠀⠠⠟⠋⠛⠆⠀⠀⠀⠀⠻⡿⠵⠀⠀⠀⠀⠀⢿⣦⡄⣯⣷
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠃⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⢠⣤⡀⠀⠈⠧⡄
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠁⠀⠀⠀⣿⡏⢳⠀⠀⠀⠀⠀⠀⣿⡍⢹
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠀⢀⢀⠈⠛⠇⠀⠀⠠⣤⠀⠀⠈⠙⠃⢀⡀⠀⣸
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠙⠉⠀⠀⠀⠀⠀⠴⠋⠙⠦⠀⠀⠀⠀⢉⡥⠋
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡹⢲⡤⠤⢄⣀⣀⣀⣀⣀⣠⠤⠖⢋⣅⡀
            ⠀⠀⠀⠀⠀⣠⠞⠉⠉⠉⠳⡄⡠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠆
            ⠀⠀⠀⢠⠏⠀⢀⣀⣤⡀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠒⢦⡄⠀⠀⠀⠀⠀⠀⣴⡍⠀⠀⠀⢳
            ⠀⠀⢠⠇⠀⢸⠁⠀⠀⠈⡇⡸⠀⠀⠀⠀⠀⠀⠀⠀⠉⢯⣧⠶⠚⠛⢧⡟⠀⠀⠀⠀⠀⠘⡄
            ⠀⠀⢸⠀⠀⠸⡀⠀⠙⠋⠁⢯⠀⠀⠀⠀⠀⠀⠲⣄⣀⣠⡇⠀⠀⠀⠘⣧⣄⣀⡤⠀⠀⡇
            ⠀⠀⠘⡄⠀⠀⠑⠦⣄⣀⡤⢼⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⣧⠀⠀⠀⢀⡴⠈⠉⠁⠀⠀⠀⠇
            ⠀⠀⠀⠱⡄⠀⠀⠀⠀⠀⠀⠀⢨⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠋⠁
            ⠀⠀⠀⠀⠉⠣⡄⠀⠀⠀⠀⠀⠀⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀
            ⠀⠀⠀⠀⠀⠀⠈⠉⠢⠤⠤⠤⠖⠋⠉⢀⡀⠀⠀⠀⠀⠀⠀⠀⡇⠀⡤
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠒⠒⠒⠒⠋⠈⠁⠉⠓⠒⠒⠒⠉⠁
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
            ⠀⠀⠀⠀⠀⠀⠀⠀⠀
            """
        ).strip(),

        CreaturePose.EATING: textwrap.dedent(
            """
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣖⣶⣶⣦⣄⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡿⣏⡝⠛⠯⢿⣯⣆⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⠏⠀⠀⠀⠙⡟⣿⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠤⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠖⠲⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢏⡟⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠉⢆⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠁⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⣴⠾⠛⠋⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⣶⡄⠀⠀⠱⡀⢾⠛⢦⣶⠛⣧⠀⡇⠀⠀⠀⡤⡲⣅⡇⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠘⣿⣿⢦⠀⠀⠁⠘⠳⢾⣿⠾⠟⠙⠀⠀⢀⣯⣟⣬⠏⠀⠀⠀⠀⠈⠛⠃⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠙⡿⠁⠁⠀⠀⠀⠠⠟⠋⠛⠆⠀⠀⠀⠀⠻⡿⠵⠀⠀⠀⠀⠀⢿⣦⡄⣯⣷
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠃⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⢠⣤⡀⠀⠈⠧⡄
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠁⠀⠀⠀⣿⡏⢳⠀⠀⠀⠀⠀⠀⣿⡍⢹
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠀⢀⢀⠈⠛⠇⠀⠀⠠⣤⠀⠀⠈⠙⠃⢀⡀⠀⣸
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠙⠉⠀⠀⠀⠀⠀⠴⠋⠙⠦⠀⠀⠀⠀⢉⡥⠋
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡹⢲⡤⠤⢄⣀⣀⣀⣀⣀⣠⠤⠖⢋⣅⡀
                  ⠀⠀⠀⠀⠀⣠⠞⠉⠉⠉⠳⡄⡠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠆
                  ⠀⠀⠀⢠⠏⠀⢀⣀⣤⡀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠒⢦⡄⠀⠀⠀⠀⠀⠀⣴⡍⠀⠀⠀⢳
                  ⠀⠀⢠⠇⠀⢸⠁⠀⠀⠈⡇⡸⠀⠀⠀⠀⠀⠀⠀⠀⠉⢯⣧⠶⠚⠛⢧⡟⠀⠀⠀⠀⠀⠘⡄
                  ⠀⠀⢸⠀⠀⠸⡀⠀⠙⠋⠁⢯⠀⠀⠀⠀⠀⠀⠲⣄⣀⣠⡇⠀⠀⠀⠘⣧⣄⣀⡤⠀⠀⡇
                  ⠀⠀⠘⡄⠀⠀⠑⠦⣄⣀⡤⢼⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⣧⠀⠀⠀⢀⡴⠈⠉⠁⠀⠀⠀⠇
                  ⠀⠀⠀⠱⡄⠀⠀⠀⠀⠀⠀⠀⢨⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠋⠁
                  ⠀⠀⠀⠀⠉⠣⡄⠀⠀⠀⠀⠀⠀⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀
                  ⠀⠀⠀⠀⠀⠀⠈⠉⠢⠤⠤⠤⠖⠋⠉⢀⡀⠀⠀⠀⠀⠀⠀⠀⡇⠀⡤
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠒⠒⠒⠒⠋⠈⠁⠉⠓⠒⠒⠒⠉⠁
                  ⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀
            """
        ).strip(),

        CreaturePose.BOUNCING: textwrap.dedent(
            """
                    ~  ~  ~
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣖⣶⣶⣦⣄⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡿⣏⡝⠛⠯⢿⣯⣆⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⠏⠀⠀⠀⠙⡟⣿⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠤⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠖⠲⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢏⡟⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠉⢆⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠁⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⣴⠾⠛⠋⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⣶⡄⠀⠀⠱⡀⢾⠛⢦⣶⠛⣧⠀⡇⠀⠀⠀⡤⡲⣅⡇⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠘⣿⣿⢦⠀⠀⠁⠘⠳⢾⣿⠾⠟⠙⠀⠀⢀⣯⣟⣬⠏⠀⠀⠀⠀⠈⠛⠃⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠙⡿⠁⠁⠀⠀⠀⠠⠟⠋⠛⠆⠀⠀⠀⠀⠻⡿⠵⠀⠀⠀⠀⠀⢿⣦⡄⣯⣷
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠃⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⢠⣤⡀⠀⠈⠧⡄
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠁⠀⠀⠀⣿⡏⢳⠀⠀⠀⠀⠀⠀⣿⡍⢹
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠀⢀⢀⠈⠛⠇⠀⠀⠠⣤⠀⠀⠈⠙⠃⢀⡀⠀⣸
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠙⠉⠀⠀⠀⠀⠀⠴⠋⠙⠦⠀⠀⠀⠀⢉⡥⠋
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡹⢲⡤⠤⢄⣀⣀⣀⣀⣀⣠⠤⠖⢋⣅⡀
                  ⠀⠀⠀⠀⠀⣠⠞⠉⠉⠉⠳⡄⡠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠆
                  ⠀⠀⠀⢠⠏⠀⢀⣀⣤⡀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠒⢦⡄⠀⠀⠀⠀⠀⠀⣴⡍⠀⠀⠀⢳
                  ⠀⠀⢠⠇⠀⢸⠁⠀⠀⠈⡇⡸⠀⠀⠀⠀⠀⠀⠀⠀⠉⢯⣧⠶⠚⠛⢧⡟⠀⠀⠀⠀⠀⠘⡄
                  ⠀⠀⢸⠀⠀⠸⡀⠀⠙⠋⠁⢯⠀⠀⠀⠀⠀⠀⠲⣄⣀⣠⡇⠀⠀⠀⠘⣧⣄⣀⡤⠀⠀⡇
                  ⠀⠀⠘⡄⠀⠀⠑⠦⣄⣀⡤⢼⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⣧⠀⠀⠀⢀⡴⠈⠉⠁⠀⠀⠀⠇
                  ⠀⠀⠀⠱⡄⠀⠀⠀⠀⠀⠀⠀⢨⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠋⠁
                  ⠀⠀⠀⠀⠉⠣⡄⠀⠀⠀⠀⠀⠀⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀
                  ⠀⠀⠀⠀⠀⠀⠈⠉⠢⠤⠤⠤⠖⠋⠉⢀⡀⠀⠀⠀⠀⠀⠀⠀⡇⠀⡤
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠒⠒⠒⠒⠋⠈⠁⠉⠓⠒⠒⠒⠉⠁
                  ⠀⠀⠀⠀⠀
                  ⠀⠀⠀
            """
        ).strip(),

        CreaturePose.WALKING: textwrap.dedent(
            """
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣖⣶⣶⣦⣄⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⡿⣏⡝⠛⠯⢿⣯⣆⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⠏⠀⠀⠀⠙⡟⣿⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠤⠤⢄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠖⠲⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢏⡟⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠉⢆⡀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠁⠀⠀⠀⠀⢧⠀⠀⠀⠀⠀⠀⣴⠾⠛⠋⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⣶⡄⠀⠀⠱⡀⢾⠛⢦⣶⠛⣧⠀⡇⠀⠀⠀⡤⡲⣅⡇⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢆⠘⣿⣿⢦⠀⠀⠁⠘⠳⢾⣿⠾⠟⠙⠀⠀⢀⣯⣟⣬⠏⠀⠀⠀⠀⠈⠛⠃⠀⠀
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠙⡿⠁⠁⠀⠀⠀⠠⠟⠋⠛⠆⠀⠀⠀⠀⠻⡿⠵⠀⠀⠀⠀⠀⢿⣦⡄⣯⣷
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠃⠀⠀⠀⣀⡀⠀⠀⠀⠀⠀⠀⢠⣤⡀⠀⠈⠧⡄
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠁⠀⠀⠀⣿⡏⢳⠀⠀⠀⠀⠀⠀⣿⡍⢹
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠀⢀⢀⠈⠛⠇⠀⠀⠠⣤⠀⠀⠈⠙⠃⢀⡀⠀⣸
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠙⠉⠀⠀⠀⠀⠀⠴⠋⠙⠦⠀⠀⠀⠀⢉⡥⠋
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡹⢲⡤⠤⢄⣀⣀⣀⣀⣀⣠⠤⠖⢋⣅⡀
                  ⠀⠀⠀⠀⠀⣠⠞⠉⠉⠉⠳⡄⡠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠆
                  ⠀⠀⠀⢠⠏⠀⢀⣀⣤⡀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠒⢦⡄⠀⠀⠀⠀⠀⠀⣴⡍⠀⠀⠀⢳
                  ⠀⠀⢠⠇⠀⢸⠁⠀⠀⠈⡇⡸⠀⠀⠀⠀⠀⠀⠀⠀⠉⢯⣧⠶⠚⠛⢧⡟⠀⠀⠀⠀⠀⠘⡄
                  ⠀⠀⢸⠀⠀⠸⡀⠀⠙⠋⠁⢯⠀⠀⠀⠀⠀⠀⠲⣄⣀⣠⡇⠀⠀⠀⠘⣧⣄⣀⡤⠀⠀⡇
                  ⠀⠀⠘⡄⠀⠀⠑⠦⣄⣀⡤⢼⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⣧⠀⠀⠀⢀⡴⠈⠉⠁⠀⠀⠀⠇
                  ⠀⠀⠀⠱⡄⠀⠀⠀⠀⠀⠀⠀⢨⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠋⠁
                  ⠀⠀⠀⠀⠉⠣⡄⠀⠀⠀⠀⠀⠀⠳⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀
                  ⠀⠀⠀⠀⠀⠀⠈⠉⠢⠤⠤⠤⠖⠋⠉⢀⡀⠀⠀⠀⠀⠀⠀⠀⡇⠀⡤
                  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠑⠒⠒⠒⠒⠋⠈⠁⠉⠓⠒⠒⠒⠉⠁
                  ⠀⠀⠀
                  ⠀⠀⠀
            """
        ).strip(),
    }

    @classmethod
    def render_creature(cls, pose: CreaturePose, expression: CreatureExpression,
                       x_offset: int = 0) -> str:
        """Render a creature with specific pose and expression."""
        template = cls.CREATURE_TEMPLATES.get(pose, cls.CREATURE_TEMPLATES[CreaturePose.STANDING])
        face = cls.EXPRESSIONS.get(expression, cls.EXPRESSIONS[CreatureExpression.HAPPY])

        # Handle both old separate eye format and new combined format
        left_eye = face.get("left_eye", "◉")
        right_eye = face.get("right_eye", "◉")

        # If eyes are combined strings, extract individual characters for proper positioning
        if len(left_eye) > 1:
            # Extract individual characters for proper positioning in template
            left_eye = left_eye[0] if len(left_eye) > 0 else "◉"
            right_eye = left_eye  # Use same character for both eyes if combined
        if len(right_eye) > 1:
            right_eye = right_eye[0] if len(right_eye) > 0 else "◉"

        render_values = {
            "left_eye": left_eye,
            "right_eye": right_eye,
            "nose": face.get("nose", "•"),
            "mouth_line": face.get("mouth_line", "‿‿‿"),
            "whisker_left": face.get("whisker_left", "~"),
            "whisker_right": face.get("whisker_right", "~"),
            "cheek_left": face.get("cheek_left", " "),
            "cheek_right": face.get("cheek_right", " "),
        }

        rendered = template.format(**render_values)

        # Apply horizontal offset if needed
        if x_offset != 0:
            lines = rendered.split("\n")
            if x_offset > 0:
                lines = [" " * x_offset + line for line in lines]
            else:
                trim = abs(x_offset)
                lines = [line[trim:] if len(line) > trim else "" for line in lines]
            rendered = "\n".join(lines)

        return rendered


class ParticleSystem:
    """Manages particle effects like hearts, sparkles, rain, etc."""

    PARTICLE_DEFINITIONS = {
        ParticleType.HEARTS: ["♥", "💕", "💖", "♡"],
        ParticleType.SPARKLES: ["✨", "⭐", "✦", "✧", "⋆"],
        ParticleType.RAIN_CLOUD: ["☁", "💧", "💧", "💧"],
        ParticleType.LIGHTNING: ["⚡", "⚡", "⚡"],
        ParticleType.SLEEP_ZZ: ["Z", "z", "Z", "z"],
        ParticleType.FOOD_CRUMBS: [".", "·", "•", "○"],
        ParticleType.STARS: ["★", "☆", "✦", "✧"],
        ParticleType.TEARS: ["💧", "💧", "💧"],
    }

    @classmethod
    def create_particle_effect(cls, particle_type: ParticleType,
                             intensity: int = 5) -> List[Particle]:
        """Create a list of particles for an effect."""
        particles = []
        symbols = cls.PARTICLE_DEFINITIONS.get(particle_type, ["•"])

        for _ in range(intensity):
            particle = Particle(
                symbol=random.choice(symbols),
                x=random.randint(0, 40),
                y=random.randint(0, 15),
                velocity_x=random.uniform(-0.5, 0.5),
                velocity_y=random.uniform(-1.0, 0.5),
                life=random.uniform(0.5, 1.0),
                decay=random.uniform(0.05, 0.15)
            )
            particles.append(particle)

        return particles

    @classmethod
    def update_particles(cls, particles: List[Particle]) -> List[Particle]:
        """Update particle positions and remove dead particles."""
        updated = []

        for particle in particles:
            # Update position
            particle.x += particle.velocity_x
            particle.y += particle.velocity_y

            # Update life
            particle.life -= particle.decay

            # Keep alive particles
            if particle.life > 0 and 0 <= particle.x <= 50 and 0 <= particle.y <= 20:
                updated.append(particle)

        return updated

    @classmethod
    def render_particles(cls, particles: List[Particle], width: int = 50,
                        height: int = 20) -> str:
        """Render particles onto a canvas."""
        # Create empty canvas
        canvas = [[' ' for _ in range(width)] for _ in range(height)]

        # Place particles
        for particle in particles:
            x, y = int(particle.x), int(particle.y)
            if 0 <= x < width and 0 <= y < height:
                # Apply alpha based on life
                if particle.life > 0.7:
                    canvas[y][x] = particle.symbol
                elif particle.life > 0.3:
                    canvas[y][x] = '·'  # Faded version

        # Convert to string
        return '\n'.join(''.join(row) for row in canvas)


class EnhancedAnimationEngine:
    """Advanced animation engine with layered rendering and particle effects."""

    def __init__(self):
        self.current_pose = CreaturePose.STANDING
        self.current_expression = CreatureExpression.HAPPY
        self.particles: List[Particle] = []
        self.creature_x_offset = 0
        self.target_x_offset = 0
        self.movement_speed = 0.5

        # Animation state
        self.breathing_phase = 0.0
        self.blink_timer = 0.0
        self.last_blink = 0.0

        # Dynamic movement state
        self.idle_movement_timer = 0.0
        self.ear_twitch_timer = 0.0
        self.tail_swish_timer = 0.0
        self.head_bob_phase = 0.0
        self.movement_pattern = 0  # For varying movement patterns

        # Thinking/loading state
        self.is_thinking = False
        self.thinking_dots = ""
        self.thinking_messages = [
            "pondering...",
            "thinking deeply...",
            "considering options...",
            "processing thoughts...",
            "having an idea...",
            "contemplating...",
            "mulling it over...",
            "brain wheels turning...",
            "connecting dots...",
            "piecing together thoughts..."
        ]
        self.current_thinking_message = ""
        self.thinking_symbol_cycle = 0

    def update_mood_from_stats(self, hunger: float, happiness: float,
                              energy: float, health: float):
        """Update creature's expression and pose based on stats."""
        # Determine expression based on stats
        if health < 30:
            self.current_expression = CreatureExpression.SAD
        elif happiness > 80:
            if energy > 70:
                self.current_expression = CreatureExpression.EXCITED
            else:
                self.current_expression = CreatureExpression.HAPPY
        elif energy < 30:
            self.current_expression = CreatureExpression.SLEEPY
        elif hunger < 30:
            self.current_expression = CreatureExpression.SAD
        else:
            self.current_expression = CreatureExpression.HAPPY

        # Determine pose based on energy and mood
        if energy < 20:
            self.current_pose = CreaturePose.LYING_DOWN
        elif energy > 80 and happiness > 70:
            self.current_pose = CreaturePose.DANCING
        elif energy > 60:
            self.current_pose = CreaturePose.STANDING
        else:
            self.current_pose = CreaturePose.SITTING

    def add_particle_effect(self, effect_type: ParticleType, intensity: int = 5):
        """Add a particle effect to the scene."""
        new_particles = ParticleSystem.create_particle_effect(effect_type, intensity)
        self.particles.extend(new_particles)

    def move_creature_to(self, x_position: int):
        """Start movement animation to a new position."""
        self.target_x_offset = max(-10, min(10, x_position))

    def generate_frame(self) -> EnhancedAnimationFrame:
        """Generate a complete animation frame with all layers."""
        # Update continuous animations
        self._update_continuous_animations()

        # Update particles
        self.particles = ParticleSystem.update_particles(self.particles)

        # Smooth movement towards target
        if abs(self.creature_x_offset - self.target_x_offset) > 0.1:
            diff = self.target_x_offset - self.creature_x_offset
            self.creature_x_offset += diff * self.movement_speed

        # Create layers
        layers = []

        # Background layer (environment)
        background = self._generate_background()
        layers.append(AnimationLayer(background, 0, 0, "background"))

        # Creature layer
        creature = DynamicCreatureRenderer.render_creature(
            self.current_pose, self.current_expression, int(self.creature_x_offset)
        )
        layers.append(AnimationLayer(creature, 0, 0, "creature"))

        # Effects layer
        effects = ParticleSystem.render_particles(self.particles)
        layers.append(AnimationLayer(effects, 0, 0, "effects"))

        return EnhancedAnimationFrame(layers, self.particles.copy(), 100)

    def start_thinking(self):
        """Start the thinking/loading animation."""
        self.is_thinking = True
        self.current_thinking_message = random.choice(self.thinking_messages)
        self.thinking_dots = ""
        self.thinking_symbol_cycle = 0

    def stop_thinking(self):
        """Stop the thinking/loading animation."""
        self.is_thinking = False
        self.current_thinking_message = ""
        self.thinking_dots = ""

    def _update_continuous_animations(self):
        """Update continuous micro-animations like breathing."""
        import time
        import math
        current_time = time.time()

        # Breathing animation (subtle size changes)
        self.breathing_phase += 0.1

        # Random blinking
        if current_time - self.last_blink > random.uniform(2.0, 5.0):
            self.blink_timer = 0.3
            self.last_blink = current_time

        if self.blink_timer > 0:
            self.blink_timer -= 0.1

        # Dynamic idle movements
        self.idle_movement_timer += 0.1
        self.ear_twitch_timer += 0.15
        self.tail_swish_timer += 0.12
        self.head_bob_phase += 0.08

        # Randomly change movement patterns
        if random.random() < 0.01:  # 1% chance per frame
            self.movement_pattern = random.randint(0, 3)

        # Add subtle swaying movement
        sway_offset = math.sin(self.idle_movement_timer) * 0.5
        self.target_x_offset = sway_offset

        # Randomly change poses for idle movement
        if not self.is_thinking and random.random() < 0.008:  # 0.8% chance per frame
            idle_poses = [CreaturePose.STANDING, CreaturePose.SITTING, CreaturePose.BOUNCING]
            if self.current_pose not in idle_poses:
                self.current_pose = CreaturePose.STANDING
            else:
                # Occasionally switch to bouncing or different sitting positions
                if random.random() < 0.4:
                    self.current_pose = random.choice(idle_poses)

        # Add subtle ear twitching animation
        if random.random() < 0.02:  # 2% chance per frame
            self.ear_twitch_timer = 0.5

        # Thinking animation updates
        if self.is_thinking:
            self.thinking_symbol_cycle += 1
            if self.thinking_symbol_cycle % 20 == 0:  # Update every 20 frames
                dot_count = (self.thinking_symbol_cycle // 20) % 4
                self.thinking_dots = "." * dot_count
                if dot_count == 0 and random.random() < 0.3:
                    self.current_thinking_message = random.choice(self.thinking_messages)

    def _generate_background(self) -> str:
        """Generate background elements (ground, sky, etc.)."""
        import math

        lines = []

        # Add thinking indicator if chinchilla is thinking
        if self.is_thinking:
            thinking_symbols = ["💭", "⚡", "✨", "💫"]
            symbol = thinking_symbols[self.thinking_symbol_cycle // 15 % len(thinking_symbols)]
            lines.append(f"                {symbol} {self.current_thinking_message}{self.thinking_dots}")
            lines.extend([""] * 16)
        else:
            lines.extend([""] * 17)

        # Add dynamic ground with subtle movement
        ground_char = "═"
        if self.movement_pattern == 1:
            ground_char = "▬"
        elif self.movement_pattern == 2:
            ground_char = "―"

        # Add some random sparkles or environment elements
        if random.random() < 0.05:  # 5% chance
            sparkle_pos = random.randint(5, 45)
            ground_line = list(ground_char * 50)
            ground_line[sparkle_pos] = random.choice(["✨", "⭐", "·"])
            lines.append("".join(ground_line))
        else:
            lines.append(ground_char * 50)

        lines.append("")

        return "\n".join(lines)

    def trigger_action_animation(self, action: PetAction):
        """Trigger a specific action animation with effects."""
        if action == PetAction.SMILE:
            self.current_expression = CreatureExpression.HAPPY
            self.add_particle_effect(ParticleType.HEARTS, 3)
        elif action == PetAction.WAVE:
            self.current_pose = CreaturePose.DANCING
            self.add_particle_effect(ParticleType.SPARKLES, 5)
        elif action == PetAction.WIGGLE:
            # Quick left-right movement
            self.move_creature_to(-3)
            asyncio.create_task(self._wiggle_sequence())
        elif action == PetAction.THINK:
            self.current_expression = CreatureExpression.CONFUSED
            self.add_particle_effect(ParticleType.STARS, 2)

    async def _wiggle_sequence(self):
        """Perform a wiggle animation sequence."""
        await asyncio.sleep(0.2)
        self.move_creature_to(3)
        await asyncio.sleep(0.2)
        self.move_creature_to(0)
            
