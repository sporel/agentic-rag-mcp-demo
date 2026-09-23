# New Engineer Onboarding FAQ

**Q: How do I get access to the data warehouse?**
A: Request access through the internal access-management portal, selecting the "Data Platform - Read" role. Approval typically takes 1 business day.

**Q: Where is the schema documentation?**
A: Table and column definitions live in the data catalog (Unity Catalog). Each Gold-layer table has an owner tag and a linked runbook.

**Q: How do I report a data quality issue?**
A: File a ticket in the #data-platform-support channel with the table name, expected vs. actual behavior, and a sample of affected rows. On-call rotates weekly.

**Q: What's the SLA for Gold-layer freshness?**
A: Gold tables are guaranteed fresh within 1 hour of the corresponding Silver-layer update, except for tables explicitly marked `batch-daily`.

**Q: Who do I contact about pipeline failures?**
A: Pipeline failures page the on-call data engineer automatically via the alerting pipeline. Non-urgent issues go through the standard ticket queue.

