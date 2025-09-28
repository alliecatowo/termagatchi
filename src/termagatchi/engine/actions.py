"""Pet actions and animation definitions."""

from typing import Dict, List
from ..ai.schema import PetAction


class AnimationFrame:
    """A single frame of ASCII art animation."""

    def __init__(self, frame: str, duration_ms: int = 100):
        self.frame = frame
        self.duration_ms = duration_ms


class ActionAnimation:
    """Complete animation sequence for a pet action."""

    def __init__(self, frames: List[str], fps: int = 8):
        self.frames = [AnimationFrame(frame, int(1000 / fps)) for frame in frames]
        self.fps = fps
        self.total_duration_ms = len(frames) * int(1000 / fps)


# ASCII art frames for each action
# TODO: Fix escape sequence warnings by using raw strings (r"...") for all ASCII art
ACTION_ANIMATIONS: Dict[PetAction, ActionAnimation] = {
    PetAction.SMILE: ActionAnimation([
        """
    - | ○ ○ | -
    - | \_/ | -
        """.strip(),
        """
    - | ◉ ◉ | -
    - | \_/ | -
        """.strip(),
    ], fps=4),

    PetAction.LAUGH: ActionAnimation([
        """
    - | ○ ○ | -
    - | \_/ | -
        """.strip(),
        """
    - | ◉ ◉ | -
    - | \^/ | -
        """.strip(),
        """
    - | ◉ ◉ | -
    - | \_/ | -
        """.strip(),
    ], fps=8),

    PetAction.BLUSH: ActionAnimation([
        """
    - | ○ ○ | -
    ~ | \_/ | ~
        """.strip(),
        """
    ~ | ◉ ◉ | ~
    ~ | \_/ | ~
        """.strip(),
    ], fps=4),

    PetAction.HEART: ActionAnimation([
        """
    ♡ | ○ ○ | ♡
    - | \_/ | -
        """.strip(),
        """
    ♥ | ◉ ◉ | ♥
    - | \_/ | -
        """.strip(),
    ], fps=6),

    PetAction.WAVE: ActionAnimation([
        """
  ╭─| ○ ○ |─╮
    | \_/ |
        """.strip(),
        """
    | ○ ○ |─╮
    | \_/ |
        """.strip(),
        """
  ╭─| ○ ○ |
    | \_/ |
        """.strip(),
    ], fps=6),

    PetAction.WIGGLE: ActionAnimation([
        """
  ╱ | ○ ○ | ╲
    | \_/ |
        """.strip(),
        """
  ╲ | ○ ○ | ╱
    | \_/ |
        """.strip(),
        """
    | ○ ○ |
    | \_/ |
        """.strip(),
    ], fps=10),

    PetAction.JUMP: ActionAnimation([
        """
    | ○ ○ |
    | \_/ |
   ╱       ╲
        """.strip(),
        """
   ╭| ○ ○ |╮
   ╰| \_/ |╯
        """.strip(),
        """
    | ○ ○ |
    | \_/ |
   ╱       ╲
        """.strip(),
    ], fps=8),

    PetAction.EAT: ActionAnimation([
        """
    | ○ ○ |
    | \_/ | ●
        """.strip(),
        """
    | ○ ○ |
    | \o/ |
        """.strip(),
        """
    | ○ ○ |
    | \_/ |
        """.strip(),
    ], fps=6),

    PetAction.CLEAN: ActionAnimation([
        """
  ～| ○ ○ |～
    | \_/ |
        """.strip(),
        """
  ◦◦| ○ ○ |◦◦
    | \_/ |
        """.strip(),
        """
    | ◉ ◉ |
    | \_/ |
        """.strip(),
    ], fps=6),

    PetAction.PLAY: ActionAnimation([
        """
    | ○ ○ |
    | \_/ | ★
        """.strip(),
        """
  ★ | ◉ ◉ |
    | \^/ |
        """.strip(),
        """
    | ○ ○ | ★
    | \_/ |
        """.strip(),
    ], fps=8),

    PetAction.NAP: ActionAnimation([
        """
    | - - |
    | \_/ |
        """.strip(),
        """
    | ‾ ‾ |
    | \_/ |
        """.strip(),
    ], fps=2),

    PetAction.SLEEPING: ActionAnimation([
        """
    | - - |  Z
    | \_/ | z
        """.strip(),
        """
    | ‾ ‾ | z
    | \_/ |  Z
        """.strip(),
    ], fps=2),

    PetAction.SAD: ActionAnimation([
        """
    | ○ ○ |
    | /‾\ |
        """.strip(),
        """
    | ◦ ◦ |
    | /‾\ |
        """.strip(),
    ], fps=3),

    PetAction.CRY: ActionAnimation([
        """
  ╷ | ○ ○ | ╷
    | /‾\ |
        """.strip(),
        """
  ┆ | ◦ ◦ | ┆
    | /‾\ |
        """.strip(),
    ], fps=4),

    PetAction.SICK: ActionAnimation([
        """
    | × × |
    | /‾\ |
        """.strip(),
        """
    | ◦ ◦ |
    | /○\ |
        """.strip(),
    ], fps=3),

    PetAction.HEAL: ActionAnimation([
        """
  ╋ | ○ ○ | ╋
    | \_/ |
        """.strip(),
        """
  ✚ | ◉ ◉ | ✚
    | \_/ |
        """.strip(),
        """
    | ○ ○ |
    | \_/ |
        """.strip(),
    ], fps=6),

    PetAction.CONFUSED: ActionAnimation([
        """
  ? | ○ ○ | ?
    | \_? |
        """.strip(),
        """
  ? | ◦ ◦ | ?
    | \_? |
        """.strip(),
    ], fps=4),

    PetAction.THINK: ActionAnimation([
        """
  . | ○ ○ |
  ° | \_/ |
        """.strip(),
        """
  ° | ○ ○ |
  ○ | \_/ |
        """.strip(),
        """
  ○ | ○ ○ |
    | \_/ |
        """.strip(),
    ], fps=4),

    PetAction.SURPRISED: ActionAnimation([
        """
    | ○ ○ |
    | \_○ |
        """.strip(),
        """
    | ◉ ◉ |
    | \_O |
        """.strip(),
        """
    | ○ ○ |
    | \_/ |
        """.strip(),
    ], fps=8),

    PetAction.THANKS: ActionAnimation([
        """
    | ○ ○ |
    | \_/ |
  ╰───────╯
        """.strip(),
        """
    | ◉ ◉ |
    | \_/ |
  ╰ thank ╯
   you!
        """.strip(),
        """
    | ○ ○ |
    | \_/ |
        """.strip(),
    ], fps=6),
}


def get_action_animation(action: PetAction) -> ActionAnimation:
    """Get the animation for a specific action."""
    return ACTION_ANIMATIONS.get(action, ACTION_ANIMATIONS[PetAction.SMILE])


def get_idle_frame() -> str:
    """Get the default idle frame for the pet."""
    return ACTION_ANIMATIONS[PetAction.SMILE].frames[0].frame