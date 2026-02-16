# 01. Functional Specification (MVP P0)

**Version**: 1.0
**Status**: Approved
**Related PRD**: [PRD.md](../PRD.md) (Lines 153-186)

## 1. Overview
This document defines the functional specifications for the Phase 1 MVP of MCP_scan. The primary goal is to establish a modular, distributed scanning framework using the Model Context Protocol (MCP).

## 2. Functional Capabilities

### 2.1. MCP Tool Wrappers (Feature 1)
**Goal**: Encapsulate Nmap and Nuclei as standardized MCP tools.

#### 2.1.1. Port Scanning (Nmap)
- **Description**: Perform port discovery and service version detection.
- **Inputs**:
  - `target` (string): IPv4, IPv6, or Hostname.
  - `ports` (string, optional): "top-100", "1-65535", or list "80,443". Default: "top-1000".
  - `timing` (string, optional): "T3" (default), "T4".
- **Outputs**:
  - Structured JSON containing open ports, service names, and versions.
- **Business Rules**:
  - Must validate target against whitelist/blacklist (if configured).
  - Must sanitize all CLI arguments to prevent injection.
  - Timeout: 5 minutes per host.

#### 2.1.2. Vulnerability Scanning (Nuclei)
- **Description**: Run template-based vulnerability scans.
- **Inputs**:
  - `target` (string): URL (http/https).
  - `tags` (list, optional): e.g., ["cve", "misconfig"].
- **Outputs**:
  - List of findings with Severity (Info, Low, Medium, High, Critical).
- **Business Rules**:
  - Only run on targets that have been confirmed as "live" by Nmap.
  - Rate limit: 50 requests/second.

#### 2.1.3. Web Directory Enumeration (Gobuster)
- **Description**: Enumerate directories and files on web servers.
- **Inputs**:
  - `url` (string): Target URL.
  - `wordlist` (string): Path to wordlist (default: `/usr/share/wordlists/dirb/common.txt`).
  - `threads` (integer, optional): Number of threads (default: 10).
- **Outputs**:
  - List of discovered paths with status codes (200, 301, 403).
- **Business Rules**:
  - Only run if port 80/443 is open.

#### 2.1.4. SQL Injection Testing (SQLMap)
- **Description**: Detect and exploit SQL injection flaws.
- **Inputs**:
  - `url` (string): Target URL with parameters.
  - `batch` (boolean): Run in non-interactive mode (default: true).
  - `level` (integer, optional): 1-5 (default: 1).
  - `risk` (integer, optional): 1-3 (default: 1).
- **Outputs**:
  - Injection points, database type, and version.
- **Business Rules**:
  - Requires user approval for level > 3 or risk > 1.

#### 2.1.5. Exploit Execution (Metasploit)
- **Description**: Execute specific exploit modules.
- **Inputs**:
  - `module` (string): e.g., `exploit/windows/smb/ms17_010_eternalblue`.
  - `options` (object): Module-specific parameters (RHOSTS, LHOST, etc.).
- **Outputs**:
  - Session ID (if successful), execution logs.
- **Business Rules**:
  - Strict whitelist of allowed modules in MVP.
  - Requires explicit confirmation via CLI.

#### 2.1.6. Password Cracking (Hydra)
- **Description**: Online password brute-forcing.
- **Inputs**:
  - `target` (string): IP address.
  - `service` (string): ssh, ftp, http-post-form.
  - `user_list` (string): Path to username list.
  - `pass_list` (string): Path to password list.
- **Outputs**:
  - Valid credentials (username:password).
- **Business Rules**:
  - Max limits on thread count to prevent DoS.

### 2.2. Distributed Task Scheduling (Feature 2)
**Goal**: Coordinate execution across local and remote nodes.

#### 2.2.1. Node Communication Protocol
- **Architecture**: Hub-and-Spoke. Scheduler (Hub) -> Execution Nodes (Spokes).
- **Protocol**: JSON-RPC over HTTPs.
- **Heartbeat**: Nodes report health every 30s (`POST /node/heartbeat`).

#### 2.2.2. Task Dispatching
- **Logic**:
  1. Scheduler selects best available node (based on load/tags).
  2. Sends `TaskPayload` to Node.
  3. Node spawns subprocess for tool execution.
  4. Node streams stdout/stderr back to Scheduler via WebSocket/SSE.

### 2.2. Basic Task Scheduling (Feature 2)
**Goal**: Coordinate sequential execution of tools.

#### 2.2.1. Sequential Workflow
- **Logic**: `Job` -> `Task A (Recon)` -> `Task B (Exploit)`.
- **Data Flow**: Output of Task A (e.g., Open Ports) becomes Input of Task B (e.g., Target URL).
- **State Management**:
  - Job Status: `PENDING` -> `RUNNING` -> `COMPLETED` / `FAILED`.
  - Persistence: Local JSON files (MVP) or Redis (Target).

### 2.3. Terminal CLI (Feature 3)
**Goal**: User interaction via command line.

#### 2.3.1. Scan Management
- **Commands**:
  - `mcp_scan start --target <IP> --profile <fast|deep>`
  - `mcp_scan status <JOB_ID>`
  - `mcp_scan stop <JOB_ID>`
- **Output**:
  - Rich-formatted tables for status.
  - Real-time log streaming.

## 3. Exception Handling

| Error Category | Scenario | Strategy |
|----------------|----------|----------|
| **Validation** | Invalid IP/URL format | Reject request immediately (HTTP 400). |
| **Execution** | Tool timeout (Nmap hangs) | Kill process, retry once, then mark Task as FAILED. |
| **System** | Scheduler crash | On restart, load persisted state and resume PENDING jobs. |
| **Security** | Command injection attempt | Block request, log security event, ban user session (if applicable). |

## 4. Rollback Strategy
- **Configuration**: Support `--safe-mode` to run only non-intrusive scans.
- **State**: If database corrupts, fallback to empty state (loss of history, but system functional).
