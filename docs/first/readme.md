**# Phase 1: MVP / Core Automation (P0) Implementation Guide Index**



\- ***\*Requirement Source\****: [PRD.md:L153-L186](file:///d:/PaperDesign/MCP_scan/docs/PRD.md#L153-L186)

\- ***\*Technical Reference\****: [TSD.md](file:///d:/PaperDesign/MCP_scan/docs/TSD.md) · [PROJECT_STRUCTURE_SIMPLIFIED.md](file:///d:/PaperDesign/MCP_scan/docs/PROJECT_STRUCTURE_SIMPLIFIED.md)

\- ***\*Traceability Placeholder\****: `commit=COMMIT_TBD`

## Feature Specifications
- **Feature 1 · MCP Tool Wrappers (Nmap / Nuclei)**  
  [feature-1-mcp-tool-wrappers.md](file:///d:/PaperDesign/MCP_scan/docs/mvp-p0/feature-1-mcp-tool-wrappers.md)
- **Feature 2 · Basic Task Scheduling (Sequential Execution, Result Propagation)**  
  [feature-2-basic-task-scheduling.md](file:///d:/PaperDesign/MCP_scan/docs/mvp-p0/feature-2-basic-task-scheduling.md)
- **Feature 3 · Terminal CLI (Scan Initiation, Real-time Progress, Result Export)**  
  [feature-3-terminal-cli.md](file:///d:/PaperDesign/MCP_scan/docs/mvp-p0/feature-3-terminal-cli.md)
- **Data Models (ER Diagram + JSON Schema + Constraints/Indexes/TTL)**  
  [data-models.md](file:///d:/PaperDesign/MCP_scan/docs/mvp-p0/data-models.md)
- **API Reference (RESTful + Error Encapsulation + Idempotency/Rate Limiting/Caching + Versioning)**  
  [api-reference.md](file:///d:/PaperDesign/MCP_scan/docs/mvp-p0/api-reference.md)

## Overview (Mermaid)
```mermaid
flowchart LR
    CLI["CLI: mcp_scan --target <IP> --tools nmap,nuclei"]
    SCH[Scheduler]
    RS[Recon Server\n(Nmap wrapper)]
    ES[Exploit Server\n(Nuclei wrapper)]
    KB[(Knowledge Base\nRedis/JSON)]

    CLI -->|Create Job| SCH
    SCH -->|Invoke MCP| RS
    SCH -->|Invoke MCP| ES
    RS -->|Recon Results| KB
    ES -->|Vuln Findings| KB
    SCH -->|Aggregate + Logs| KB
    CLI -->|Progress/Results| KB
```

## Bi-directional Traceability
- Each file provides links to the requirement source and technical solution files (with line numbers or commit placeholders).
- Interfaces, models, and error codes are centrally defined in the "API Reference" and "Data Models" files and referenced in each Feature document.
- Code implementation correspondence follows the project structure:
  - Nmap Wrapper: `servers/recon/tools/nmap_wrapper.py` (Reference Structure)
  - Nuclei Wrapper: `servers/exploit/tools/nuclei_wrapper.py` (Reference Structure)
  - CLI: `client/cli.py` (Reference Structure)
  - Scheduler: `core/scheduler/` (Reference Structure)
  - If code is not yet committed, it is marked with a commit placeholder: `commit=COMMIT_TBD`.