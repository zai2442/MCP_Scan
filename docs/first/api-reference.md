# API Reference · MVP P0 (Internal Interface)

- **Related Requirement**: [PRD.md:L153-L186](file:///d:/PaperDesign/MCP_scan/docs/PRD.md#L153-L186)
- **Technical Basis**: RESTful API design [TSD.md:L80-L86](file:///d:/PaperDesign/MCP_scan/docs/TSD.md#L80-L86)
- **Traceability Placeholder**: `commit=COMMIT_TBD`

## Global Standards
- **Base URL**: `/api/v1`
- **Content-Type**: `application/json`
- **Auth**: None (Local Only) / API Key (Future)
- **Error Response**: See `ErrorResponse` in [Data Models](data-models.md)

## 1. Job Management (Jobs)

### Create Job
- **Endpoint**: `POST /jobs`
- **Description**: Submit a new scan task. Supports idempotency via `job_id`.
- **Request Body**:
  ```json
  {
    "job_id": "uuid-v4",
    "target": "192.168.1.1",
    "tools": ["nmap", "nuclei"],
    "options": {
      "port_range": "top-100",
      "severity_threshold": "medium"
    }
  }
  ```
- **Response**: `201 Created`
  ```json
  {
    "job_id": "uuid-v4",
    "status": "queued",
    "eta_seconds": 300
  }
  ```

### Get Job Status
- **Endpoint**: `GET /jobs/{job_id}`
- **Description**: Poll task progress and current stage.
- **Response**: `200 OK`
  ```json
  {
    "job_id": "uuid-v4",
    "status": "running",
    "progress": 45,
    "current_stage": "exploit.nuclei_scan",
    "events": [
      {"ts": "...", "level": "INFO", "message": "Port scan completed. Open: 80, 443"}
    ]
  }
  ```

### Cancel Job
- **Endpoint**: `POST /jobs/{job_id}/cancel`
- **Description**: Terminate a running task.
- **Response**: `200 OK` (Async request accepted)

## 2. Result Query (Results)

### Get Job Results
- **Endpoint**: `GET /jobs/{job_id}/results`
- **Query Params**:
  - `format`: `json` (default) | `csv`
  - `filter_severity`: `medium,high,critical` (optional)
- **Response**: `200 OK`
  ```json
  {
    "summary": {"hosts": 1, "vulns": 2},
    "recon": [...],
    "findings": [...]
  }
  ```

## 3. System Health (Health)

### Health Check
- **Endpoint**: `GET /health`
- **Response**: `200 OK`
  ```json
  {
    "status": "healthy",
    "components": {
      "scheduler": "up",
      "redis": "up",
      "mcp_nmap": "up"
    },
    "version": "0.1.0"
  }
  ```

## Error Handling Standards
- **400 Bad Request**: Invalid parameters (e.g., target format error).
- **404 Not Found**: Job ID does not exist.
- **409 Conflict**: Idempotency conflict (same ID, different parameters).
- **429 Too Many Requests**: Rate limiting (if applicable).
- **500 Internal Server Error**: Unhandled system exception.

## Idempotency Mechanism
- Clients MUST generate `job_id` (UUIDv4) and include it in the `POST /jobs` request.
- If the server receives an existing `job_id`:
  - If parameters match: Return existing job status (200 OK).
  - If parameters differ: Return 409 Conflict.

## Rate Limiting & Quotas (Local)
- **Max Concurrent Jobs**: 10 (default configuration).
- **Max History**: 1000 Jobs (older jobs auto-archived).

## Traceability
- **Requirement Source**: [PRD.md:L153-L186](file:///d:/PaperDesign/MCP_scan/docs/PRD.md#L153-L186)
- **Code Location (Reference)**:
  - [api_server.py](file:///d:/PaperDesign/MCP_scan/server/api_server.py) · `commit=COMMIT_TBD`
