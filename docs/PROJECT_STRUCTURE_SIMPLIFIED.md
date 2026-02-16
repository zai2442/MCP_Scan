# MCP_kali 简化版项目结构

## 项目概述

MCP_kali 简化版是一个基于 MCP 协议的分布式渗透测试协同系统，专为本地测试环境设计，保留核心功能，支持在笔记本和虚拟机中运行。

---

## 精简目录结构

```
MCP_kali/
├── README.md                          # 项目说明
├── requirements.txt                   # Python 依赖
├── setup.py                          # 包配置
├── .env.example                      # 环境变量模板
├── config.yaml                       # 主配置文件
│
├── core/                             # 核心系统模块
│   ├── __init__.py
│   ├── mcp/                          # MCP 协议实现
│   │   ├── __init__.py
│   │   ├── protocol.py               # MCP 协议核心
│   │   ├── message_types.py          # 消息类型
│   │   └── registry.py               # 能力注册中心
│   │
│   ├── scheduler/                    # 任务调度系统
│   │   ├── __init__.py
│   │   ├── dag_builder.py            # 任务 DAG 构建
│   │   ├── task_decomposer.py        # 任务分解
│   │   └── distributed_executor.py   # 分布式执行器
│   │
│   ├── knowledge/                    # 知识模型
│   │   ├── __init__.py
│   │   ├── asset_model.py            # 资产模型
│   │   ├── vulnerability_model.py    # 漏洞模型
│   │   └── scan_result_model.py      # 扫描结果模型
│   │
│   └── communication/                # 通信层
│       ├── __init__.py
│       ├── node_manager.py           # 节点管理
│       └── message_router.py         # 消息路由
│
├── servers/                          # MCP 服务器
│   ├── __init__.py
│   ├── base/                         # 基础服务器类
│   │   ├── __init__.py
│   │   └── mcp_server_base.py        # MCP 服务器基类
│   │
│   ├── recon/                        # 信息收集服务器
│   │   ├── __init__.py
│   │   ├── recon_server.py           # 侦察服务器
│   │   ├── capabilities/
│   │   │   ├── __init__.py
│   │   │   ├── port_scan.py          # 端口扫描 (nmap)
│   │   │   ├── web_discovery.py      # Web 发现 (gobuster)
│   │   │   ├── subdomain_enum.py     # 子域名枚举
│   │   │   └── smb_enum.py           # SMB 枚举
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── nmap_wrapper.py       # Nmap 封装
│   │       └── gobuster_wrapper.py   # Gobuster 封装
│   │
│   ├── exploit/                      # 漏洞验证服务器
│   │   ├── __init__.py
│   │   ├── exploit_server.py         # 漏洞验证服务器
│   │   ├── capabilities/
│   │   │   ├── __init__.py
│   │   │   ├── weak_password_test.py # 弱密码验证
│   │   │   ├── sqli_verify.py        # SQL 注入验证
│   │   │   └── nuclei_scan.py        # Nuclei 模板扫描
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── nuclei_wrapper.py     # Nuclei 封装
│   │       └── sqlmap_wrapper.py     # SQLMap 封装
│   │
│   └── ai/                           # AI 决策服务器
│       ├── __init__.py
│       ├── ai_server.py              # AI 决策服务器
│       ├── capabilities/
│       │   ├── __init__.py
│       │   ├── context_analyzer.py   # 上下文分析
│       │   ├── task_planner.py       # 任务规划
│       │   └── attack_chain_builder.py # 攻击链构建
│       └── models/
│           ├── __init__.py
│           └── decision_engine.py    # 决策引擎
│
├── client/                           # 客户端
│   ├── __init__.py
│   ├── cli.py                        # 命令行接口
│   ├── sdk.py                        # Python SDK
│   └── config/
│       ├── __init__.py
│       └── client_config.py          # 客户端配置
│
├── data/                             # 数据目录
│   ├── __init__.py
│   ├── schemas/                      # 数据模式
│   │   ├── __init__.py
│   │   ├── asset_schema.json         # 资产数据模式
│   │   ├── scan_result_schema.json   # 扫描结果模式
│   │   └── task_schema.json          # 任务数据模式
│   └── samples/                      # 示例数据
│       ├── __init__.py
│       ├── sample_assets.json        # 示例资产
│       └── sample_scan_results.json  # 示例扫描结果
│
├── tests/                            # 测试目录
│   ├── __init__.py
│   ├── test_core/                    # 核心测试
│   │   ├── __init__.py
│   │   ├── test_mcp_protocol.py      # MCP 协议测试
│   │   ├── test_scheduler.py         # 调度器测试
│   │   └── test_knowledge_model.py   # 知识模型测试
│   ├── test_servers/                 # 服务器测试
│   │   ├── __init__.py
│   │   ├── test_recon_server.py      # 侦察服务器测试
│   │   ├── test_exploit_server.py    # 漏洞验证服务器测试
│   │   └── test_ai_server.py         # AI 服务器测试
│   └── test_client/                  # 客户端测试
│       ├── __init__.py
│       └── test_cli.py               # CLI 测试
│
├── deployment/                       # 简化部署
│   └── scripts/                      # 部署脚本
│       ├── start.sh                  # 启动脚本
│       ├── stop.sh                   # 停止脚本
│       └── setup.sh                  # 环境设置
│
└── docs/                             # 文档
    ├── README.md                     # 文档索引
    ├── PROJECT_STRUCTURE_SIMPLIFIED.md # 简化结构说明
    ├── API_REFERENCE.md              # API 参考
    └── DEPLOYMENT_GUIDE.md           # 部署指南
```

---

## 核心功能模块

### 1. MCP 协议层 (`core/mcp/`)
- **protocol.py**: 简化的 MCP 协议实现
- **message_types.py**: 基础消息类型定义
- **registry.py**: 能力注册和发现

### 2. 任务调度器 (`core/scheduler/`)
- **dag_builder.py**: 基础任务 DAG 构建
- **task_decomposer.py**: 简单任务分解逻辑
- **distributed_executor.py**: 本地分布式执行

### 3. 知识模型 (`core/knowledge/`)
- **asset_model.py**: 基础资产数据模型
- **vulnerability_model.py**: 简化漏洞模型
- **scan_result_model.py**: 统一扫描结果格式

### 4. 侦察服务器 (`servers/recon/`)
- **port_scan.py**: Nmap 端口扫描能力
- **web_discovery.py**: Gobuster Web 发现
- **subdomain_enum.py**: 基础子域名枚举
- **smb_enum.py**: SMB 共享枚举

### 5. 漏洞验证服务器 (`servers/exploit/`)
- **weak_password_test.py**: 弱密码验证接口
- **sqli_verify.py**: SQL 注入验证接口
- **nuclei_scan.py**: Nuclei 模板扫描接口

### 6. AI 决策服务器 (`servers/ai/`)
- **context_analyzer.py**: 基础上下文分析
- **task_planner.py**: 简单任务规划
- **attack_chain_builder.py**: 攻击链构建

---

## 简化部署方案

### 本地单机部署
```bash
# 启动所有服务
python -m servers.recon.recon_server &
python -m servers.exploit.exploit_server &
python -m servers.ai.ai_server &
python client/cli.py
```

### Docker 容器部署
```bash
# 构建镜像
docker build -t MCP_kali .

# 启动服务
docker-compose up -d
```

### 虚拟机分布式部署
```bash
# 在主节点启动调度器和 AI 服务
python -m core.scheduler.main &
python -m servers.ai.ai_server &

# 在工作节点启动侦察和漏洞验证服务
python -m servers.recon.recon_server &
python -m servers.exploit.exploit_server &
```

---

## 配置文件示例

### config.yaml
```yaml
# MCP 协议配置
mcp:
  host: "127.0.0.1"
  port: 8080
  timeout: 30

# 服务器配置
servers:
  recon:
    enabled: true
    port: 8081
  exploit:
    enabled: true
    port: 8082
  ai:
    enabled: true
    port: 8083

# 工具路径配置
tools:
  nmap: "/usr/bin/nmap"
  gobuster: "/usr/bin/gobuster"
  nuclei: "/usr/bin/nuclei"
  sqlmap: "/usr/bin/sqlmap"

# 日志配置
logging:
  level: "INFO"
  file: "MCP_kali.log"
```

---

## 快速启动指南

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 安装安全工具
sudo apt-get install nmap gobuster nuclei sqlmap
```

### 2. 配置设置
```bash
# 复制配置文件
cp .env.example .env
cp config.yaml.example config.yaml

# 编辑配置
vim config.yaml
```

### 3. 启动系统
```bash
# 使用启动脚本
./deployment/scripts/start.sh

# 或手动启动
python -m servers.recon.recon_server &
python -m servers.exploit.exploit_server &
python -m servers.ai.ai_server &
python client/cli.py
```

### 4. 基本使用
```bash
# 扫描目标
python client/cli.py scan --target 192.168.1.0/24

# 查看结果
python client/cli.py results --scan-id <scan_id>

# 生成报告
python client/cli.py report --scan-id <scan_id> --format json
```

---

## 技术栈（简化版）

### 后端
- **Python 3.8+**: 主要开发语言
- **FastAPI**: Web API 框架
- **asyncio**: 异步编程
- **Pydantic**: 数据验证

### 分布式
- **Redis**: 本地消息队列
- **asyncio**: 异步任务调度

### 前端
- **Rich**: 终端美化
- **Click**: 命令行界面

---

## 移除的组件

相比完整版本，简化版移除了：
- ❌ 实验场景 (scenarios/)
- ❌ 对比实验 (experiments/)
- ❌ 复杂监控 (monitoring/)
- ❌ Kubernetes 部署
- ❌ Web 界面
- ❌ 复杂运维工具
- ❌ 高级分析功能

---

## 保留的核心价值

✅ **MCP 协议驱动**: 标准化的能力封装和通信
✅ **分布式协同**: 多节点并行执行能力
✅ **AI 决策**: 基于上下文的智能任务规划
✅ **模块化设计**: 清晰的功能分离
✅ **易于部署**: 支持本地和虚拟机环境
✅ **可扩展性**: 为未来功能扩展预留接口

---

## 总结

这个简化版本专注于核心功能实现，去除了复杂的实验和运维组件，适合在本地环境中快速部署和测试。保留了 MCP 协议、分布式调度、AI 决策等核心特性，为研究提供了坚实的基础。
