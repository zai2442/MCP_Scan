# Technical Specification Document (TSD) - MCP_scan

## 1. System Architecture

### 1.1. Overview
MCP_scan is a distributed penetration testing system based on the Model Context Protocol (MCP). It decouples the decision-making brain (AI), the coordination heart (Scheduler), and the execution limbs (Recon/Exploit Servers).

```mermaid
graph TD
    subgraph Control_Plane
        CLI[Command Line Client] -->|Task Request| SCH[Scheduler]
        SCH -->|Context| AI[AI Decision Server]
        AI -->|Attack Plan| SCH
    end

    subgraph Execution_Plane
        SCH -->|MCP Call| RS[Recon Server]
        SCH -->|MCP Call| ES[Exploit Server]
        RS -->|Results| KB[(Knowledge Base)]
        ES -->|Evidence| KB
        KB -.->|Telemetry| AI
    end

    subgraph Subsystems
        KB[(Redis / JSON)]
        SEC[Security Sanitizer]
    end

    RS -->|Wrap| Nmap[Nmap / Gobuster]
    ES -->|Wrap| Nuclei / SQLMap
    RS & ES --- SEC
```

### 1.2. Planning & Research Context
> [!NOTE]
> This TSD is grounded in the project's persistent working memory. For ongoing technical progress and detailed research findings, refer to [task_plan.md](task_plan.md) and [findings.md](findings.md).

## 2. Technology Stack
- **Core Engine**: Python 3.10+
- **API Layer**: FastAPI (REST/SSE for MCP)
- **Validation**: Pydantic v2
- **Communication**: MCP Protocol (JSON-RPC over HTTP/SSE)
- **State & Storage**: Redis (Distributed broker & transient cache)
- **Security Tools**: Nmap, Nuclei, Sqlmap, Gobuster

## 3. Requirement Mapping
This section maps the technical components back to the [PRD.md](PRD.md) functional requirements.

| Req ID | Requirement | Technical Component | Design Decision |
| :--- | :--- | :--- | :--- |
| **F1** | MCP-Compliant Tool Wrappers | `servers/recon/`, `servers/exploit/` | Decouples logic from tool syntax via MCP Capabilities. |
| **F2** | Basic Task Scheduling | `core/scheduler/` | Uses DAG-based execution to handle tool dependencies. |
| **F3** | Terminal-Based CLI | `client/cli/` | Python-based CLI for real-time monitoring and control. |
| **F4** | AI-Driven Decomposition | `core/ai_engine/` | AI analyzes goals to generate optimized attack paths. |
| **F5** | Attack Chain Visualization | `core/reporting/` | Generates Mermaid/GraphViz diagrams from execution telemetry. |

## 4. Key Design Decisions

### 4.1. Tool-as-a-Service (TaaS)
- **Decision**: Every security tool is encapsulated as an MCP Capability.
- **Rationale**: Simplifies the AI task. The AI invokes "port_scan" with structured parameters, and the wrapper handles the platform-specific syntax (e.g., Nmap flags).

### 4.2. DAG-based Task Scheduling
- **Decision**: Logic execution is modeled as a Directed Acyclic Graph (DAG).
- **Rationale**: Pentesting is inherently sequential (Recon -> Enum -> Exploit). DAGs ensure dependencies are met and enable parallel scanning where assets are independent.

### 4.3. Command Sanitization Layer
- **Decision**: Mandatory regex-based shell injection filtering in the core security module.
- **Rationale**: Prevents accidental command injection when the AI or user provides malformed inputs to tool wrappers.

## 5. Resilient Workflow (3-Strike Protocol)
To ensure reliability in complex or unstable environments, the execution engine follows a systematic error handling protocol:

1. **Strike 1: Diagnose & Retry** — Read the tool error and attempt a retry with sanitized parameters (e.g., adjusting Nmap timing).
2. **Strike 2: Alternative Tooling** — If the primary tool fails, switch to a fallback capability (e.g., switching from Gobuster to a custom directory fuzzer).
3. **Strike 3: Logic Rethink** — After two tool-level failures, the AI re-evaluates the attack chain based on the failure context.

## 6. Subsystem Detailed Design

### 6.1. Scheduler (The Coordinator)
- **Workflow**:
    1. Receives target from CLI.
    2. Requests decomposition from **AI Server**.
    3. Builds DAG and dispatches tasks to **Recon/Exploit Nodes**.
    4. Aggregates results into the **Knowledge Base**.

### 6.2. AI Decision Engine
- **Attack Chain Builder**: Transforms high-level goals into specific tool sequences.
- **Feedback Loop**: Uses real-time findings to pivot the attack strategy (e.g., if port 80 is found, prioritize web templates).

### 6.3. Knowledge Base (KB)
- **Asset Model**: Centralized state management for all discovered hosts and services.
- **Telemetry**: Stores execution logs and tool outputs for both visualization and AI context.

## 7. Deployment Plan
- **Environment**: Kali Linux (Native/VM)
- **Prerequisites**: Python 3.10+, Redis, and security tools pre-installed in `$PATH`.
- **Modes**: Supports both **Local Mono-node** and **Distributed Control** via MCP over SSE.
