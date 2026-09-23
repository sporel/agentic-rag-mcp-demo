# Data Governance Policy

All tables in the Gold layer must have an assigned owner and a documented retention period before being published to the catalog.

Personally identifiable information (PII) columns must be tagged in Unity Catalog and are subject to row- and column-level access controls. Direct queries against PII columns require membership in the `pii-readers` group, audited quarterly.

Data lineage is tracked automatically for all Delta Live Tables pipelines and is viewable in the catalog UI, showing upstream sources and downstream consumers for any table.

Any new pipeline that writes to Gold must pass a governance review checklist covering: schema stability, PII classification, retention policy, and access control configuration, before it can be promoted to production.

