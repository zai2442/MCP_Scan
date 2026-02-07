# 05. Changelog & Migration (Prototype -> MVP P0)

**Version**: 1.0
**Date**: 2026-02-07

## Overview
This document tracks the structural and functional changes from the initial `MCP_kali` prototype to the formalized MVP P0 architecture.

## Summary of Changes

### 1. Architecture Refactoring
- **Removed**: Flat structure (`kali_server.py`, `mcp_server.py` in root).
- **Added**: Modular structure (`core/`, `servers/`, `client/`).
- **Reason**: Separation of concerns, scalability, and alignment with `PROJECT_STRUCTURE_SIMPLIFIED.md`.

### 2. Functional Changes

| Feature | Prototype (`MCP_kali`) | MVP P0 | PRD Reference |
|---------|------------------------|--------|---------------|
| **Execution** | Generic `execute_command` (Remote Shell) | Specific Tool Wrappers (Nmap, Nuclei) | Feature 1 |
| **Parsing** | Raw stdout/stderr | Structured JSON Parsing | Feature 1 |
| **Scheduling**| None (Direct API call) | DAG/Sequential Scheduler | Feature 2 |
| **Interface** | HTTP API (Flask) | CLI (Click) + Internal MCP API | Feature 3 |
| **Config** | Env Vars / Hardcoded | `config.yaml` | Non-Functional |

### 3. Deleted / Deprecated Items
- **File**: `MCP-Kali-Server/kali_server.py`
    - **Status**: Deprecated.
    - **Migration**: Logic moved to `servers/base/execution.py` (planned).
- **File**: `MCP-Kali-Server/mcp_server.py`
    - **Status**: Deprecated.
    - **Migration**: Replaced by `core/mcp/protocol.py` and `servers/*/`.

## Compatibility Guide
- **API**: The old Flask API (`POST /execute`) is **NOT** compatible with the new MCP-based architecture.
- **Data**: No persistent data existed in prototype, so no migration needed.
- **Clients**: Any scripts calling the old API must be rewritten to use the new `mcp_scan` CLI or SDK.
