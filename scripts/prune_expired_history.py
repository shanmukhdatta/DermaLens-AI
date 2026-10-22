"""Operator-only CLI for bounded, privacy-safe history metadata retention sweeps."""

from __future__ import annotations

import argparse
import json

from apps.api.dermalens_api.config import Settings
from services.persistence.retention import MAX_SWEEP_SIZE, prune_expired_analyses
from services.persistence.runtime import build_database


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-records", type=int, default=250)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete expired analysis metadata and cascaded feedback",
    )
    parser.add_argument(
        "--confirm-delete",
        action="store_true",
        help="Explicit operator confirmation required together with --execute",
    )
    args = parser.parse_args()
    if args.max_records < 1 or args.max_records > MAX_SWEEP_SIZE:
        parser.error(f"--max-records must be within 1..{MAX_SWEEP_SIZE}")
    if args.execute and not args.confirm_delete:
        parser.error("--execute also requires --confirm-delete")
    if args.confirm_delete and not args.execute:
        parser.error("--confirm-delete can only be used with --execute")
    settings = Settings()
    if not settings.database_url:
        parser.error("configure DERMALENS_DATABASE_URL first")
    engine, factory = build_database(settings.database_url)
    try:
        with factory() as session:
            affected = prune_expired_analyses(
                session,
                max_records=args.max_records,
                dry_run=not args.execute,
            )
    finally:
        engine.dispose()
    print(
        json.dumps(
            {
                "mode": "executed" if args.execute else "dry_run",
                "records_matched_or_deleted": affected,
                "batch_limit": args.max_records,
                "contains_personal_data": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
