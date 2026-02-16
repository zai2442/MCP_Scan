# Job Result System

Containerized MySQL system for storing and exporting job results.

## Quick Start

1.  **Start Services**:
    ```bash
    docker-compose up -d
    ```

2.  **View Logs**:
    ```bash
    docker-compose logs -f
    ```

3.  **Run Tests**:
    ```bash
    npm test
    ```

4.  **Load Test**:
    Ensure `load-test-job` exists in DB.
    ```bash
    k6 run scripts/load.js
    ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | Database Host | `db` |
| `DB_USER` | Database User | `root` |
| `DB_PASSWORD` | Database Password | `root` |
| `DB_NAME` | Database Name | `job_result_db` |
| `PORT` | API Port | `3000` |
| `EXPORTS_DIR` | Export Directory | `/exports` |

## Naming Conventions

-   **Job ID**: Alphanumeric, hyphen, underscore, 1-64 characters. Regex: `^[a-zA-Z0-9_-]{1,64}$`
-   **Export File**: `{job_id}_result.json`
-   **Export Location**: Container internal `/exports/` (mapped to host `./exports`)

## Slow Query Log

Slow queries (>1s) are logged to stdout and can be viewed via `docker-compose logs db`.
