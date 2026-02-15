# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-02-15 (MVP P0)

### Added
- **Feature 1: Tool Support**
  - Implemented wrappers for Nmap, Gobuster, Nuclei, SQLMap, Hydra, Metasploit.
  - Standardized `CommandExecutor` with timeout and logging.
- **Feature 2: Task Scheduler**
  - AsyncIO-based Scheduler engine.
  - DAG-based task execution (Nmap findings trigger web scans).
  - `Job` and `Task` Pydantic models.
- **Feature 3: CLI Interface**
  - `scan start`, `scan status`, `report export` commands.
  - Integrated `rich` for terminal UI.
- **Testing & Quality**
  - Unit tests for Scheduler and Models.
  - Integration test for full scan flow.
  - Performance benchmark script (verified 50+ jobs/sec throughput).
- **Documentation**
  - Updated README with usage instructions.
  - Created Design Specification for MVP.
  - Created Performance Report.

### Changed
- Refactored project structure to `src/mcp_scan`.
- Consolidated dependency management in `requirements.txt`.
