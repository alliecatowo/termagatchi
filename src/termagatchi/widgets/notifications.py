"""Notifications panel widget for displaying status messages."""

import asyncio
from datetime import datetime

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class NotificationItem(Static):
    """A single notification message."""

    def __init__(self, message: str, timestamp: datetime, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.timestamp = timestamp
        self.fade_task = None

    def compose(self) -> ComposeResult:
        """Compose the notification item."""
        # Format message with timestamp
        time_str = self.timestamp.strftime("%H:%M")
        text = Text(f"[{time_str}] {self.message}", style="#eee")
        yield Static(text)

    @work
    async def start_fade_timer(self, fade_after_seconds: int = 10) -> None:
        """Start fade timer for this notification."""
        try:
            await asyncio.sleep(fade_after_seconds)
            # Add fade styling
            self.add_class("fading-notification")
            await asyncio.sleep(2)  # Fade duration
            # Request removal
            self.parent.remove_notification(self)
        except asyncio.CancelledError:
            pass

    def cancel_fade(self) -> None:
        """Cancel the fade timer."""
        if self.fade_task:
            self.fade_task.cancel()


class NotificationsPanel(Static):
    """Panel for displaying multiple notifications."""

    def __init__(self, max_notifications: int = 5, **kwargs):
        super().__init__(**kwargs)
        self.max_notifications = max_notifications
        self.notifications: list[NotificationItem] = []

    def compose(self) -> ComposeResult:
        """Compose the notifications panel."""
        with Vertical(id="notifications-container"):
            yield Static("NOTIFICATIONS", classes="notification-title")

    def on_mount(self) -> None:
        """Initialize the notifications panel."""
        self.add_class("notifications-panel")

    def add_notification(self, message: str, auto_fade: bool = True) -> None:
        """Add a new notification message."""
        timestamp = datetime.now()
        notification = NotificationItem(message, timestamp)

        # Add to container
        container = self.query_one("#notifications-container", Vertical)
        container.mount(notification)

        # Track notification
        self.notifications.append(notification)

        # Start fade timer if enabled
        if auto_fade:
            notification.start_fade_timer()

        # Remove oldest notifications if we exceed max
        while len(self.notifications) > self.max_notifications:
            oldest = self.notifications.pop(0)
            oldest.cancel_fade()
            oldest.remove()

    def remove_notification(self, notification: NotificationItem) -> None:
        """Remove a specific notification."""
        if notification in self.notifications:
            self.notifications.remove(notification)
            notification.remove()

    def clear_all(self) -> None:
        """Clear all notifications."""
        for notification in self.notifications:
            notification.cancel_fade()
            notification.remove()
        self.notifications.clear()

    def get_notification_count(self) -> int:
        """Get the current number of notifications."""
        return len(self.notifications)

    def update_notifications(self, messages: list[str]) -> None:
        """Update notifications with a new list of messages."""
        # Clear existing notifications
        self.clear_all()

        # Add new notifications
        for message in messages[-self.max_notifications :]:
            self.add_notification(message, auto_fade=False)
