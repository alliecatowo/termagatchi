"""Sprite widget for displaying the animated pet."""

import asyncio
from textual.widgets import Static
from textual.app import ComposeResult
from textual import work
from rich.text import Text
from rich.align import Align

from ..ai.schema import PetAction
from ..engine.actions import get_action_animation, get_idle_frame


class SpriteWidget(Static):
    """Widget that displays the pet sprite with animations."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_frame = get_idle_frame()
        self.is_animating = False
        self.animation_task = None

    def compose(self) -> ComposeResult:
        """Compose the sprite widget."""
        yield Static(self.current_frame, id="sprite-display", classes="sprite-display")

    def on_mount(self) -> None:
        """Initialize the sprite widget."""
        self.add_class("sprite-container")
        self.update_display()

    def update_display(self) -> None:
        """Update the sprite display."""
        sprite_display = self.query_one("#sprite-display", Static)

        # Create rich text with golden color
        text = Text(self.current_frame, style="bold #ffd700")
        aligned_text = Align.center(text)

        sprite_display.update(aligned_text)

    @work(exclusive=True)
    async def play_animation(self, action: PetAction) -> None:
        """Play an animation for the given action."""
        if self.is_animating:
            # Cancel current animation
            if self.animation_task:
                self.animation_task.cancel()

        self.is_animating = True
        animation = get_action_animation(action)

        try:
            # Play animation frames
            for frame_data in animation.frames:
                self.current_frame = frame_data.frame
                self.update_display()
                await asyncio.sleep(frame_data.duration_ms / 1000.0)

            # Return to idle frame
            self.current_frame = get_idle_frame()
            self.update_display()

        except asyncio.CancelledError:
            pass
        finally:
            self.is_animating = False

    def set_idle_frame(self) -> None:
        """Set the sprite to idle frame."""
        if not self.is_animating:
            self.current_frame = get_idle_frame()
            self.update_display()

    def get_current_frame(self) -> str:
        """Get the current frame being displayed."""
        return self.current_frame