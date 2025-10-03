"""Sprite widget for displaying the animated pet."""

import asyncio

from rich.align import Align
from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.widgets import Static

from ..ai.schema import PetAction
from ..engine.enhanced_animations import EnhancedAnimationEngine
from ..engine.models import PetStats


class SpriteWidget(Static):
    """Widget that displays the pet sprite with animations."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.animation_engine = EnhancedAnimationEngine()
        self.is_animating = False
        self.animation_task = None
        self.continuous_animation_task = None

    def compose(self) -> ComposeResult:
        """Compose the sprite widget."""
        # Return empty compose - we'll update content directly
        return []

    def on_mount(self) -> None:
        """Initialize the sprite widget."""
        self.add_class("sprite-display")
        # Start continuous animation loop
        self.continuous_animation_task = asyncio.create_task(self._continuous_animation_loop())
        # Set initial frame
        self.update_display()

    def update_display(self) -> None:
        """Update the sprite display."""
        # Generate current frame from animation engine
        frame = self.animation_engine.generate_frame()

        # Composite all layers into final frame
        final_content = self._composite_frame(frame)

        # Update display with rich text
        text = Text.from_markup(final_content, style="bold")
        self.update(text)

    async def _continuous_animation_loop(self) -> None:
        """Continuous animation loop that updates the creature display."""
        try:
            while True:
                if not self.is_animating:
                    self.update_display()
                await asyncio.sleep(0.1)  # 10 FPS for smooth animation
        except asyncio.CancelledError:
            pass

    def _composite_frame(self, frame) -> str:
        """Composite all animation layers into a single frame."""
        # For now, simply overlay layers in order: background, creature, effects
        lines = []
        max_width = 50
        max_height = 20

        # Start with empty canvas
        canvas = [[' ' for _ in range(max_width)] for _ in range(max_height)]

        # Apply each layer
        for layer in frame.layers:
            layer_lines = layer.content.split('\n')
            start_y = max(0, layer.y_offset)
            start_x = max(0, layer.x_offset)

            for y, line in enumerate(layer_lines):
                if start_y + y >= max_height:
                    break
                for x, char in enumerate(line):
                    if start_x + x >= max_width:
                        break
                    if char != ' ' and char != '\n':  # Don't overwrite with spaces
                        canvas[start_y + y][start_x + x] = char

        # Convert canvas to string
        return '\n'.join(''.join(row) for row in canvas)

    @work(exclusive=True)
    async def play_animation(self, action: PetAction) -> None:
        """Play an animation for the given action."""
        self.is_animating = True

        try:
            # Trigger action animation in the engine
            self.animation_engine.trigger_action_animation(action)

            # Let the action play for a few seconds
            await asyncio.sleep(2.0)

        except asyncio.CancelledError:
            pass
        finally:
            self.is_animating = False

    def update_stats(self, stats: PetStats) -> None:
        """Update creature mood based on pet stats."""
        self.animation_engine.update_mood_from_stats(
            stats.hunger, stats.happiness, stats.energy, stats.health
        )

    def get_current_frame(self) -> str:
        """Get the current frame being displayed."""
        frame = self.animation_engine.generate_frame()
        return self._composite_frame(frame)
