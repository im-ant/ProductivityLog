"""Background waste monitor with macOS notifications."""

import datetime
import logging
import subprocess
import threading

from . import log_parser, analytics

logger = logging.getLogger(__name__)

DEFAULT_THRESHOLD_HOURS = 1.5
DEFAULT_POLL_INTERVAL = 300  # 5 minutes


class WasteMonitor:
    """Polls today's log and notifies when wasted time exceeds threshold."""

    def __init__(
        self,
        threshold_hours: float = DEFAULT_THRESHOLD_HOURS,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        log_dir: str = log_parser.DEFAULT_LOG_DIR,
    ):
        self.threshold_hours = threshold_hours
        self.poll_interval = poll_interval
        self.log_dir = log_dir
        self._stop_event = threading.Event()
        self._notified_today: datetime.date | None = None
        self._thread: threading.Thread | None = None

    def start(self):
        """Start the monitor as a daemon thread."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info(
            "Waste monitor started (threshold=%.1fh, interval=%ds)",
            self.threshold_hours, self.poll_interval,
        )

    def stop(self):
        """Signal the monitor to stop."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=10)

    def _run(self):
        while not self._stop_event.is_set():
            try:
                self._check()
            except Exception:
                logger.exception("Error in waste monitor check")
            self._stop_event.wait(self.poll_interval)

    def _check(self):
        today = datetime.date.today()

        # Reset notification flag on new day
        if self._notified_today != today:
            self._notified_today = None

        # Already notified today
        if self._notified_today == today:
            return

        df = log_parser.get_today_log(self.log_dir)
        if df is None or df.empty:
            return

        sessions = analytics.process_day(df, today)
        wasted = sessions[sessions['Activity_Type'] == 'wasted']
        total_wasted = wasted['DurationHours'].sum() if not wasted.empty else 0

        if total_wasted >= self.threshold_hours:
            self._notify(total_wasted)
            self._notified_today = today

    def _notify(self, hours: float):
        """Send macOS notification via osascript."""
        title = "Productivity Alert"
        message = f"Wasted time today: {hours:.1f}h (threshold: {self.threshold_hours:.1f}h)"
        logger.warning(message)
        try:
            subprocess.run([
                'osascript', '-e',
                f'display notification "{message}" with title "{title}"'
            ], timeout=10, check=False)
        except Exception:
            logger.exception("Failed to send notification")
