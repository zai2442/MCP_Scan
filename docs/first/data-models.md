# Data Models · MVP P0 (ER Diagram + JSON Schema)

- **Related Requirement**: [PRD.md:L153-L186](file:///d:/PaperDesign/MCP_scan/docs/PRD.md#L153-L186)
- **Technical Basis**: Knowledge Base & Telemetry [TSD.md:L91-L94](file:///d:/PaperDesign/MCP_scan/docs/TSD.md#L91-L94)
- **Traceability Placeholder**: `commit=COMMIT_TBD`

## ER Diagram (Mermaid)
```mermaid
erDiagram
    JOB ||--o{ TASK : contains
    TASK ||--o{ INVOCATION : triggers
    JOB ||--o{ LOG_ENTRY : logs
    JOB ||--o{ SCAN_RESULT : aggregates
    JOB ||--o{ FINDING : aggregates
    ASSET ||--o{ SCAN_RESULT : observed_on

    JOB {
      string job_id PK
      string target
      string status
      datetime created_at
      datetime updated_at
    }
    TASK {
      string task_id PK
      string job_id FK
      string name
      string status
      datetime started_at
      datetime finished_at
      string last_error_code
    }
    INVOCATION {
      string invocation_id PK
      string task_id FK
      string capability_name
      json input_json
      json output_json
      string trace_id INDEX
      datetime ts
    }
    SCAN_RESULT {
      string result_id PK
      string job_id FK
      string host INDEX
      int port INDEX
      string protocol
      string service
      string version
      json raw
      datetime ts
    }
    FINDING {
      string finding_id PK
      string job_id FK
      string target INDEX
      string name
      string severity INDEX
      string cve
      json evidence
      datetime ts
    }
    LOG_ENTRY {
      string log_id PK
      string job_id FK
      string level INDEX
      string message
      string trace_id INDEX
      datetime ts
    }
    ASSET {
      string asset_id PK
      string host UNIQUE
      string tags
      datetime first_seen
      datetime last_seen
    }
```

## JSON Schema (Core Entities)

### Job
```json
{
  "$id": "https://mcp_scan/schemas/job.json",
  "type": "object",
  "required": ["job_id", "target", "status", "created_at"],
  "properties": {
    "job_id": { "type": "string", "minLength": 8 },
    "target": { "type": "string" },
    "tools": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
    "status": { "type": "string", "enum": ["queued","running","completed","failed","canceled"] },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" }
  }
}
```

### Task
```json
{
  "$id": "https://mcp_scan/schemas/task.json",
  "type": "object",
  "required": ["task_id", "job_id", "name", "status"],
  "properties": {
    "task_id": { "type": "string" },
    "job_id": { "type": "string" },
    "name": { "type": "string" },
    "status": { "type": "string", "enum": ["queued","running","completed","failed"] },
    "started_at": { "type": "string", "format": "date-time" },
    "finished_at": { "type": "string", "format": "date-time" },
    "last_error_code": { "type": "string" }
  }
}
```

### ScanResult (Nmap)
```json
{
  "$id": "https://mcp_scan/schemas/scan_result.json",
  "type": "object",
  "required": ["result_id","job_id","host","port","protocol","ts"],
  "properties": {
    "result_id": { "type": "string" },
    "job_id": { "type": "string" },
    "host": { "type": "string" },
    "port": { "type": "integer", "minimum": 1, "maximum": 65535 },
    "protocol": { "type": "string", "enum": ["tcp","udp"] },
    "state": { "type": "string", "enum": ["open","closed","filtered"] },
    "service": { "type": "string" },
    "version": { "type": "string" },
    "os": {
      "type": "object",
      "properties": {
        "name": { "type": "string" },
        "accuracy": { "type": "integer", "minimum": 0, "maximum": 100 }
      }
    },
    "raw": { "type": "object" },
    "ts": { "type": "string", "format": "date-time" }
  }
}
```

### Finding (Nuclei)
```json
{
  "$id": "https://mcp_scan/schemas/finding.json",
  "type": "object",
  "required": ["finding_id","job_id","target","name","severity","ts"],
  "properties": {
    "finding_id": { "type": "string" },
    "job_id": { "type": "string" },
    "target": { "type": "string" },
    "name": { "type": "string" },
    "severity": { "type": "string", "enum": ["info","low","medium","high","critical"] },
    "cve": { "type": "string" },
    "evidence": { "type": "object" },
    "ts": { "type": "string", "format": "date-time" }
  }
}
```

### ErrorResponse (Unified Error Encapsulation)
```json
{
  "$id": "https://mcp_scan/schemas/error_response.json",
  "type": "object",
  "required": ["code","message","trace_id"],
  "properties": {
    "code": { "type": "string" },
    "message": { "type": "string" },
    "details": { "type": "object" },
    "trace_id": { "type": "string" }
  }
}
```

### LogEntry
```json
{
  "$id": "https://mcp_scan/schemas/log_entry.json",
  "type": "object",
  "required": ["log_id","job_id","level","message","ts"],
  "properties": {
    "log_id": { "type": "string" },
    "job_id": { "type": "string" },
    "level": { "type": "string", "enum": ["DEBUG","INFO","WARN","ERROR"] },
    "message": { "type": "string" },
    "trace_id": { "type": "string" },
    "ts": { "type": "string", "format": "date-time" }
  }
}
```

## Primary Key / Foreign Key / Index Strategy
- **Primary Keys**: `job.job_id`, `task.task_id`, `invocation.invocation_id`, `scan_result.result_id`, `finding.finding_id`, `log_entry.log_id`, `asset.asset_id`
- **Foreign Keys**: `task.job_id → job.job_id`, `invocation.task_id → task.task_id`, `scan_result.job_id → job.job_id`, `finding.job_id → job.job_id`, `log_entry.job_id → job.job_id`
- **Indexes**:
  - Tracing: `invocation.trace_id`, `log_entry.trace_id`
  - Query Hotspots: `scan_result.host+port` (composite); `finding.severity`, `finding.target`
  - Time-series: `ts` field uniformly indexed
- **Sharding (If Applicable)**:
  - Results and logs sharded by month: `scan_result_YYYYMM`, `log_entry_YYYYMM`
  - At scale, shard by `job_id` hash: `db_scan_{job_id % N}`

## Field-Level Constraints
- **Unique**: `asset.host` (unique); `job.job_id` (unique); `task.task_id` (unique)
- **Not Null**: PKs/FKs, critical enum fields (`status`, `severity`)
- **Defaults**: `job.status=queued`, `task.status=queued`, `log_entry.level=INFO`
- **Enum Ranges**: See each JSON Schema `enum`

## Data Lifecycle Strategy
- **KB (Redis)**: Short-term cache and messages, TTL=7 days; async archive to JSON/Columnar storage after expiry
- **Scan Results**: Active period 90 days, then archived; searchable by `job_id` and time range
- **Logs**: Retain 30 days, auto-clean after; error logs permanently archived (compressed monthly)
- **Assets**: Continuously update `last_seen`; mark as `stale` after 180 days inactivity and move to archive

## Traceability
- **Requirement Source**: [PRD.md:L153-L186](file:///d:/PaperDesign/MCP_scan/docs/PRD.md#L153-L186)
- **Structure Reference**:
  - [asset_model.py](file:///d:/PaperDesign/MCP_scan/core/knowledge/asset_model.py) · `commit=COMMIT_TBD`
  - [scan_result_model.py](file:///d:/PaperDesign/MCP_scan/core/knowledge/scan_result_model.py) · `commit=COMMIT_TBD`
