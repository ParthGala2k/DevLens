"""Periodic proactive blind-spot scanner.

Runs on an interval (started from app lifespan), asks AlertsService to scan current metrics,
and lets new alerts flow to Firestore + the "alerts" SSE channel. This is what makes alerts
appear "without you asking".
"""


async def run_scanner(interval_seconds: int = 300) -> None:
    """Loop: every `interval_seconds`, run AlertsService.scan().

    TODO: while True: await alerts_service.scan(); await asyncio.sleep(interval_seconds).
    """
    raise NotImplementedError
