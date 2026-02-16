# Entity Relationship Diagram

```mermaid
erDiagram
    JOB_RESULTS {
        VARCHAR(64) job_id PK
        JSON result_data
        DATETIME created_at "INDEX: idx_created"
        DATETIME updated_at
    }
```
