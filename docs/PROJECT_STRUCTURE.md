# HexStrike AI 分布式渗透测试协同系统 - 项目结构设计

## 项目概述

HexStrike AI 是一个基于 MCP (Model Context Protocol) 协议的分布式渗透测试协同系统，旨在实现多节点协作的自动化安全测试。系统通过能力注册、任务 DAG 和分布式调度，实现智能化的攻击面发现和漏洞验证。

---

## 核心设计理念

### 1. MCP 协议驱动
- 所有功能模块通过 MCP 协议进行通信
- 标准化的能力注册和发现机制
- 统一的任务分发和结果聚合

### 2. 分布式协同架构
- 多节点并行执行能力
- 智能任务分解与调度
- 实时状态同步与故障转移

### 3. AI 增强决策
- 基于上下文的智能任务规划
- 攻击链自动生成与优化
- 风险评估与优先级排序

---

## 项目目录结构

```
hexstrike-ai/
├── README.md                           # 项目总体说明
├── requirements.txt                    # Python 依赖管理
├── setup.py                           # 包安装配置
├── pyproject.toml                     # 现代Python项目配置
├── .env.example                       # 环境变量模板
├── .gitignore                         # Git 忽略文件
│
├── docs/                              # 系统文档目录
│   ├── README.md                      # 文档索引
│   ├── PROJECT_STRUCTURE.md           # 项目结构说明 (本文档)
│   ├── MODULAR_ARCHITECTURE.md        # 模块化架构设计
│   ├── MCP_PROTOCOL_SPEC.md           # MCP 协议规范
│   ├── ATTACK_CHAIN_MODEL.md          # 攻击链模型设计
│   ├── API_REFERENCE.md               # API 参考文档
│   ├── DEPLOYMENT_GUIDE.md            # 部署指南
│   ├── SECURITY_CONSIDERATIONS.md     # 安全考虑
│   └── RESEARCH_PAPER.md              # 研究论文相关
│
├── core/                              # 核心系统模块
│   ├── __init__.py                    # 包初始化
│   ├── mcp/                           # MCP 协议实现
│   │   ├── __init__.py
│   │   ├── protocol.py                # MCP 协议核心实现
│   │   ├── message_types.py           # 消息类型定义
│   │   ├── transport.py               # 传输层抽象
│   │   ├── serialization.py           # 序列化/反序列化
│   │   └── registry.py                # 能力注册中心
│   │
│   ├── scheduler/                     # 任务调度系统
│   │   ├── __init__.py
│   │   ├── dag_builder.py             # 任务 DAG 构建器
│   │   ├── task_decomposer.py         # 任务分解器
│   │   ├── distributed_executor.py    # 分布式执行器
│   │   ├── load_balancer.py           # 负载均衡器
│   │   ├── priority_queue.py          # 优先级队列
│   │   └── conflict_resolver.py       # 冲突解决器
│   │
│   ├── knowledge/                     # 知识模型
│   │   ├── __init__.py
│   │   ├── asset_model.py             # 资产模型
│   │   ├── service_model.py           # 服务模型
│   │   ├── vulnerability_model.py     # 漏洞模型
│   │   ├── discovery_model.py         # 发现结果模型
│   │   ├── risk_assessment.py         # 风险评估模型
│   │   └── knowledge_graph.py         # 知识图谱
│   │
│   ├── communication/                 # 通信层
│   │   ├── __init__.py
│   │   ├── node_manager.py            # 节点管理器
│   │   ├── message_router.py          # 消息路由器
│   │   ├── heartbeat.py               # 心跳检测
│   │   ├── discovery.py               # 节点发现
│   │   └── sync.py                    # 状态同步
│   │
│   └── security/                      # 安全模块
│       ├── __init__.py
│       ├── authentication.py          # 身份认证
│       ├── authorization.py           # 权限控制
│       ├── encryption.py              # 加密模块
│       └── audit.py                   # 审计日志
│
├── servers/                           # MCP 服务器实现
│   ├── __init__.py
│   ├── base/                          # 基础服务器类
│   │   ├── __init__.py
│   │   ├── mcp_server_base.py         # MCP 服务器基类
│   │   ├── capability_provider.py     # 能力提供者基类
│   │   └── result_handler.py          # 结果处理器基类
│   │
│   ├── recon/                         # 信息收集服务器
│   │   ├── __init__.py
│   │   ├── recon_server.py            # 侦察服务器主类
│   │   ├── capabilities/
│   │   │   ├── __init__.py
│   │   │   ├── port_enumeration.py    # 端口枚举 (nmap)
│   │   │   ├── web_discovery.py       # Web 发现 (目录扫描、模糊测试)
│   │   │   ├── subdomain_enum.py      # 子域名枚举
│   │   │   ├── smb_enum.py            # SMB 枚举
│   │   │   └── dns_recon.py           # DNS 侦察
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── nmap_wrapper.py        # Nmap 工具封装
│   │   │   ├── gobuster_wrapper.py    # Gobuster 工具封装
│   │   │   ├── amass_wrapper.py       # Amass 工具封装
│   │   │   └── smbmap_wrapper.py      # SMBmap 工具封装
│   │   └── config/
│   │       ├── __init__.py
│   │       └── recon_config.py        # 侦察模块配置
│   │
│   ├── exploit/                       # 漏洞验证服务器
│   │   ├── __init__.py
│   │   ├── exploit_server.py          # 漏洞验证服务器
│   │   ├── capabilities/
│   │   │   ├── __init__.py
│   │   │   ├── weak_password_test.py  # 弱密码验证
│   │   │   ├── sqli_verify.py         # SQL 注入验证
│   │   │   ├── nuclei_scan.py         # Nuclei 模板扫描
│   │   │   ├── metasploit_interface.py # Metasploit 接口
│   │   │   └── payload_generator.py   # 载荷生成接口
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── nuclei_wrapper.py      # Nuclei 工具封装
│   │   │   ├── sqlmap_wrapper.py      # SQLMap 工具封装
│   │   │   ├── hydra_wrapper.py       # Hydra 工具封装
│   │   │   └── msf_interface.py       # Metasploit 接口
│   │   └── config/
│   │       ├── __init__.py
│   │       └── exploit_config.py      # 漏洞验证配置
│   │
│   └── ai/                            # AI 决策服务器
│       ├── __init__.py
│       ├── ai_server.py               # AI 决策服务器
│       ├── capabilities/
│       │   ├── __init__.py
│       │   ├── context_analyzer.py    # 上下文分析器
│       │   ├── task_planner.py        # 任务规划器
│       │   ├── risk_assessor.py       # 风险评估器
│       │   ├── attack_chain_builder.py # 攻击链构建器
│       │   └── priority_optimizer.py  # 优先级优化器
│       ├── models/
│       │   ├── __init__.py
│       │   ├── decision_engine.py     # 决策引擎
│       │   ├── context_model.py       # 上下文模型
│       │   ├── attack_graph.py        # 攻击图模型
│       │   └── ml_predictor.py        # 机器学习预测器
│       └── config/
│           ├── __init__.py
│           └── ai_config.py           # AI 模块配置
│
├── client/                            # 统一控制客户端
│   ├── __init__.py
│   ├── cli/                           # 命令行接口
│   │   ├── __init__.py
│   │   ├── main.py                    # CLI 主入口
│   │   ├── commands/                  # 命令实现
│   │   │   ├── __init__.py
│   │   │   ├── scan.py                # 扫描命令
│   │   │   ├── analyze.py             # 分析命令
│   │   │   ├── plan.py                # 规划命令
│   │   │   └── status.py              # 状态命令
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── output_formatter.py    # 输出格式化
│   │       └── config_loader.py       # 配置加载器
│   │
│   ├── web/                           # Web 界面
│   │   ├── __init__.py
│   │   ├── app.py                     # Web 应用主入口
│   │   ├── api/                       # REST API
│   │   │   ├── __init__.py
│   │   │   ├── scan_api.py            # 扫描 API
│   │   │   ├── task_api.py            # 任务 API
│   │   │   └── result_api.py          # 结果 API
│   │   ├── static/                    # 静态资源
│   │   │   ├── css/
│   │   │   ├── js/
│   │   │   └── images/
│   │   └── templates/                 # 页面模板
│   │       ├── index.html
│   │       ├── scan.html
│   │       └── results.html
│   │
│   └── sdk/                           # Python SDK
│       ├── __init__.py
│       ├── client.py                  # 客户端 SDK
│       ├── models.py                  # 数据模型
│       └── exceptions.py              # 异常定义
│
├── scenarios/                         # 实验场景描述
│   ├── __init__.py
│   ├── README.md                      # 场景使用说明
│   ├── basic_network/                 # 基础网络场景
│   │   ├── scenario.yaml              # 场景定义
│   │   ├── topology.png               # 网络拓扑图
│   │   └── expected_results.yaml      # 预期结果
│   ├── web_application/               # Web 应用场景
│   │   ├── scenario.yaml
│   │   ├── docker-compose.yml         # 容器编排
│   │   └── expected_results.yaml
│   ├── enterprise_network/            # 企业网络场景
│   │   ├── scenario.yaml
│   │   ├── vagrant/                   # 虚拟机配置
│   │   └── expected_results.yaml
│   └── custom/                        # 自定义场景
│       ├── template.yaml              # 场景模板
│       └── README.md                  # 自定义指南
│
├── experiments/                       # 对比实验设计
│   ├── __init__.py
│   ├── README.md                      # 实验设计说明
│   ├── serial_vs_collaborative/       # 串行 vs 协同对比
│   │   ├── experiment_design.md       # 实验设计文档
│   │   ├── test_cases/                # 测试用例
│   │   │   ├── small_network.yaml     # 小型网络测试
│   │   │   ├── medium_network.yaml    # 中型网络测试
│   │   │   └── large_network.yaml     # 大型网络测试
│   │   ├── metrics/                   # 评估指标
│   │   │   ├── performance_metrics.py # 性能指标
│   │   │   ├── coverage_metrics.py    # 覆盖率指标
│   │   │   └── efficiency_metrics.py  # 效率指标
│   │   └── results/                   # 实验结果
│   │       ├── raw_data/              # 原始数据
│   │       ├── analysis/              # 分析结果
│   │       └── charts/                # 图表
│   │
│   ├── scalability_test/              # 可扩展性测试
│   │   ├── experiment_design.md
│   │   ├── load_test.py               # 负载测试
│   │   └── resource_monitoring.py     # 资源监控
│   │
│   └── accuracy_evaluation/           # 准确性评估
│       ├── experiment_design.md
│       ├── false_positive_test.py     # 误报测试
│       └── detection_rate_test.py     # 检出率测试
│
├── data/                              # 数据目录
│   ├── __init__.py
│   ├── schemas/                       # 数据模式定义
│   │   ├── __init__.py
│   │   ├── asset_schema.json          # 资产数据模式
│   │   ├── scan_result_schema.json    # 扫描结果模式
│   │   ├── task_schema.json           # 任务数据模式
│   │   └── report_schema.json         # 报告数据模式
│   ├── templates/                     # 模板文件
│   │   ├── scan_templates/            # 扫描模板
│   │   ├── report_templates/          # 报告模板
│   │   └── config_templates/          # 配置模板
│   └── samples/                       # 示例数据
│       ├── sample_assets.json         # 示例资产数据
│       ├── sample_scan_results.json   # 示例扫描结果
│       └── sample_tasks.json          # 示例任务数据
│
├── tests/                             # 测试目录
│   ├── __init__.py
│   ├── unit/                          # 单元测试
│   │   ├── __init__.py
│   │   ├── test_core/                 # 核心模块测试
│   │   │   ├── test_mcp_protocol.py
│   │   │   ├── test_scheduler.py
│   │   │   └── test_knowledge_model.py
│   │   ├── test_servers/              # 服务器模块测试
│   │   │   ├── test_recon_server.py
│   │   │   ├── test_exploit_server.py
│   │   │   └── test_ai_server.py
│   │   └── test_client/               # 客户端测试
│   │       ├── test_cli.py
│   │       └── test_sdk.py
│   │
│   ├── integration/                   # 集成测试
│   │   ├── __init__.py
│   │   ├── test_mcp_communication.py  # MCP 通信测试
│   │   ├── test_distributed_execution.py # 分布式执行测试
│   │   └── test_end_to_end.py         # 端到端测试
│   │
│   ├── performance/                   # 性能测试
│   │   ├── __init__.py
│   │   ├── test_scalability.py        # 可扩展性测试
│   │   ├── test_throughput.py         # 吞吐量测试
│   │   └── test_latency.py            # 延迟测试
│   │
│   └── fixtures/                      # 测试数据
│       ├── __init__.py
│       ├── mock_servers.py            # 模拟服务器
│       ├── test_data/                 # 测试数据
│       └── test_configs/              # 测试配置
│
├── deployment/                        # 部署相关
│   ├── __init__.py
│   ├── docker/                        # Docker 部署
│   │   ├── Dockerfile.base            # 基础镜像
│   │   ├── Dockerfile.recon           # 侦察服务镜像
│   │   ├── Dockerfile.exploit         # 漏洞验证镜像
│   │   ├── Dockerfile.ai              # AI 服务镜像
│   │   └── docker-compose.yml         # 容器编排
│   │
│   ├── kubernetes/                    # Kubernetes 部署
│   │   ├── namespace.yaml             # 命名空间
│   │   ├── configmap.yaml             # 配置映射
│   │   ├── deployment.yaml            # 部署配置
│   │   ├── service.yaml               # 服务配置
│   │   └── ingress.yaml               # 入口配置
│   │
│   ├── ansible/                       # Ansible 部署
│   │   ├── playbook.yml               # 主剧本
│   │   ├── inventory/                 # 主机清单
│   │   └── roles/                     # 角色定义
│   │
│   └── scripts/                       # 部署脚本
│       ├── setup.sh                   # 环境设置脚本
│       ├── deploy.sh                  # 部署脚本
│       └── cleanup.sh                 # 清理脚本
│
├── monitoring/                        # 监控和日志
│   ├── __init__.py
│   ├── logging/                       # 日志配置
│   │   ├── __init__.py
│   │   ├── logger_config.py           # 日志配置
│   │   ├── formatters.py              # 格式化器
│   │   └── handlers.py                # 处理器
│   │
│   ├── metrics/                       # 指标收集
│   │   ├── __init__.py
│   │   ├── collector.py               # 指标收集器
│   │   ├── exporter.py                # 指标导出器
│   │   └── dashboard.py               # 监控仪表板
│   │
│   └── alerting/                      # 告警系统
│       ├── __init__.py
│       ├── rules.py                   # 告警规则
│       ├── notifications.py           # 通知系统
│       └── escalation.py              # 升级策略
│
└── tools/                             # 开发和运维工具
    ├── __init__.py
    ├── development/                   # 开发工具
    │   ├── __init__.py
    │   ├── code_generator.py          # 代码生成器
    │   ├── schema_validator.py        # 模式验证器
    │   └── test_runner.py             # 测试运行器
    │
    ├── operations/                    # 运维工具
    │   ├── __init__.py
    │   ├── health_check.py            # 健康检查工具
    │   ├── backup.py                  # 备份工具
    │   └── recovery.py                # 恢复工具
    │
    └── analysis/                      # 分析工具
        ├── __init__.py
        ├── log_analyzer.py            # 日志分析器
        ├── performance_analyzer.py    # 性能分析器
        └── security_analyzer.py       # 安全分析器
```

---

## 模块职责说明

### 核心模块 (`core/`)

#### MCP 协议层 (`core/mcp/`)
- **protocol.py**: MCP 协议的核心实现，包括消息格式、通信规范
- **message_types.py**: 定义所有 MCP 消息类型和结构
- **transport.py**: 提供传输层抽象，支持多种通信方式
- **serialization.py**: 处理数据的序列化和反序列化
- **registry.py**: 实现能力注册中心，管理所有可用能力

#### 调度系统 (`core/scheduler/`)
- **dag_builder.py**: 将复杂任务分解为有向无环图 (DAG)
- **task_decomposer.py**: 智能任务分解，根据目标特点生成子任务
- **distributed_executor.py**: 分布式任务执行器，协调多节点执行
- **load_balancer.py**: 负载均衡算法，优化资源利用
- **priority_queue.py**: 基于优先级的任务队列管理
- **conflict_resolver.py**: 解决任务冲突和资源竞争

#### 知识模型 (`core/knowledge/`)
- **asset_model.py**: 资产数据模型，包括网络设备、服务等
- **service_model.py**: 服务模型，描述各种网络服务特征
- **vulnerability_model.py**: 漏洞模型，标准化漏洞描述
- **discovery_model.py**: 发现结果模型，统一扫描结果格式
- **risk_assessment.py**: 风险评估算法和模型
- **knowledge_graph.py**: 知识图谱，建立实体间关系

### 服务器模块 (`servers/`)

#### 侦察服务器 (`servers/recon/`)
- **recon_server.py**: 信息收集服务器主类，实现 MCP 服务器接口
- **capabilities/**: 各种侦察能力实现
  - 端口枚举、Web 发现、子域名枚举、SMB 枚举、DNS 侦察
- **tools/**: 第三方工具的标准化封装
- **config/**: 侦察模块的配置管理

#### 漏洞验证服务器 (`servers/exploit/`)
- **exploit_server.py**: 漏洞验证服务器主类
- **capabilities/**: 各种漏洞验证能力
  - 弱密码测试、SQL 注入验证、模板扫描、Metasploit 接口
- **tools/**: 安全工具的封装和接口
- **config/**: 漏洞验证模块配置

#### AI 决策服务器 (`servers/ai/`)
- **ai_server.py**: AI 决策服务器主类
- **capabilities/**: AI 驱动的决策能力
  - 上下文分析、任务规划、风险评估、攻击链构建
- **models/**: 机器学习模型和算法实现
- **config/**: AI 模块配置

### 客户端模块 (`client/`)

#### 命令行接口 (`client/cli/`)
- **main.py**: CLI 主入口，提供命令行交互界面
- **commands/**: 各种命令的具体实现
- **utils/**: 辅助工具和配置管理

#### Web 界面 (`client/web/`)
- **app.py**: Web 应用主入口，基于 Flask/FastAPI
- **api/**: REST API 实现，提供 HTTP 接口
- **static/**: 前端静态资源
- **templates/**: HTML 页面模板

#### Python SDK (`client/sdk/`)
- **client.py**: Python 客户端 SDK，便于集成开发
- **models.py**: 数据模型定义
- **exceptions.py**: 异常类型定义

### 实验场景 (`scenarios/`)
- 提供标准化的测试环境配置
- 支持不同复杂度的网络拓扑
- 包含预期结果用于验证

### 对比实验 (`experiments/`)
- **串行 vs 协同**: 验证分布式协同的优势
- **可扩展性测试**: 测试系统在不同规模下的表现
- **准确性评估**: 评估漏洞检测的准确性

---

## 技术栈选择

### 后端技术
- **Python 3.9+**: 主要开发语言
- **FastAPI**: Web API 框架
- **asyncio**: 异步编程支持
- **Pydantic**: 数据验证和序列化
- **SQLAlchemy**: ORM 和数据库抽象

### 分布式技术
- **Redis**: 消息队列和缓存
- **Celery**: 分布式任务队列
- **Docker**: 容器化部署
- **Kubernetes**: 容器编排

### AI/ML 技术
- **scikit-learn**: 机器学习算法
- **networkx**: 图算法和网络分析
- **pandas**: 数据处理和分析
- **numpy**: 数值计算

### 前端技术
- **React**: 前端框架
- **TypeScript**: 类型安全的 JavaScript
- **Ant Design**: UI 组件库
- **ECharts**: 数据可视化

### 监控和日志
- **Prometheus**: 指标收集
- **Grafana**: 监控仪表板
- **ELK Stack**: 日志收集和分析

---

## 部署架构

### 单机部署
适用于开发和小规模测试
- 所有组件运行在同一台机器
- 使用 Docker Compose 进行编排
- 本地 Redis 作为消息队列

### 分布式部署
适用于生产环境和大规模测试
- 各服务器组件独立部署
- 使用 Kubernetes 进行容器编排
- 外部 Redis 集群和数据库

### 云原生部署
适用于云端部署和弹性扩展
- 使用云服务 (AWS/Azure/GCP)
- 自动扩缩容和负载均衡
- 托管数据库和消息队列

---

## 安全考虑

### 通信安全
- 所有 MCP 通信使用 TLS 加密
- 节点间身份验证和授权
- 消息完整性校验

### 访问控制
- 基于角色的访问控制 (RBAC)
- API 密钥管理
- 操作审计日志

### 数据安全
- 敏感数据加密存储
- 扫描结果脱敏处理
- 定期安全扫描和更新

---

## 开发规范

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 使用类型注解提高代码可读性
- 完整的文档字符串和注释

### 测试规范
- 单元测试覆盖率 > 80%
- 集成测试覆盖主要业务流程
- 性能测试验证系统指标

### 版本控制
- 使用 Git 进行版本控制
- 遵循语义化版本规范
- 代码审查和持续集成

---

## 项目里程碑

### 第一阶段：基础框架 (4 周)
- MCP 协议层实现
- 基础调度系统
- 简单的侦察服务器

### 第二阶段：核心功能 (6 周)
- 完整的任务调度系统
- 知识模型实现
- AI 决策模块

### 第三阶段：系统集成 (4 周)
- 客户端开发
- Web 界面实现
- 端到端测试

### 第四阶段：实验验证 (3 周)
- 实验场景搭建
- 对比实验执行
- 性能优化

---

## 总结

本项目结构设计充分体现了分布式协同的思想，通过 MCP 协议实现了标准化的能力封装和通信。模块化的设计使得系统具有良好的可扩展性和可维护性，同时支持多种部署方式。完整的实验设计确保了研究的科学性和可验证性。

该架构为分布式渗透测试协同系统的研究提供了坚实的基础，不仅满足了学术研究的严谨性要求，也具备了实际应用的潜力。
