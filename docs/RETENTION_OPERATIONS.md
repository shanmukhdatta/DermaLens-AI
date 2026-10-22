# Expired analysis metadata retention — operator runbook

Implemented in `services/persistence/retention.py` with an **offline-only** operator CLI `scripts/prune_expired_history.py`. No HTTP deletion endpoint or background scheduler is exposed.

## Behavior

- Requires an existing migrated relational database (`alembic upgrade head`, migration `0003_expiry`).
- Selects only `analyses.expires_at <= current_UTC_time`, never unexpired or NULL expiry metadata.
- Sorts by expiration then ID, and caps deletes to 250 by default (maximum 5000 per invocation).
- Uses a single transaction; associated feedback is deleted by database `ON DELETE CASCADE` enforcement.
- Prints counts only, never user IDs, filenames, predictions or images.
- **Default is dry-run**; actual deletion requires two explicit flags.

## Usage

```bash
# Inspect pending metadata expiry without changing data.
python -m scripts.prune_expired_history --max-records 250

# After operator sign-off and backup/recovery verification, delete one batch.
python -m scripts.prune_expired_history --max-records 250 --execute --confirm-delete
```

Configure `DERMALENS_DATABASE_URL` from a secret manager, not in Git.

## Limitations and release gates

This **does not** schedule recurring jobs, delete raw image objects (none are currently stored), implement legal holds, or validate jurisdiction-specific retention requirements. Operational scheduling, monitoring, authorization to run the CLI, audits and production database backup remain operator responsibilities. Test database FK cascades and restore drills before production use.
