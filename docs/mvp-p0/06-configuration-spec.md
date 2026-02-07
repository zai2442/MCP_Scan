# 06. Configuration Specification (MVP P0)

**Version**: 1.0
**Status**: Draft

## 1. Overview
The `config.yaml` file is the central source of truth for the MCP_scan node. It defines the node's identity, capable tools, network settings, and logging preferences.

## 2. Structure

```yaml
# Identity of this execution node
node:
  id: "auto-generated-uuid"  # Leave empty to auto-generate on startup
  hostname: "kali-worker-1"
  tags: ["gpu", "high-bandwidth"]

# Network Configuration
network:
  host: "0.0.0.0"
  port: 8080
  scheduler_url: "http://localhost:8000"  # URL of the central scheduler
  api_key: "secure-api-key-here"

# Tool Paths (Override auto-detection)
tools:
  nmap: "/usr/bin/nmap"
  gobuster: "/usr/local/bin/gobuster"
  sqlmap: "/usr/bin/sqlmap"
  metasploit: "/usr/bin/msfconsole"
  # Add other tools as needed...

# Logging Settings
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "logs/mcp_scan.log"
  format: "json" # text or json

# Security Limits
limits:
  max_concurrent_tasks: 5
  max_runtime_seconds: 3600
  allowed_networks: ["192.168.0.0/16", "10.0.0.0/8"]
```

## 3. Validation Rules
- **tools**: Paths must be executable. If a tool is missing, the node initiates but marks that capability as unavailable.
- **network**: `port` must be > 1024 (unless root).
- **limits**: `allowed_networks` is a mandatory whitelist for safety.
