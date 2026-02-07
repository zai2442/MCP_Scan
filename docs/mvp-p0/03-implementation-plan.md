# 03. Implementation Plan (MVP P0)

**Version**: 1.0
**Status**: Planned

## 1. Migration Strategy
Current codebase (`MCP_kali`) is a flat prototype. The goal is to migrate to the Modular Architecture defined in `PROJECT_STRUCTURE_SIMPLIFIED.md`.

### Phase 1: Foundation (Week 1)
- [ ] **Init**: Initialize new directory structure (`core/`, `servers/`, `client/`).
- [ ] **Config**: Implement `config.yaml` loading and Pydantic validation.
- [ ] **Core**: Implement `core/mcp/` (Protocol adaptation from `mcp_server.py`).

### Phase 2: Core Capabilities (Week 2)
- [ ] **Recon Server**:
    - Create `servers/recon/recon_server.py`.
    - Implement wrappers: `nmap`, `gobuster`, `dirb`, `enum4linux`.
- [ ] **Exploit Server**:
    - Create `servers/exploit/exploit_server.py`.
    - Implement wrappers: `nuclei`, `sqlmap`, `hydra`, `metasploit`, `john`, `wpscan`.
    - Implement `nikto` wrapper.

### Phase 3: Distributed Orchestration (Week 3)
- [ ] **Scheduler Core**: Implement `core/scheduler/` (DAG Builder, Executor).
- [ ] **Node Manager**: Implement `core/communication/node_manager.py` (Registration, Heartbeat).
- [ ] **Message Router**: Implement `core/communication/message_router.py` (JSON-RPC over HTTPs).
- [ ] **Data**: Implement `core/knowledge/` models (Asset, Vuln).

### Phase 4: Interface & Polish (Week 4)
- [ ] **CLI**: Build `client/cli.py` using Click & Rich.
- [ ] **Integration**: End-to-end testing of `CLI -> Scheduler -> Server -> Tool`.

## 2. Task Breakdown

| ID | Task Name | Priority | Est. Hours | Owner | Dependencies |
|----|-----------|----------|------------|-------|--------------|
| T1.1 | Project Skeleton Setup | High | 4 | Lead | None |
| T1.2 | Config Module | High | 4 | Dev | T1.1 |
| T2.1 | Nmap Wrapper Impl | High | 8 | Dev | T1.2 |
| T2.2 | Nuclei Wrapper Impl | High | 8 | Dev | T1.2 |
| T2.3 | SQLMap Wrapper Impl | High | 8 | Dev | T1.2 |
| T2.4 | Metasploit Wrapper Impl | High | 12 | Dev | T1.2 |
| T2.5 | Other Tool Wrappers (Hydra, etc.) | Medium | 16 | Dev | T1.2 |
| T3.1 | Distributed Scheduler Core | Critical | 16 | Lead | T2.* |
| T3.2 | Node Communication (RPC/Heartbeat) | Critical | 12 | Lead | T1.2 |
| T4.1 | CLI "Start Scan" Command | Medium | 8 | Dev | T3.1 |

## 3. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Tool Versioning** | High | Medium | Containerize tools (Docker) or strict version checks on startup. |
| **Concurrency Issues** | Medium | High | Use `asyncio` primitives and file locking for local state. |
| **Migration Complexity** | Medium | Low | `MCP_kali` is small; rewrite is cleaner than refactor. |

## 4. Milestones
- **M1 (Day 7)**: Hello World from Modular Architecture.
- **M2 (Day 14)**: Nmap & Nuclei running via MCP calls.
- **M3 (Day 28)**: Full End-to-End Scan via CLI (MVP Release).
