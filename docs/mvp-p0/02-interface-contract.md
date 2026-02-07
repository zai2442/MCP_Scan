# 02. Interface Contract (MVP P0)

**Version**: 1.0
**Status**: Draft
**Format**: OpenAPI 3.0 / JSON Schema

## 1. CLI Command Interface

### Global Options
- `--config <path>`: Path to `config.yaml` (default: `./config.yaml`).
- `--verbose / -v`: Enable debug logging.

### Commands

#### `scan start`
Initialize a new scanning job.
```bash
mcp_scan scan start [OPTIONS]
```
- **Options**:
  - `--target <IP/URL>` (Required): Target to scan.
  - `--tools <tool_list>`: Comma-separated tools (default: "nmap,nuclei").
  - `--idempotency-key <uuid>`: Optional key for safe retries.

#### `scan status`
Check the progress of a job.
```bash
mcp_scan scan status <JOB_ID>
```

#### `report export`
Export results to a file.
```bash
mcp_scan report export <JOB_ID> --format <json|csv> --output <path>
```

#### `node list`
List registered execution nodes.
```bash
mcp_scan node list
```

## 2. API Contract (Node <-> Scheduler)

### 2.1. Node Registration
- **Endpoint**: `POST /api/node/register`
- **Request**:
  ```json
  {
    "node_id": "uuid",
    "hostname": "kali-worker-1",
    "capabilities": ["nmap", "sqlmap"],
    "ip": "192.168.1.50"
  }
  ```
- **Response**: `200 OK`

### 2.2. Heartbeat & Status
- **Endpoint**: `POST /api/node/heartbeat`
- **Request**:
  ```json
  {
    "node_id": "uuid",
    "status": "idle|busy",
    "current_tasks": ["task-uuid-1"]
  }
  ```
- **Response**: `200 OK`

## 3. Data Models (JSON Schema)

### 2.1. Job Object
```json
{
  "type": "object",
  "properties": {
    "job_id": { "type": "string", "format": "uuid" },
    "target": { "type": "string" },
    "status": { "type": "string", "enum": ["pending", "running", "completed", "failed"] },
    "created_at": { "type": "string", "format": "date-time" },
    "tasks": {
      "type": "array",
      "items": { "$ref": "#/definitions/Task" }
    }
  }
}
```

### 2.2. Task Object
```json
{
  "type": "object",
  "properties": {
    "task_id": { "type": "string", "format": "uuid" },
    "tool_name": { "type": "string", "enum": ["nmap", "nuclei"] },
    "status": { "type": "string", "enum": ["pending", "running", "completed", "failed"] },
    "result_summary": { "type": "object" }
  }
}
```

### 2.3. Scan Result (Unified)
```json
{
  "type": "object",
  "properties": {
    "host": { "type": "string" },
    "open_ports": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "port": { "type": "integer" },
          "protocol": { "type": "string" },
          "service": { "type": "string" }
        }
      }
    },
    "vulnerabilities": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "severity": { "type": "string", "enum": ["info", "low", "medium", "high", "critical"] },
          "description": { "type": "string" }
        }
      }
    }
  }
}
```

## 3. Error Codes

| Code | Message | Description |
|------|---------|-------------|
| `E1001` | `INVALID_TARGET` | Target format is incorrect or on blacklist. |
| `E2001` | `TOOL_NOT_FOUND` | Requested tool is not installed or configured. |
| `E3001` | `SCHEDULER_FULL` | Max concurrent jobs reached (default: 10). |
| `E5001` | `INTERNAL_ERROR` | Unhandled exception in system core. |
