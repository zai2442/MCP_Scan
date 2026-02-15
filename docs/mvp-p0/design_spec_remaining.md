# Design Specification: Remaining MVP-P0 Features

**Version**: 1.0
**Date**: 2026-02-15
**Status**: Draft

## 1. Overview
This document outlines the detailed design for the Scheduler, Knowledge Base, and CLI components of the MCP_scan MVP-P0.

## 2. Core Architecture (Refined)

### 2.1 Knowledge Base (`core/models.py`)
Uses Pydantic V2 for strict validation.

#### Entities
*   **Target**: The input scope (IP/URL).
*   **Asset**: A discovered entity.
    *   `Host`: ip, hostname, os.
    *   `Service`: port, protocol, product, version.
    *   `Vulnerability`: title, severity, description, evidence.
*   **Job**: A scan session.
    *   `id`: UUID.
    *   `status`: PENDING, RUNNING, COMPLETED, FAILED.
    *   `tasks`: List[Task].
*   **Task**: A specific tool execution unit.
    *   `id`: UUID.
    *   `tool`: Tool name (e.g., "nmap").
    *   `params`: Dict of arguments.
    *   `dependencies`: List[TaskID].

### 2.2 Scheduler Engine (`core/scheduler.py`)
The Scheduler is responsible for the "Intelligent Reconnaissance" logic.

#### Components
1.  **DAG Builder**:
    *   Input: `Target`, `Profile` (Fast/Deep).
    *   Logic:
        *   Step 1: Create `NmapTask`.
        *   Step 2: Create `GobusterTask` (depends on Nmap).
        *   Step 3: Create `NucleiTask` (depends on Nmap).
    *   Note: In MVP, dependencies are static. Dynamic expansion (creating tasks based on Nmap *results*) is the goal for v1.1, but for v1.0, we can implement a simplified "Phase 2" expansion or just static chaining if results are available.
    *   *Decision*: We will implement **Dynamic Task Generation**. The Scheduler will have an `on_task_complete` hook. If Nmap finds Port 80, it *dynamically* adds a Nuclei task.

2.  **Local Executor**:
    *   Uses `asyncio.Queue` for task management.
    *   Wraps `CommandExecutor` to run tools.
    *   Updates `Job` state.

#### State Machine
*   `Idle` -> `Scanning` -> `Analyzing` -> `Done`.

### 2.3 CLI (`cli.py`)
Built with `click` and `rich`.

#### Commands
*   `scan start`:
    *   Args: target.
    *   Action: Init Job, Start Scheduler Loop (Async), Stream logs.
*   `scan status`:
    *   Args: job_id.
    *   Action: Read Job state from memory/file.

## 3. Interface Design

### 3.1 Python API
```python
class Scheduler:
    async def start_scan(self, target: str, profile: str = "fast") -> Job: ...
    async def get_status(self, job_id: str) -> Job: ...
```

### 3.2 Error Codes (`core/errors.py`)
| Code | Name | Description |
|------|------|-------------|
| E1001 | INVALID_TARGET | Target validation failed |
| E2001 | TOOL_EXEC_FAIL | Tool exited with non-zero code |
| E3001 | CONFIG_ERROR | Missing config file or key |

## 4. Sequence Diagram (Simplified)

```mermaid
sequenceDiagram
    User->>CLI: scan start 10.0.0.1
    CLI->>Scheduler: create_job("10.0.0.1")
    Scheduler->>DAGBuilder: build_initial_tasks()
    DAGBuilder-->>Scheduler: [NmapTask]
    Scheduler->>Executor: run(NmapTask)
    Executor->>NmapTool: execute()
    NmapTool-->>Executor: Result(Port 80 Open)
    Executor-->>Scheduler: TaskComplete
    Scheduler->>DAGBuilder: process_result(Result)
    DAGBuilder-->>Scheduler: [NucleiTask, GobusterTask]
    Scheduler->>Executor: run(NucleiTask)
    ...
```
