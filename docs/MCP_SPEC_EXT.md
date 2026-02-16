# MCP Protocol Extension for Penetration Testing Scenarios

## 概述

本文档定义了 MCP (Model Context Protocol) 在渗透测试场景中的扩展规范，旨在确保异构节点（Recon、Exploit、AI）之间的语义一致性和通信标准化。

---

## 核心扩展原则

### 1. 语义标准化
- 统一的资源描述格式
- 标准化的工具参数定义
- 一致的提示词结构

### 2. 类型安全
- 严格的 JSON Schema 验证
- 明确的数据类型约束
- 完整的错误处理机制

### 3. 可扩展性
- 模块化的能力定义
- 灵活的参数扩展机制
- 向后兼容的版本控制

---

## Resource 扩展规范

### 扫描快照资源 (ScanSnapshot)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Penetration Testing Scan Snapshot",
  "description": "扫描快照资源，包含目标资产和发现的服务信息",
  "type": "object",
  "properties": {
    "uri": {
      "type": "string",
      "pattern": "^scan://[a-f0-9-]{36}$",
      "description": "扫描快照的唯一标识符"
    },
    "name": {
      "type": "string",
      "description": "扫描快照的显示名称"
    },
    "description": {
      "type": "string",
      "description": "扫描快照的详细描述"
    },
    "mimeType": {
      "type": "string",
      "const": "application/vnd.hexstrike.scan-snapshot+json"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "scan_id": {
          "type": "string",
          "pattern": "^[a-f0-9-]{36}$"
        },
        "target": {
          "type": "object",
          "properties": {
            "ip_range": {
              "type": "string",
              "pattern": "^(\\d{1,3}\\.){3}\\d{1,3}/\\d{1,2}$"
            },
            "domains": {
              "type": "array",
              "items": {
                "type": "string",
                "format": "hostname"
              }
            },
            "scan_type": {
              "type": "string",
              "enum": ["port_scan", "web_discovery", "subdomain_enum", "vuln_scan"]
            }
          },
          "required": ["ip_range", "scan_type"]
        },
        "timestamp": {
          "type": "string",
          "format": "date-time"
        },
        "duration": {
          "type": "number",
          "minimum": 0
        },
        "node_id": {
          "type": "string",
          "description": "执行扫描的节点标识"
        }
      },
      "required": ["scan_id", "target", "timestamp", "node_id"]
    }
  },
  "required": ["uri", "name", "description", "mimeType", "metadata"]
}
```

### 资产发现资源 (AssetDiscovery)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Asset Discovery Resource",
  "description": "资产发现结果，包含主机、服务、漏洞信息",
  "type": "object",
  "properties": {
    "uri": {
      "type": "string",
      "pattern": "^asset://[a-f0-9-]{36}$"
    },
    "name": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "mimeType": {
      "type": "string",
      "const": "application/vnd.hexstrike.asset-discovery+json"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "discovery_id": {
          "type": "string",
          "pattern": "^[a-f0-9-]{36}$"
        },
        "assets": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "ip": {
                "type": "string",
                "format": "ipv4"
              },
              "hostname": {
                "type": "string",
                "format": "hostname"
              },
              "os": {
                "type": "object",
                "properties": {
                  "family": {
                    "type": "string",
                    "enum": ["Linux", "Windows", "Unix", "Cisco", "Unknown"]
                  },
                  "version": {
                    "type": "string"
                  },
                  "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                  }
                }
              },
              "services": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "port": {
                      "type": "integer",
                      "minimum": 1,
                      "maximum": 65535
                    },
                    "protocol": {
                      "type": "string",
                      "enum": ["tcp", "udp"]
                    },
                    "service": {
                      "type": "string"
                    },
                    "version": {
                      "type": "string"
                    },
                    "state": {
                      "type": "string",
                      "enum": ["open", "closed", "filtered"]
                    },
                    "banner": {
                      "type": "string"
                    }
                  },
                  "required": ["port", "protocol", "service", "state"]
                }
              },
              "vulnerabilities": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "cve": {
                      "type": "string",
                      "pattern": "^CVE-\\d{4}-\\d{4,}$"
                    },
                    "severity": {
                      "type": "string",
                      "enum": ["critical", "high", "medium", "low", "info"]
                    },
                    "description": {
                      "type": "string"
                    },
                    "confidence": {
                      "type": "number",
                      "minimum": 0,
                      "maximum": 1
                    }
                  },
                  "required": ["severity", "description"]
                }
              }
            },
            "required": ["ip", "services"]
          }
        },
        "statistics": {
          "type": "object",
          "properties": {
            "total_hosts": {
              "type": "integer",
              "minimum": 0
            },
            "total_services": {
              "type": "integer",
              "minimum": 0
            },
            "total_vulnerabilities": {
              "type": "integer",
              "minimum": 0
            },
            "critical_count": {
              "type": "integer",
              "minimum": 0
            },
            "high_count": {
              "type": "integer",
              "minimum": 0
            }
          }
        }
      },
      "required": ["discovery_id", "assets", "statistics"]
    }
  },
  "required": ["uri", "name", "description", "mimeType", "metadata"]
}
```

---

## Tool 扩展规范

### 端口扫描工具 (PortScanTool)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Port Scan Tool",
  "description": "Nmap 端口扫描工具的标准化参数定义",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "const": "port_scan"
    },
    "description": {
      "type": "string",
      "const": "Perform port scanning using Nmap"
    },
    "inputSchema": {
      "type": "object",
      "properties": {
        "target": {
          "type": "string",
          "description": "目标 IP 地址或网段",
          "examples": ["192.168.1.1", "192.168.1.0/24"]
        },
        "ports": {
          "type": "string",
          "description": "端口范围",
          "default": "1-1000",
          "examples": ["22,80,443", "1-65535", "top-1000"]
        },
        "scan_type": {
          "type": "string",
          "enum": ["syn", "connect", "udp", "ack"],
          "default": "syn",
          "description": "扫描类型"
        },
        "timing": {
          "type": "integer",
          "minimum": 0,
          "maximum": 5,
          "default": 3,
          "description": "扫描时序模板 (0-5)"
        },
        "scripts": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "要执行的 NSE 脚本"
        },
        "max_retries": {
          "type": "integer",
          "minimum": 1,
          "maximum": 10,
          "default": 3,
          "description": "最大重试次数"
        },
        "timeout": {
          "type": "integer",
          "minimum": 1,
          "maximum": 3600,
          "default": 300,
          "description": "超时时间（秒）"
        }
      },
      "required": ["target"]
    }
  },
  "required": ["name", "description", "inputSchema"]
}
```

### Web 发现工具 (WebDiscoveryTool)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Web Discovery Tool",
  "description": "Web 应用发现工具的标准化参数定义",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "const": "web_discovery"
    },
    "description": {
      "type": "string",
      "const": "Discover web applications and directories"
    },
    "inputSchema": {
      "type": "object",
      "properties": {
        "target": {
          "type": "string",
          "format": "uri",
          "description": "目标 URL",
          "examples": ["http://192.168.1.100", "https://example.com"]
        },
        "wordlist": {
          "type": "string",
          "description": "字典文件路径",
          "default": "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
        },
        "extensions": {
          "type": "array",
          "items": {
            "type": "string",
            "pattern": "^\\.[a-zA-Z0-9]+$"
          },
          "description": "文件扩展名",
          "default": [".php", ".html", ".js", ".txt"]
        },
        "threads": {
          "type": "integer",
          "minimum": 1,
          "maximum": 100,
          "default": 10,
          "description": "并发线程数"
        },
        "status_codes": {
          "type": "array",
          "items": {
            "type": "integer",
            "minimum": 100,
            "maximum": 599
          },
          "description": "要记录的 HTTP 状态码",
          "default": [200, 301, 302, 403]
        },
        "follow_redirects": {
          "type": "boolean",
          "default": true,
          "description": "是否跟随重定向"
        },
        "timeout": {
          "type": "integer",
          "minimum": 1,
          "maximum": 300,
          "default": 10,
          "description": "请求超时时间（秒）"
        }
      },
      "required": ["target"]
    }
  },
  "required": ["name", "description", "inputSchema"]
}
```

### 漏洞验证工具 (VulnerabilityVerifyTool)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Vulnerability Verification Tool",
  "description": "漏洞验证工具的标准化参数定义",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "const": "vulnerability_verify"
    },
    "description": {
      "type": "string",
      "const": "Verify and validate vulnerabilities"
    },
    "inputSchema": {
      "type": "object",
      "properties": {
        "target": {
          "type": "string",
          "description": "目标地址",
          "examples": ["192.168.1.100:80", "https://example.com"]
        },
        "vulnerability_type": {
          "type": "string",
          "enum": ["sqli", "xss", "weak_password", "directory_traversal", "file_upload"],
          "description": "漏洞类型"
        },
        "payloads": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "测试载荷列表"
        },
        "templates": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "Nuclei 模板列表"
        },
        "severity_threshold": {
          "type": "string",
          "enum": ["info", "low", "medium", "high", "critical"],
          "default": "medium",
          "description": "严重性阈值"
        },
        "parallelism": {
          "type": "integer",
          "minimum": 1,
          "maximum": 50,
          "default": 10,
          "description": "并行执行数量"
        },
        "timeout": {
          "type": "integer",
          "minimum": 1,
          "maximum": 1800,
          "default": 300,
          "description": "验证超时时间（秒）"
        }
      },
      "required": ["target", "vulnerability_type"]
    }
  },
  "required": ["name", "description", "inputSchema"]
}
```

---

## Prompt 扩展规范

### 攻击建议提示词 (AttackSuggestionPrompt)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Attack Suggestion Prompt",
  "description": "AI 攻击建议的标准化提示词格式",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "const": "attack_suggestion"
    },
    "description": {
      "type": "string",
      "const": "Generate AI-powered attack suggestions based on scan results"
    },
    "arguments": {
      "type": "object",
      "properties": {
        "scan_results": {
          "type": "object",
          "description": "扫描结果数据",
          "properties": {
            "assets": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "ip": {
                    "type": "string",
                    "format": "ipv4"
                  },
                  "services": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "port": {
                          "type": "integer"
                        },
                        "service": {
                          "type": "string"
                        },
                        "version": {
                          "type": "string"
                        }
                      }
                    }
                  },
                  "vulnerabilities": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "cve": {
                          "type": "string"
                        },
                        "severity": {
                          "type": "string"
                        }
                      }
                    }
                  }
                }
              }
            },
            "scan_context": {
              "type": "object",
              "properties": {
                "objective": {
                  "type": "string",
                  "enum": ["reconnaissance", "vulnerability_assessment", "penetration_test"]
                },
                "scope": {
                  "type": "string",
                  "description": "测试范围描述"
                },
                "constraints": {
                  "type": "array",
                  "items": {
                    "type": "string"
                  },
                  "description": "测试约束条件"
                }
              }
            }
          }
        },
        "suggestion_type": {
          "type": "string",
          "enum": ["next_steps", "attack_chain", "priority_targets", "tool_recommendation"],
          "description": "建议类型"
        },
        "risk_tolerance": {
          "type": "string",
          "enum": ["conservative", "moderate", "aggressive"],
          "default": "moderate",
          "description": "风险容忍度"
        },
        "max_suggestions": {
          "type": "integer",
          "minimum": 1,
          "maximum": 20,
          "default": 5,
          "description": "最大建议数量"
        }
      },
      "required": ["scan_results", "suggestion_type"]
    }
  },
  "required": ["name", "description", "arguments"]
}
```

### 任务规划提示词 (TaskPlanningPrompt)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Task Planning Prompt",
  "description": "AI 任务规划的标准化提示词格式",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "const": "task_planning"
    },
    "description": {
      "type": "string",
      "const": "Generate optimized task execution plan"
    },
    "arguments": {
      "type": "object",
      "properties": {
        "mission": {
          "type": "object",
          "properties": {
            "target": {
              "type": "string",
              "description": "任务目标"
            },
            "objectives": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "具体目标列表"
            },
            "timeline": {
              "type": "object",
              "properties": {
                "start_time": {
                  "type": "string",
                  "format": "date-time"
                },
                "duration": {
                  "type": "integer",
                  "minimum": 1,
                  "description": "持续时间（分钟）"
                }
              }
            }
          },
          "required": ["target", "objectives"]
        },
        "available_resources": {
          "type": "object",
          "properties": {
            "nodes": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "node_id": {
                    "type": "string"
                  },
                  "capabilities": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  },
                  "load": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                  }
                }
              }
            },
            "tools": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "可用工具列表"
            }
          }
        },
        "optimization_criteria": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["speed", "accuracy", "stealth", "coverage"]
          },
          "description": "优化标准"
        }
      },
      "required": ["mission", "available_resources"]
    }
  },
  "required": ["name", "description", "arguments"]
}
```

---

## 消息类型扩展

### 任务执行消息 (TaskExecutionMessage)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Task Execution Message",
  "description": "任务执行状态的消息格式",
  "type": "object",
  "properties": {
    "message_id": {
      "type": "string",
      "pattern": "^[a-f0-9-]{36}$"
    },
    "message_type": {
      "type": "string",
      "const": "task_execution"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "sender": {
      "type": "object",
      "properties": {
        "node_id": {
          "type": "string"
        },
        "server_type": {
          "type": "string",
          "enum": ["recon", "exploit", "ai"]
        }
      },
      "required": ["node_id", "server_type"]
    },
    "payload": {
      "type": "object",
      "properties": {
        "task_id": {
          "type": "string",
          "pattern": "^[a-f0-9-]{36}$"
        },
        "status": {
          "type": "string",
          "enum": ["pending", "running", "completed", "failed", "cancelled"]
        },
        "progress": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "result": {
          "type": "object",
          "description": "任务结果数据"
        },
        "error": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string"
            },
            "message": {
              "type": "string"
            },
            "details": {
              "type": "object"
            }
          }
        },
        "metadata": {
          "type": "object",
          "description": "额外的元数据"
        }
      },
      "required": ["task_id", "status"]
    }
  },
  "required": ["message_id", "message_type", "timestamp", "sender", "payload"]
}
```

---

## 版本控制和兼容性

### 版本格式
```
MCP-PT-EXT-MAJOR.MINOR.PATCH
```

### 向后兼容性规则
1. **MAJOR 版本**: 不兼容的 API 修改
2. **MINOR 版本**: 向后兼容的功能性新增
3. **PATCH 版本**: 向后兼容的问题修正

### 协议协商机制
```json
{
  "handshake": {
    "protocol_version": "MCP-PT-EXT-1.0.0",
    "supported_versions": ["1.0.0", "0.9.0"],
    "capabilities": {
      "resource_types": ["scan_snapshot", "asset_discovery"],
      "tool_types": ["port_scan", "web_discovery", "vulnerability_verify"],
      "prompt_types": ["attack_suggestion", "task_planning"]
    }
  }
}
```

---

## 实现指南

### 1. 服务器端实现
- 严格验证所有输入数据
- 提供详细的错误信息
- 支持协议版本协商

### 2. 客户端实现
- 缓存协议模式定义
- 实现自动重试机制
- 支持优雅降级

### 3. 测试验证
- 单元测试覆盖所有模式
- 集成测试验证端到端通信
- 性能测试确保协议效率

---

## 总结

本扩展规范为渗透测试场景下的 MCP 协议提供了标准化的数据格式和通信规范，确保了异构节点之间的语义一致性，为分布式渗透测试协同系统奠定了坚实的协议基础。
