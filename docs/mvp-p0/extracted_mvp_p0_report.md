# Extracted MVP P0 Report

**Date**: 2026-02-07
**Status**: Analysis Complete

## 1. MVP P0 Core Functional Checklist (Based on PRD)

| ID | Feature Name | Description | Input | Output | Acceptance Criteria |
|----|--------------|-------------|-------|--------|---------------------|
| P0-01 | **MCP Tool Wrappers** | Standardized execution of Nmap & Nuclei. | JSON Params (`target`, `ports`) | Structured JSON (Open Ports, Vulns) | - Sanitized input<br>- JSON output<br>- No raw shell (unless authorized) |
| P0-02 | **Basic Scheduling** | Sequential execution (Task A -> Task B). | Job Definition (DAG/List) | Execution Logs & Results | - Results passed to next task<br>- Persistence |
| P0-03 | **Terminal CLI** | Command line interface for control. | `mcp_scan start ...` | Real-time Status Table | - Async status updates<br>- Rich UI |

## 2. Code Mapping & Gap Analysis

### P0-01: MCP Tool Wrappers
- **Requirement**: Specific wrappers for Nmap/Nuclei with structured parsing.
- **Existing Code**: `KaliToolsClient.execute_command` (Generic Shell).
- **Gap**: **High**. Existing code allows running `nmap` but does *not* provide specific wrappers or structured parsing. It is a "Remote Shell" primitive.
- **Action**: Extract `KaliToolsClient` as a base for the "Transport Layer", but must implement `NmapWrapper` and `NucleiWrapper` on top of it.

### P0-02: Basic Scheduling
- **Requirement**: Job queue and state management.
- **Existing Code**: `CommandExecutor` (Threaded execution with timeout).
- **Gap**: **Medium**. `CommandExecutor` handles *single* command execution well (timeout, stdout reading), but lacks the *orchestration* logic (DAG/Sequence).
- **Action**: Extract `CommandExecutor` to serve as the "Local Node Executor".

### P0-03: Terminal CLI
- **Requirement**: Click + Rich based CLI.
- **Existing Code**: None. `kali_server.py` is a Flask server; `mcp_server.py` is an MCP agent.
- **Gap**: **Complete**. Needs fresh implementation.
- **Action**: No extraction possible.

## 3. Extracted Components

### Component A: `mvp_p0_feature_base` (Execution Engine)
- **Source**: `MCP_kali/MCP-Kali-Server/kali_server.py`
- **Class**: `CommandExecutor`
- **Justification**: Solid implementation of threaded subprocess management with timeouts. Reusable for the "Executor" part of the Scheduler.

### Component B: `mvp_p0_feature_transport` (MCP Client)
- **Source**: `MCP_kali/MCP-Kali-Server/mcp_server.py`
- **Class**: `KaliToolsClient`
- **Justification**: Provides the HTTP bridge to the execution engine. Reusable for the "Node Manager" in Distributed Distributed mode.

## 4. Next Steps
1.  **Refactor**: Wrap `CommandExecutor` into `servers.base.execution`.
2.  **Implement**: Build `NmapWrapper` inheriting from a new `ToolBase`, utilizing `CommandExecutor` internally.
3.  **Create**: `client/cli.py` from scratch.
