"""Pet actions and animation definitions."""

from ..ai.schema import PetAction


class AnimationFrame:
    """A single frame of ASCII art animation."""

    def __init__(self, frame: str, duration_ms: int = 100):
        self.frame = frame
        self.duration_ms = duration_ms


class ActionAnimation:
    """Complete animation sequence for a pet action."""

    def __init__(self, frames: list[str], fps: int = 8):
        self.frames = [AnimationFrame(frame, int(1000 / fps)) for frame in frames]
        self.fps = fps
        self.total_duration_ms = len(frames) * int(1000 / fps)


# ASCII art frames for each action
# TODO: Fix escape sequence warnings by using raw strings (r"...") for all ASCII art
ACTION_ANIMATIONS: dict[PetAction, ActionAnimation] = {
    PetAction.SMILE: ActionAnimation(
        [
            r"""
       [yellow]░░░░░░░░░░░░░░░░░░░[/yellow]
      [yellow]░░░[black]███████████[/black]░░░░░░[/yellow]
     [yellow]░░[black]███████████████[/black]░░░░[/yellow]
    [yellow]░░[black]█████████████████[/black]░░[/yellow]
   [yellow]░░[black]█[/black][red]███[/red][black]███████[/black][red]███[/red][black]█[/black]░░[/yellow]
  [yellow]░░[black]█[/black][red]███████████[/red][black]█[/black]░░[/yellow]
 [yellow]░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░[/yellow]
[yellow]░░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░░[/yellow]
[yellow]░░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░░[/yellow]
[yellow]░░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░░[/yellow]
[yellow]░░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░░[/yellow]
[yellow]░░░[black]██[/black][red]█████████[/red][black]██[/black]░░░[/yellow]
[yellow]░░░░[black]███████████████[/black]░░░░[/yellow]
        """.strip(),
            r"""
       [yellow]░░░░░░░░░░░░░░░░░░░[/yellow]
      [yellow]░░░[black]███████████[/black]░░░░░░[/yellow]
     [yellow]░░[black]███████████████[/black]░░░░[/yellow]
    [yellow]░░[black]█████████████████[/black]░░[/yellow]
   [yellow]░░[black]█[/black][red]███[/red][black]███████[/black][red]███[/red][black]█[/black]░░[/yellow]
  [yellow]░░[black]█[/black][red]███████████[/red][black]█[/black]░░[/yellow]
 [yellow]░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░[/yellow]
[yellow]░░░[black]█[/black][red]███[/red][black]█[/black][blue]∪∪∪[/blue][black]█[/black][red]███[/red][black]█[/black]░░░[/yellow]
[yellow]░░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░░[/yellow]
[yellow]░░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░░[/yellow]
[yellow]░░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░░[/yellow]
[yellow]░░░[black]██[/black][red]█████████[/red][black]██[/black]░░░[/yellow]
[yellow]░░░░[black]███████████████[/black]░░░░[/yellow]
        """.strip(),
        ],
        fps=4,
    ),
    PetAction.LAUGH: ActionAnimation(
        [
            r"""
      ╭─────────╮
     ╱           ╲
    ╱   ◉     ◉   ╲
   ╱               ╲
  ╱     \_____/     ╲
 ╱                   ╲
╱_____________________╲
        """.strip(),
            r"""
      ╭─────────╮
     ╱           ╲
    ╱   ◉     ◉   ╲
   ╱               ╲
  ╱     \^^^^^/     ╲
 ╱                   ╲
╱_____________________╲
        """.strip(),
            r"""
      ╭─────────╮
     ╱           ╲
    ╱   ◉     ◉   ╲
   ╱               ╲
  ╱     \^___^/     ╲
 ╱                   ╲
╱_____________________╲
        """.strip(),
        ],
        fps=8,
    ),
    PetAction.BLUSH: ActionAnimation(
        [
            r"""
    - | ○ ○ | -
    ~ | \_/ | ~
        """.strip(),
            r"""
    ~ | ◉ ◉ | ~
    ~ | \_/ | ~
        """.strip(),
        ],
        fps=4,
    ),
    PetAction.HEART: ActionAnimation(
        [
            r"""
         ╭─────────────╮
        ╱               ╲
       ╱    ◉       ◉    ╲
      ╱                   ╲
     ╱        \___/        ╲
    ╱      ♡        ♡       ╲
   ╱_________________________╲
        """.strip(),
            r"""
         ╭─────────────╮
        ╱               ╲
       ╱    ♥       ♥    ╲
      ╱                   ╲
     ╱        ^_^          ╲
    ╱      ♥        ♥       ╲
   ╱_________________________╲
        """.strip(),
        ],
        fps=6,
    ),
    PetAction.WAVE: ActionAnimation(
        [
            r"""
         ╭─────────────╮
        ╱               ╲
       ╱    ◉       ◉    ╲
      ╱                   ╲
     ╱        \___/        ╲
    ╱          o            ╲
   ╱_________________________╲
        """.strip(),
            r"""
         ╭─────────────╮
        ╱               ╲
       ╱    ◉       ◉    ╲
      ╱                   ╲
     ╱        \___/        ╲
    ╱         o             ╲
   ╱_________________________╲
        """.strip(),
            r"""
         ╭─────────────╮
        ╱               ╲
       ╱    ◉       ◉    ╲
      ╱                   ╲
     ╱        \___/        ╲
    ╱                       ╲
   ╱_________________________╲
        """.strip(),
        ],
        fps=6,
    ),
    PetAction.WIGGLE: ActionAnimation(
        [
            r"""
         ╭─────────────╮
        ╱               ╲
       ╱    ◉       ◉    ╲
      ╱                   ╲
     ╱        \___/        ╲
    ╱      ~         ~      ╲
   ╱_________________________╲
        """.strip(),
            r"""
         ╭─────────────╮
        ╱               ╲
       ╱    ◉       ◉    ╲
      ╱                   ╲
     ╱        \___/        ╲
    ╱     ~         ~       ╲
   ╱_________________________╲
        """.strip(),
            r"""
         ╭─────────────╮
        ╱               ╲
       ╱    ◉       ◉    ╲
      ╱                   ╲
     ╱        \___/        ╲
    ╱                       ╲
   ╱_________________________╲
        """.strip(),
        ],
        fps=10,
    ),
    PetAction.JUMP: ActionAnimation(
        [
            r"""
    | ○ ○ |
    | \_/ |
   ╱       ╲
        """.strip(),
            r"""
   ╭| ○ ○ |╮
   ╰| \_/ |╯
        """.strip(),
            r"""
    | ○ ○ |
    | \_/ |
   ╱       ╲
        """.strip(),
        ],
        fps=8,
    ),
    PetAction.EAT: ActionAnimation(
        [
            r"""
    | ○ ○ |
    | \_/ | ●
        """.strip(),
            r"""
    | ○ ○ |
    | \o/ |
        """.strip(),
            r"""
    | ○ ○ |
    | \_/ |
        """.strip(),
        ],
        fps=6,
    ),
    PetAction.CLEAN: ActionAnimation(
        [
            r"""
  ～| ○ ○ |～
    | \_/ |
        """.strip(),
            r"""
  ◦◦| ○ ○ |◦◦
    | \_/ |
        """.strip(),
            r"""
    | ◉ ◉ |
    | \_/ |
        """.strip(),
        ],
        fps=6,
    ),
    PetAction.PLAY: ActionAnimation(
        [
            r"""
    | ○ ○ |
    | \_/ | ★
        """.strip(),
            r"""
  ★ | ◉ ◉ |
    | \^/ |
        """.strip(),
            r"""
    | ○ ○ | ★
    | \_/ |
        """.strip(),
        ],
        fps=8,
    ),
    PetAction.NAP: ActionAnimation(
        [
            r"""
    | - - |
    | \_/ |
        """.strip(),
            r"""
    | ‾ ‾ |
    | \_/ |
        """.strip(),
        ],
        fps=2,
    ),
    PetAction.SLEEPING: ActionAnimation(
        [
            r"""
    | - - |  Z
    | \_/ | z
        """.strip(),
            r"""
    | ‾ ‾ | z
    | \_/ |  Z
        """.strip(),
        ],
        fps=2,
    ),
    PetAction.SAD: ActionAnimation(
        [
            r"""
         ╭─────────────╮
        ╱               ╲
       ╱    ◉       ◉    ╲
      ╱                   ╲
     ╱        /‾‾‾\        ╲
    ╱                       ╲
   ╱_________________________╲
        """.strip(),
            r"""
         ╭─────────────╮
        ╱               ╲
       ╱    ◦       ◦    ╲
      ╱                   ╲
     ╱        /‾‾‾\        ╲
    ╱                       ╲
   ╱_________________________╲
        """.strip(),
        ],
        fps=3,
    ),
    PetAction.CRY: ActionAnimation(
        [
            r"""
  ╷ | ○ ○ | ╷
    | /‾\ |
        """.strip(),
            r"""
  ┆ | ◦ ◦ | ┆
    | /‾\ |
        """.strip(),
        ],
        fps=4,
    ),
    PetAction.SICK: ActionAnimation(
        [
            r"""
    | × × |
    | /‾\ |
        """.strip(),
            r"""
    | ◦ ◦ |
    | /○\ |
        """.strip(),
        ],
        fps=3,
    ),
    PetAction.HEAL: ActionAnimation(
        [
            r"""
  ╋ | ○ ○ | ╋
    | \_/ |
        """.strip(),
            r"""
  ✚ | ◉ ◉ | ✚
    | \_/ |
        """.strip(),
            r"""
    | ○ ○ |
    | \_/ |
        """.strip(),
        ],
        fps=6,
    ),
    PetAction.CONFUSED: ActionAnimation(
        [
            r"""
  ? | ○ ○ | ?
    | \_? |
        """.strip(),
            r"""
  ? | ◦ ◦ | ?
    | \_? |
        """.strip(),
        ],
        fps=4,
    ),
    PetAction.THINK: ActionAnimation(
        [
            r"""
  . | ○ ○ |
  ° | \_/ |
        """.strip(),
            r"""
  ° | ○ ○ |
  ○ | \_/ |
        """.strip(),
            r"""
  ○ | ○ ○ |
    | \_/ |
        """.strip(),
        ],
        fps=4,
    ),
    PetAction.SURPRISED: ActionAnimation(
        [
            r"""
    | ○ ○ |
    | \_○ |
        """.strip(),
            r"""
    | ◉ ◉ |
    | \_O |
        """.strip(),
            r"""
    | ○ ○ |
    | \_/ |
        """.strip(),
        ],
        fps=8,
    ),
    PetAction.THANKS: ActionAnimation(
        [
            r"""
    | ○ ○ |
    | \_/ |
  ╰───────╯
        """.strip(),
            r"""
    | ◉ ◉ |
    | \_/ |
  ╰ thank ╯
   you!
        """.strip(),
            r"""
    | ○ ○ |
    | \_/ |
        """.strip(),
        ],
        fps=6,
    ),
}


def get_action_animation(action: PetAction) -> ActionAnimation:
    """Get the animation for a specific action."""
    return ACTION_ANIMATIONS.get(action, ACTION_ANIMATIONS[PetAction.SMILE])


def get_idle_frame() -> str:
    """Get the default idle frame for the pet."""
    return r"""
       [yellow]░░░░░░░░░░░░░░░░░░░[/yellow]
      [yellow]░░░[black]███████████[/black]░░░░░░[/yellow]
     [yellow]░░[black]███████████████[/black]░░░░[/yellow]
    [yellow]░░[black]█████████████████[/black]░░[/yellow]
   [yellow]░░[black]█[/black][red]███[/red][black]███████[/black][red]███[/red][black]█[/black]░░[/yellow]
  [yellow]░░[black]█[/black][red]███████████[/red][black]█[/black]░░[/yellow]
 [yellow]░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░[/yellow]
[yellow]░░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░░[/yellow]
[yellow]░░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░░[/yellow]
[yellow]░░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░░[/yellow]
[yellow]░░░[black]█[/black][red]███[/red][black]█[/black][blue]███[/blue][black]█[/black][red]███[/red][black]█[/black]░░░[/yellow]
[yellow]░░░[black]██[/black][red]█████████[/red][black]██[/black]░░░[/yellow]
[yellow]░░░░[black]███████████████[/black]░░░░[/yellow]
    """.strip()
