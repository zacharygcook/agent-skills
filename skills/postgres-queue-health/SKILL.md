---
name: postgres-queue-health
description: Review and diagnose Postgres-backed job queues for MVCC dead tuples, index bloat, autovacuum lag, long transactions, claim-query performance, retention, and SKIP LOCKED safety. Use when implementing, debugging, reviewing, or scaling database queues and their dashboards.
---

# Postgres Queue Health

High-churn queue tables can slow down even when live queue depth stays flat. Updates and deletes create dead tuples; old snapshots delay cleanup; hot indexes retain dead entries; and claim workers repeatedly pay the visibility cost. `FOR UPDATE SKIP LOCKED` reduces worker blocking but does not solve bloat or retention.

## Inspect the Claim Path

- Confirm the claim query has a narrow queue/status/due-time predicate, bounded `LIMIT`, intentional ordering, and `FOR UPDATE SKIP LOCKED` where appropriate.
- Compare partial-index predicates and column order with the actual filter and ordering.
- Keep the claim transaction short. Commit the claim/update before external I/O or long job execution.
- Bound batch claims and heartbeat frequency.
- Use `EXPLAIN (ANALYZE, BUFFERS)` safely on representative, non-destructive queries.

## Inspect Lifecycle and Storage

- Separate hot claimable states from terminal history.
- Add bounded cleanup, archive, or partitioning before succeeded/dead jobs dominate the table.
- Keep dedupe and claim indexes free of terminal rows when possible.
- Distinguish update-heavy tables from append-only attempt/event tables; their vacuum risks differ.
- Check table and index growth alongside live/dead tuple estimates, not row count alone.

## Inspect Vacuum and Transactions

- Review table-level autovacuum thresholds for high-churn tables.
- Find long-running and `idle in transaction` sessions that pin the MVCC horizon.
- Compare last vacuum/autovacuum times, dead tuples, relation sizes, claim latency, and queue depth over time.
- Do not recommend manual vacuum as a complete fix while an old transaction still prevents cleanup.

## Inspect Read Paths

Keep dashboards and polling queries bounded, indexed, short, and read-only. Avoid broad analytics over hot queue history on the primary.

## Starting Queries

```sql
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum, last_vacuum
FROM pg_stat_user_tables
WHERE relname IN ('queue_jobs', 'queue_job_attempts');
```

```sql
SELECT now() - xact_start AS transaction_age, state, wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_start ASC
LIMIT 20;
```

```sql
SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
WHERE relname IN ('queue_jobs', 'queue_job_attempts');
```

Adapt identifiers and predicates to the repository. Never run mutating maintenance against shared or production databases without explicit authorization.

## Output

Report evidence, likely failure mode, claim/index alignment, retention risk, transaction risk, safe verification queries, and a low/medium/high severity. Separate observed facts from recommendations.

Further reading: [Brandur Leach, “Postgres Job Queues & Failure By MVCC”](https://brandur.org/postgres-queues) and [PlanetScale, “Keeping a Postgres queue healthy”](https://planetscale.com/blog/keeping-a-postgres-queue-healthy).
