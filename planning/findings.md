# Findings & Research

## PRD P0 Requirements (Analysis)
Based on `docs/PRD.md` (Features 1-3) and `docs/mvp-p0/*.md`:
1.  **Feature 1: MCP Tool Wrappers**:
    - Needs structured Nmap/Nuclei wrappers.
    - Input: JSON params. Output: JSON structured results.
    - Current `MCP_kali`: Generic shell execution. **GAP**: Missing specific wrappers and parsing.
2.  **Feature 2: Basic Task Scheduling**:
    - Needs Sequential/DAG scheduling.
    - Needs Redis for state (optional in MVP but architecture should support it).
    - Current `MCP_kali`: No scheduler, direct execution. **GAP**: Missing scheduler module.
3.  **Feature 3: Terminal CLI**:
    - Needs `mcp_scan` CLI with `scan start`, `status`, `report`.
    - Current `MCP_kali`: No CLI, just server scripts. **GAP**: Missing Client/CLI module.

## Existing Implementation (`MCP_kali`)
- **Structure**: Flat, script-based (`kali_server.py`, `mcp_server.py`).
- **Tech Stack**: Flask, subprocess, fastmcp.
- **Functionality**:
    - Exposes a Flask API to run shell commands.
    - Connects as an MCP server.
    - Basic timeout management.
- **Assessment**: This is a "v0" prototype. It allows "Remote Code Execution" but lacks the "Intelligent orchestration" and "Structured Data" required by P0.

## Structure Alignment (`PROJECT_STRUCTURE_SIMPLIFIED.md`)
- **Target**:
    - `core/`: Protocol, Scheduler, Knowledge.
    - `servers/`: Recon, Exploit, AI.
    - `client/`: CLI, SDK.
- **Action**:
    - `kali_server.py` logic (subprocess management) -> moves to `servers/base/mcp_server_base.py` or `core/scheduler/distributed_executor.py`.
    - `mcp_server.py` -> superseded by `servers/*/` modular servers.
    - `CommandExecutor` class -> useful for `local` execution mode in Scheduler.

## Mapping Table (Implemented vs PRD)
| PRD Feature | Existing Code | Status | Action |
|-------------|---------------|--------|--------|
| MCP Protocol | `mcp_server.py` (FastMCP) | Partial | Refactor into `core/mcp/protocol.py` |
| Nmap Wrapper | None (Generic `execute_command`) | Missing | Create `servers/recon/tools/nmap_wrapper.py` |
| Nuclei Wrapper| None | Missing | Create `servers/exploit/tools/nuclei_wrapper.py` |
| Scheduler | None | Missing | Create `core/scheduler/` |
| CLI | None | Missing | Create `client/cli.py` |
| Config | Hardcoded / Env Vars | Partial | Move to `config.yaml` & `core/config.py` |
