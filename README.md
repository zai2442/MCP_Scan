# MCP Scan (分布式渗透测试平台)

**版本**: 1.0.0 (MVP P0)
**状态**: Beta

MCP Scan 是一个轻量级、模块化、由 AI 编排的分布式渗透测试平台。它旨在通过 MCP 协议标准化安全工具的交互，实现自动化、智能化的安全扫描流程。

---

## 🚀 快速开始

### 运行环境
由于该系统通过 Python 调用底层安全工具，请确保您的系统中已安装以下工具：
- `nmap`
- `nuclei`
- `gobuster`
- `sqlmap`
- `hydra`

### 启动扫描
MCP Scan 作为一个 Python 模块运行。在项目根目录下执行：

1. **设置环境变量**（确保能找到源码目录）：
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)/src
   ```

2. **执行扫描命令**：
   ```bash
   python3 -m mcp_scan.cli start --target <目标IP或域名> [--profile fast/deep]
   ```

---

## 🛠 常用命令汇总

| 功能 | 命令示例 | 说明 |
| :--- | :--- | :--- |
| **启动扫描** | `python3 -m mcp_scan.cli start --target 127.0.0.1` | 开始针对目标的自动化扫描流 |
| **查看状态** | `python3 -m mcp_scan.cli status <JOB_ID>` | 实时查看子任务（nmap, nuclei 等）的进度 |
| **导出报告** | `python3 -m mcp_scan.cli report <JOB_ID> -o report.json` | 将扫描结果导出为详细的 JSON 文件 |
| **启动 MCP 服务端** | `python3 -m mcp_scan.cli server` | 启动标准 MCP 协议服务端，供大模型（如 Claude Desktop）直接调用工具 |
| **查看帮助** | `python3 -m mcp_scan.cli --help` | 查看所有可用的命令参数 |

---

## 📦 安装与配置

1. **安装依赖库**：
   ```bash
   pip install -r requirements.txt
   ```

2. **数据库配置**：
   系统默认连接本地 Docker 运行的 MySQL。如果需要修改，请编辑 `src/mcp_scan/config.py` 或在根目录创建 `config.yaml`：
   ```yaml
   database:
     host: "127.0.0.1"
     user: "root"
     password: "root"
     database: "job_result_db"
   ```

3. **Docker 启动数据库**：
   ```bash
   sudo docker run --name job_result_db -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=job_result_db -p 3306:3306 -d mysql:8.0 --skip-name-resolve
   ```
   # 1. 停止并删除所有相关容器
   sudo docker stop job_result_db job_result_api mysql8 2>/dev/null
   sudo docker rm job_result_db job_result_api mysql8 2>/dev/null

   # 2. 进入 compose 目录
   cd docs/mvp-p0/job-result-system/

   # 3. 清理旧的匿名卷（注意：这会删除数据库内的测试数据）
   sudo docker-compose down -v

   # 4. 重新启动
   sudo docker-compose up -d


---

## 🧠 智能化工作流 (DAG) 与 MCP 集成

MCP Scan 不仅内置了“智能调度器”来编排工具执行流，还完整集成了 **MCP (Model Context Protocol)** 协议，使大语言模型能够直接参与渗透测试流程：

1. **MCP 标准化接口**：系统对外暴露了 `scan_nmap`、`scan_gobuster`、`scan_nuclei`、`scan_sqlmap` 和 `scan_hydra` 等标准 MCP 资源工具，AI 客户端可以通过 JSON-RPC 无缝调用它们。
2. **AI DAG 任务编排**：通过新增的 `submit_ai_dag_plan` 工具，AI 可以将复杂的渗透目标（例如“寻找Web漏洞并尝试注入”）自主分解为一个个任务节点，并生成具有依赖关系的 DAG（有向无环图）提交给系统执行。
3. **数据聚合**：所有工具的原始输出都将被结构化，并存入统一的任务模型中，随时供 AI 再次检索和分析。

---

## 🧑‍💻 开发与测试

- **运行单元测试**：`python3 run_tests.py`
- **运行性能基准测试**：`python3 run_benchmark.py`
- **查看运行日志**：`tail -f mcp_scan.log`

---

## 📂 项目结构
- `src/mcp_scan/core`: 核心逻辑（调度器、数据库管理、数据模型）。
- `src/mcp_scan/tools`: 工具包装器（集成 nmap, nuclei 等接口）。
- `src/mcp_scan/cli.py`: 命令行交互入口。
- `src/mcp_scan/transport`: 消息传输层实现。
