# Product Requirements Document (PRD) - MCP_scan

## 1. Project Overview

### Project Identity
- **Project Name**: MCP_scan
- **Version**: 1.0 (Simplified MVP)
- **Document Owner**: Security Engineering Team
- **Last Updated**: 2026-02-07

### Vision Statement
To create a lightweight, modular, AI-orchestrated distributed penetration testing platform that standardizes security tool interactions via the MCP protocol. Focused on local and VM-based environments, it empowers security professionals to automate reconnaissance and exploitation tasks using a simplified, efficient architecture.

### Problem Statement
**Current State**: Security professionals struggle with manually chaining disparate tools and managing context across complex engagements.
**Pain Points**:
- **Tool Fragmentation**: 10+ standard tools (Nmap, SQLMap, etc.) with different syntaxes.
- **Context Loss**: Findings from one tool aren't automatically fed into the next.
- **Complex Coordination**: Validating distributed nodes requires manual SSH hopping.

### Solution Summary
A local-first, distributed scanning system where:
1.  **AI Decomposes Goals** into executable task DAGs.
2.  **MCP Servers** encapsulate standard Kali tools (Nmap, Metasploit, etc.) as callable capabilities.
3.  **Core Scheduler** manages execution flow across local or networked VM nodes.

## 2. Target Audience
- **Penetration Testers**: Automate boring recon; focus on logic bugs.
- **CTF Players**: Rapidly solve "easy" boxes with AI assistance.
- **Security Researchers**: Prototype new attack chains using Python-based MCP wrappers.

## 3. User Stories & Use Cases

### Core User Stories

#### Story 1: Intelligent Reconnaissance
- **As a** Pentester
- **I want to** say "Scan 192.168.1.10 for web vulnerabilities"
- **So that** the system automatically runs Nmap -> Gobuster -> Nikto -> Nuclei without my intervention.
- **Acceptance Criteria**:
  - [ ] AI selects correct tool chain.
  - [ ] Nmap finds port 80/443.
  - [ ] Gobuster/Nikto/Nuclei are triggered only for open web ports.
  - [ ] Results are aggregated in a unified report.

#### Story 2: Exploitation & Verification
- **As a** Red Teamer
- **I want to** use SQLMap and Hydra to verify suspected vulnerabilities
- **So that** I don't waste time on false positives.
- **Acceptance Criteria**:
  - [ ] Can trigger `sqlmap_scan` on a specific URL parameter.
  - [ ] Can trigger `hydra_attack` on found SSH/FTP services.
  - [ ] Evidence (e.g., dumped DB version, successful login) is captured.

#### Story 3: Custom Tool Integration
- **As a** Developer
- **I want to** add a wrapper for a custom script
- **So that** the AI can use it in future scans.
- **Acceptance Criteria**:
  - [ ] Adding a python file to `servers/recon/capabilities/` makes it available to the AI.

## 4. Functional Requirements

### Feature 1: Comprehensive Tool Support (MCP_kali Integration)
> **Core Value**: Direct access to industry-standard tools via MCP.
- **Reconnaissance**:
  - `nmap` (Port/Service Discovery)
  - `gobuster` (Dir/DNS/VHost enumeration)
  - `dirb` (Web Content Scanner)
  - `enum4linux` (SMB/Windows Enumeration)
- **Vulnerability Analysis**:
  - `nikto` (Web Server Scanner)
  - `wpscan` (WordPress Security Scanner)
  - `nuclei` (Template-based Scanner)
- **Exploitation**:
  - `sqlmap` (Automated SQL Injection)
  - `hydra` (Online Password Cracking)
  - `john` (Offline Password Cracking)
  - `metasploit` (Framework execution)

### Feature 2: Simplified Task Scheduling
- **DAG-Based Execution**: Tasks depend on assets (e.g., "Run Nikto ONLY IF Port 80 is open").
- **Local Distributed**: capable of dispatching tasks to:
  - Localhost (subprocess)
  - Remote SSH nodes (via `command_executor` bridge)

### Feature 3: Developer-Friendly CLI
- **Tech**: Built with **Rich** (for beautiful output) and **Click** (for robust commands).
- **Capabilities**:
  - `scan start <target>`
  - `scan status <id>`
  - `report export <id>`

## 5. Non-Functional Requirements

### Performance
- **Responsiveness**: CLI updates status every 1s.
- **Concurrency**: Support 5-10 concurrent tool executions on a standard laptop.

### Deployment
- **Method**: Local Python process or Docker Compose.
- **Config**: Simple `config.yaml` for tool paths and API keys.

### Security
- **Command Injection**: All tool arguments passed through strict Pydantic models; NO raw shell strings unless explicitly authorized (e.g., `execute_command` requires admin flag).

## 6. Out of Scope
- **Web UI**: CLI only for this version.
- **Cloud Orchestration**: No K8s/Terraform support.
- **SaaS Features**: No multi-tenant user management or billing.
