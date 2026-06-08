"""Periodic discussion -> repo bridge scanner.

Runs on an interval (started from app lifespan). Asks BridgeService to scan `actionable_threads`
and produce issue proposals (which land in the Proposal Queue for human approval). This is what
makes proposals appear without anyone asking. Accepts Fivetran's batch sync cadence — see the
latency caveat in docs/architecture.md.
"""


async def run_scanner(interval_seconds: int = 600) -> None:
    """Loop: every `interval_seconds`, run BridgeService.scan().

    TODO: while True: await bridge_service.scan(); await asyncio.sleep(interval_seconds).
    """
    raise NotImplementedError
