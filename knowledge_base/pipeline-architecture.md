# Pipeline Architecture

Our data platform follows a Medallion (Bronze/Silver/Gold) architecture on Databricks.

- **Bronze layer**: raw, unprocessed data landed as-is from source systems (event streams, CDC feeds, file drops). No transformations applied.
- **Silver layer**: cleaned and conformed data — deduplicated, schema-validated, and joined against reference/dimension tables.
- **Gold layer**: business-level aggregates and marts, optimized for BI tools and downstream analytics consumers.

Ingestion into Bronze runs on a scheduled Delta Live Tables pipeline, triggered every 15 minutes. Silver and Gold layers are recomputed incrementally using Delta Lake's change data feed, avoiding full-table rescans.

Data quality checks (null checks, referential integrity, freshness SLAs) run at the Silver layer boundary using expectations defined in the DLT pipeline. Failing records are quarantined to a `_quarantine` table rather than dropped silently.

