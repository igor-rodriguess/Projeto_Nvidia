from __future__ import annotations

import argparse
import os
import signal
import socket
import sys
from pathlib import Path
from threading import Event


sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.batch_processing_service import BatchProcessingService
from app.services.batch_worker_service import BatchWorkerService


def main() -> int:
    parser = argparse.ArgumentParser(description="Worker duravel de lotes de startups.")
    parser.add_argument("--once", action="store_true", help="Processa no maximo um lote.")
    parser.add_argument("--poll-seconds", type=float, default=5.0)
    parser.add_argument("--stale-after-minutes", type=int, default=30)
    parser.add_argument("--worker-id")
    args = parser.parse_args()

    worker_id = args.worker_id or f"{socket.gethostname()}-{os.getpid()}"
    worker = BatchWorkerService(BatchProcessingService.from_env(), worker_id)
    worker.recover_stale(args.stale_after_minutes)
    if args.once:
        worker.run_once()
        return 0

    stop_event = Event()
    signal.signal(signal.SIGINT, lambda *_: stop_event.set())
    signal.signal(signal.SIGTERM, lambda *_: stop_event.set())
    worker.run_forever(stop_event, poll_seconds=args.poll_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
