# HexStrike AI 开发者实现指南

## 概述

本指南提供 HexStrike AI 分布式渗透测试协同系统的详细开发实现流程，确保代码实现与论文研究目标保持一致。采用三阶段递进式开发方法，从协议基础到智能调度，逐步构建完整的分布式协同系统。

---

## 开发环境准备

### 必需依赖
```bash
# Python 环境
python >= 3.8
pip install fastapi uvicorn pydantic
pip install asyncio aiohttp aiofiles
pip install redis celery
pip install psutil
pip install python-nmap
pip install xmltodict

# 系统工具
sudo apt-get install nmap gobuster nuclei
```

### 项目结构
```
hexstrike-ai/
├── core/
│   ├── mcp/                    # Phase 1: 协议层
│   ├── scheduler/              # Phase 3: 调度层
│   └── knowledge/              # 数据模型
├── servers/
│   ├── base/                   # 基础服务器类
│   ├── recon/                  # 侦察服务器
│   ├── exploit/                # 漏洞验证服务器
│   └── ai/                     # AI 决策服务器
└── client/                     # 客户端接口
```

---

## Phase 1: 协议和注册中心 (基础层)

### Task 1: 实现 core/mcp/protocol.py

#### 目标
实现 JSON-RPC 2.0 基础通信，支持 MCP 协议规范

#### 实现步骤

**1.1 创建基础消息结构**
```python
# core/mcp/message_types.py
from typing import Dict, Any, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

class JSONRPCMessage(BaseModel):
    """JSON-RPC 2.0 基础消息格式"""
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

class MCPMessage(JSONRPCMessage):
    """MCP 协议扩展消息"""
    mcp_version: str = "1.0.0"
    timestamp: datetime
    node_id: str
    message_type: str  # 'request', 'response', 'notification'
```

**1.2 实现协议处理器**
```python
# core/mcp/protocol.py
import asyncio
import json
from typing import Callable, Dict, Any, Optional
from .message_types import MCPMessage

class MCPProtocol:
    """MCP 协议处理器"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.handlers: Dict[str, Callable] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
    
    def register_handler(self, method: str, handler: Callable):
        """注册消息处理器"""
        self.handlers[method] = handler
    
    async def handle_message(self, raw_message: str) -> Optional[str]:
        """处理接收到的消息"""
        try:
            data = json.loads(raw_message)
            message = MCPMessage(**data)
            
            if message.method and message.method in self.handlers:
                # 处理请求消息
                response = await self._handle_request(message)
                return json.dumps(response.dict(), default=str)
            
            elif message.id and message.id in self.pending_requests:
                # 处理响应消息
                future = self.pending_requests.pop(message.id)
                if message.error:
                    future.set_exception(Exception(message.error))
                else:
                    future.set_result(message.result)
                return None
            
            return None
            
        except Exception as e:
            error_response = MCPMessage(
                id=getattr(message, 'id', None) if 'message' in locals() else None,
                error={"code": -32603, "message": str(e)},
                timestamp=datetime.now(),
                node_id=self.node_id,
                message_type="response"
            )
            return json.dumps(error_response.dict(), default=str)
    
    async def _handle_request(self, message: MCPMessage) -> MCPMessage:
        """处理请求消息"""
        try:
            handler = self.handlers[message.method]
            result = await handler(message.params or {})
            
            return MCPMessage(
                id=message.id,
                result=result,
                timestamp=datetime.now(),
                node_id=self.node_id,
                message_type="response"
            )
        except Exception as e:
            return MCPMessage(
                id=message.id,
                error={"code": -32602, "message": str(e)},
                timestamp=datetime.now(),
                node_id=self.node_id,
                message_type="response"
            )
    
    def create_request(self, method: str, params: Dict[str, Any]) -> str:
        """创建请求消息"""
        message = MCPMessage(
            id=str(uuid.uuid4()),
            method=method,
            params=params,
            timestamp=datetime.now(),
            node_id=self.node_id,
            message_type="request"
        )
        return json.dumps(message.dict(), default=str)
```

**1.3 测试协议实现**
```python
# tests/test_mcp_protocol.py
import pytest
import asyncio
from core.mcp.protocol import MCPProtocol
from core.mcp.message_types import MCPMessage

@pytest.mark.asyncio
async def test_protocol_basic_communication():
    """测试基础通信功能"""
    protocol = MCPProtocol("test_node")
    
    # 注册处理器
    async def echo_handler(params):
        return {"echo": params.get("message")}
    
    protocol.register_handler("echo", echo_handler)
    
    # 创建请求
    request = protocol.create_request("echo", {"message": "hello"})
    
    # 处理请求
    response = await protocol.handle_message(request)
    
    # 验证响应
    response_data = json.loads(response)
    assert response_data["result"]["echo"] == "hello"
```

### Task 2: 实现 registry.py 服务发现

#### 目标
实现服务自动发现和注册机制，支持服务器启动时自动声明能力

#### 实现步骤

**2.1 创建服务注册数据结构**
```python
# core/mcp/registry.py
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class ServiceCapability:
    """服务能力描述"""
    service_id: str
    node_id: str
    server_type: str  # 'recon', 'exploit', 'ai'
    capabilities: List[str]  # ['nmap_scan', 'gobuster_discovery', ...]
    endpoint: str  # 服务地址
    status: str = 'active'
    last_heartbeat: datetime = None
    
    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.now()

class ServiceRegistry:
    """服务注册中心"""
    
    def __init__(self):
        self.services: Dict[str, ServiceCapability] = {}
        self.capabilities_index: Dict[str, Set[str]] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self.heartbeat_timeout = 300  # 5分钟
    
    async def register_service(self, service: ServiceCapability) -> bool:
        """注册服务"""
        try:
            # 更新服务信息
            self.services[service.service_id] = service
            
            # 更新能力索引
            for capability in service.capabilities:
                if capability not in self.capabilities_index:
                    self.capabilities_index[capability] = set()
                self.capabilities_index[capability].add(service.service_id)
            
            logger.info(f"Service registered: {service.service_id} with capabilities {service.capabilities}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service: {e}")
            return False
    
    async def unregister_service(self, service_id: str) -> bool:
        """注销服务"""
        try:
            if service_id not in self.services:
                return False
            
            service = self.services[service_id]
            
            # 从能力索引中移除
            for capability in service.capabilities:
                if capability in self.capabilities_index:
                    self.capabilities_index[capability].discard(service_id)
                    if not self.capabilities_index[capability]:
                        del self.capabilities_index[capability]
            
            # 移除服务
            del self.services[service_id]
            
            logger.info(f"Service unregistered: {service_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister service: {e}")
            return False
    
    async def update_heartbeat(self, service_id: str) -> bool:
        """更新服务心跳"""
        if service_id in self.services:
            self.services[service_id].last_heartbeat = datetime.now()
            return True
        return False
    
    def discover_services(self, capability: str = None, server_type: str = None) -> List[ServiceCapability]:
        """发现服务"""
        services = list(self.services.values())
        
        # 按能力过滤
        if capability:
            if capability in self.capabilities_index:
                service_ids = self.capabilities_index[capability]
                services = [s for s in services if s.service_id in service_ids]
            else:
                return []
        
        # 按服务器类型过滤
        if server_type:
            services = [s for s in services if s.server_type == server_type]
        
        return services
    
    def get_service(self, service_id: str) -> Optional[ServiceCapability]:
        """获取特定服务"""
        return self.services.get(service_id)
    
    async def start_cleanup_task(self):
        """启动清理任务"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_services())
    
    async def stop_cleanup_task(self):
        """停止清理任务"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
    
    async def _cleanup_expired_services(self):
        """清理过期服务"""
        while True:
            try:
                now = datetime.now()
                expired_services = []
                
                for service_id, service in self.services.items():
                    if (now - service.last_heartbeat).seconds > self.heartbeat_timeout:
                        expired_services.append(service_id)
                
                for service_id in expired_services:
                    await self.unregister_service(service_id)
                    logger.warning(f"Service expired and removed: {service_id}")
                
                await asyncio.sleep(60)  # 每分钟检查一次
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                await asyncio.sleep(60)
```

**2.2 实现服务发现协议**
```python
# core/mcp/discovery.py
from .protocol import MCPProtocol
from .registry import ServiceRegistry, ServiceCapability

class ServiceDiscovery:
    """服务发现管理器"""
    
    def __init__(self, protocol: MCPProtocol, registry: ServiceRegistry):
        self.protocol = protocol
        self.registry = registry
        self._setup_handlers()
    
    def _setup_handlers(self):
        """设置发现协议处理器"""
        self.protocol.register_handler("service.register", self._handle_register)
        self.protocol.register_handler("service.unregister", self._handle_unregister)
        self.protocol.register_handler("service.discover", self._handle_discover)
        self.protocol.register_handler("service.heartbeat", self._handle_heartbeat)
        self.protocol.register_handler("service.list", self._handle_list)
    
    async def _handle_register(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理服务注册请求"""
        try:
            service = ServiceCapability(**params)
            success = await self.registry.register_service(service)
            return {"success": success, "service_id": service.service_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_unregister(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理服务注销请求"""
        service_id = params.get("service_id")
        success = await self.registry.unregister_service(service_id)
        return {"success": success}
    
    async def _handle_discover(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理服务发现请求"""
        capability = params.get("capability")
        server_type = params.get("server_type")
        
        services = self.registry.discover_services(capability, server_type)
        return {
            "services": [asdict(service) for service in services],
            "count": len(services)
        }
    
    async def _handle_heartbeat(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理心跳请求"""
        service_id = params.get("service_id")
        success = await self.registry.update_heartbeat(service_id)
        return {"success": success}
    
    async def _handle_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理服务列表请求"""
        services = list(self.registry.services.values())
        return {
            "services": [asdict(service) for service in services],
            "count": len(services)
        }
```

**2.3 服务器自动注册示例**
```python
# servers/recon/recon_server.py
from core.mcp.protocol import MCPProtocol
from core.mcp.registry import ServiceCapability

class ReconServer:
    """侦察服务器"""
    
    def __init__(self):
        self.protocol = MCPProtocol("recon_server_001")
        self.service_id = "recon_001"
        self.capabilities = [
            "nmap_port_scan",
            "gobuster_web_discovery", 
            "subdomain_enumeration",
            "smb_enumeration"
        ]
    
    async def start(self):
        """启动服务器并自动注册"""
        # 创建服务能力描述
        service = ServiceCapability(
            service_id=self.service_id,
            node_id="recon_node_001",
            server_type="recon",
            capabilities=self.capabilities,
            endpoint="http://localhost:8081"
        )
        
        # 发送注册请求
        register_request = self.protocol.create_request("service.register", asdict(service))
        
        # 发送到注册中心
        await self.send_to_registry(register_request)
        
        # 启动心跳任务
        asyncio.create_task(self._heartbeat_loop())
    
    async def _heartbeat_loop(self):
        """心跳循环"""
        while True:
            heartbeat_request = self.protocol.create_request("service.heartbeat", {
                "service_id": self.service_id
            })
            await self.send_to_registry(heartbeat_request)
            await asyncio.sleep(30)  # 30秒心跳
    
    async def send_to_registry(self, message: str):
        """发送消息到注册中心"""
        # 实现网络发送逻辑
        pass
```

---

## Phase 2: 能力封装 (工具层)

### Task 3: 实现工具包装器

#### 目标
使用异步方式封装渗透测试工具，避免直接调用 os.system，统一结果格式

#### 实现步骤

**3.1 创建基础工具包装器**
```python
# servers/base/tool_wrapper.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import subprocess
import tempfile
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ToolResult:
    """工具执行结果"""
    def __init__(self, success: bool, data: Dict[str, Any], 
                 execution_time: float, stdout: str = "", stderr: str = ""):
        self.success = success
        self.data = data
        self.execution_time = execution_time
        self.stdout = stdout
        self.stderr = stderr
        self.timestamp = datetime.now()

class BaseToolWrapper(ABC):
    """基础工具包装器"""
    
    def __init__(self, tool_path: str, timeout: int = 300):
        self.tool_path = tool_path
        self.timeout = timeout
    
    @abstractmethod
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """执行工具"""
        pass
    
    @abstractmethod
    def parse_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """解析工具输出"""
        pass
    
    async def _run_command(self, cmd: List[str], input_data: str = None) -> tuple[str, str, int]:
        """异步执行命令"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE if input_data else None
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=input_data.encode() if input_data else None),
                timeout=self.timeout
            )
            
            return stdout.decode(), stderr.decode(), process.returncode
            
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise Exception(f"Command timed out after {self.timeout} seconds")
        except Exception as e:
            raise Exception(f"Command execution failed: {e}")
```

**3.2 实现 Nmap 包装器**
```python
# servers/recon/tools/nmap_wrapper.py
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from servers.base.tool_wrapper import BaseToolWrapper, ToolResult

class NmapWrapper(BaseToolWrapper):
    """Nmap 工具包装器"""
    
    def __init__(self, nmap_path: str = "/usr/bin/nmap"):
        super().__init__(nmap_path)
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """执行 Nmap 扫描"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 构建命令
            cmd = await self._build_command(params)
            
            # 执行命令
            stdout, stderr, returncode = await self._run_command(cmd)
            
            # 解析结果
            parsed_data = self.parse_output(stdout, stderr)
            
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return ToolResult(
                success=returncode == 0,
                data=parsed_data,
                execution_time=execution_time,
                stdout=stdout,
                stderr=stderr
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ToolResult(
                success=False,
                data={"error": str(e)},
                execution_time=execution_time,
                stderr=str(e)
            )
    
    async def _build_command(self, params: Dict[str, Any]) -> List[str]:
        """构建 Nmap 命令"""
        cmd = [self.tool_path]
        
        # 基础参数
        target = params.get("target")
        if not target:
            raise ValueError("Target is required")
        
        # 扫描类型
        scan_type = params.get("scan_type", "syn")
        if scan_type == "syn":
            cmd.extend(["-sS"])
        elif scan_type == "connect":
            cmd.extend(["-sT"])
        elif scan_type == "udp":
            cmd.extend(["-sU"])
        elif scan_type == "ack":
            cmd.extend(["-sA"])
        
        # 端口范围
        ports = params.get("ports", "1-1000")
        cmd.extend(["-p", str(ports)])
        
        # 时序模板
        timing = params.get("timing", 3)
        cmd.extend(["-T", str(timing)])
        
        # 输出格式
        cmd.extend(["-oX", "-"])  # XML 输出到 stdout
        
        # 脚本
        scripts = params.get("scripts", [])
        if scripts:
            cmd.extend(["--script", ",".join(scripts)])
        
        # 目标
        cmd.append(target)
        
        return cmd
    
    def parse_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """解析 Nmap XML 输出"""
        try:
            root = ET.fromstring(stdout)
            
            hosts = []
            total_ports = 0
            open_ports = 0
            
            for host in root.findall("host"):
                host_info = {
                    "ip": "",
                    "hostname": "",
                    "status": "",
                    "os": "",
                    "ports": []
                }
                
                # 获取 IP 地址
                address = host.find(".//address[@addrtype='ipv4']")
                if address is not None:
                    host_info["ip"] = address.get("addr")
                
                # 获取主机名
                hostname = host.find(".//hostname[@type='user']")
                if hostname is not None:
                    host_info["hostname"] = hostname.get("name")
                
                # 获取状态
                status = host.find("status")
                if status is not None:
                    host_info["status"] = status.get("state")
                
                # 获取操作系统信息
                os_match = host.find(".//osclass")
                if os_match is not None:
                    host_info["os"] = f"{os_match.get('vendor', '')} {os_match.get('osfamily', '')} {os_match.get('osgen', '')}".strip()
                
                # 获取端口信息
                for port in host.findall(".//port"):
                    port_info = {
                        "port": int(port.get("portid")),
                        "protocol": port.get("protocol"),
                        "state": "",
                        "service": "",
                        "version": "",
                        "banner": ""
                    }
                    
                    total_ports += 1
                    
                    # 端口状态
                    state = port.find("state")
                    if state is not None:
                        port_info["state"] = state.get("state")
                        if port_info["state"] == "open":
                            open_ports += 1
                    
                    # 服务信息
                    service = port.find("service")
                    if service is not None:
                        port_info["service"] = service.get("name", "")
                        port_info["version"] = service.get("version", "")
                        port_info["banner"] = service.get("product", "")
                    
                    host_info["ports"].append(port_info)
                
                hosts.append(host_info)
            
            return {
                "scan_type": "nmap_port_scan",
                "hosts": hosts,
                "statistics": {
                    "total_hosts": len(hosts),
                    "total_ports": total_ports,
                    "open_ports": open_ports,
                    "up_hosts": len([h for h in hosts if h["status"] == "up"])
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to parse nmap output: {e}"}
```

**3.3 实现 Gobuster 包装器**
```python
# servers/recon/tools/gobuster_wrapper.py
import re
from typing import Dict, Any, List
from servers.base.tool_wrapper import BaseToolWrapper, ToolResult

class GobusterWrapper(BaseToolWrapper):
    """Gobuster 工具包装器"""
    
    def __init__(self, gobuster_path: str = "/usr/bin/gobuster"):
        super().__init__(gobuster_path)
    
    async def execute(self, params: Dict[str, Any]) -> ToolResult:
        """执行 Gobuster 扫描"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            cmd = await self._build_command(params)
            stdout, stderr, returncode = await self._run_command(cmd)
            
            parsed_data = self.parse_output(stdout, stderr)
            execution_time = asyncio.get_event_loop().time() - start_time
            
            return ToolResult(
                success=returncode == 0,
                data=parsed_data,
                execution_time=execution_time,
                stdout=stdout,
                stderr=stderr
            )
            
        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            return ToolResult(
                success=False,
                data={"error": str(e)},
                execution_time=execution_time,
                stderr=str(e)
            )
    
    async def _build_command(self, params: Dict[str, Any]) -> List[str]:
        """构建 Gobuster 命令"""
        cmd = [self.tool_path, "dir"]
        
        # 目标 URL
        target = params.get("target")
        if not target:
            raise ValueError("Target URL is required")
        cmd.extend(["-u", target])
        
        # 字典文件
        wordlist = params.get("wordlist", "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt")
        cmd.extend(["-w", wordlist])
        
        # 文件扩展名
        extensions = params.get("extensions", [".php", ".html", ".js", ".txt"])
        if extensions:
            cmd.extend(["-x", ",".join(extensions)])
        
        # 线程数
        threads = params.get("threads", 10)
        cmd.extend(["-t", str(threads)])
        
        # 状态码
        status_codes = params.get("status_codes", [200, 301, 302, 403])
        cmd.extend(["--status-codes", ",".join(map(str, status_codes))])
        
        # 输出文件
        cmd.extend(["-o", "-"])  # 输出到 stdout
        
        # 静默模式
        cmd.append("-q")
        
        return cmd
    
    def parse_output(self, stdout: str, stderr: str) -> Dict[str, Any]:
        """解析 Gobuster 输出"""
        try:
            lines = stdout.strip().split('\n')
            directories = []
            files = []
            
            for line in lines:
                if not line or line.startswith('='):
                    continue
                
                # 解析格式: /path (Status: 200) [Size: 1234]
                match = re.match(r'^(.+?)\s+\(Status:\s+(\d+)\)\s+\[Size:\s+(\d+)\]', line)
                if match:
                    path, status, size = match.groups()
                    
                    entry = {
                        "path": path,
                        "status_code": int(status),
                        "size": int(size),
                        "url": f"{path}"
                    }
                    
                    if path.endswith('/'):
                        directories.append(entry)
                    else:
                        files.append(entry)
            
            return {
                "scan_type": "web_discovery",
                "directories": directories,
                "files": files,
                "statistics": {
                    "total_findings": len(directories) + len(files),
                    "directories_found": len(directories),
                    "files_found": len(files)
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to parse gobuster output: {e}"}
```

**3.4 统一扫描结果模型**
```python
# core/knowledge/scan_result_model.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ScanType(str, Enum):
    PORT_SCAN = "port_scan"
    WEB_DISCOVERY = "web_discovery"
    VULNERABILITY_SCAN = "vulnerability_scan"
    SUBDOMAIN_ENUM = "subdomain_enum"
    SMB_ENUM = "smb_enum"

class ServiceInfo(BaseModel):
    port: int
    protocol: str
    state: str
    service: str = ""
    version: str = ""
    banner: str = ""

class HostInfo(BaseModel):
    ip: str
    hostname: str = ""
    status: str = ""
    os: str = ""
    services: List[ServiceInfo] = Field(default_factory=list)

class WebFinding(BaseModel):
    path: str
    status_code: int
    size: int
    url: str

class VulnerabilityInfo(BaseModel):
    cve: str = ""
    severity: str
    description: str
    confidence: float = 0.0

class ScanResult(BaseModel):
    scan_id: str
    scan_type: ScanType
    target: str
    timestamp: datetime
    execution_time: float
    success: bool
    hosts: List[HostInfo] = Field(default_factory=list)
    web_findings: List[WebFinding] = Field(default_factory=list)
    vulnerabilities: List[VulnerabilityInfo] = Field(default_factory=list)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    raw_output: str = ""
    error_message: str = ""
    
    def to_unified_format(self) -> Dict[str, Any]:
        """转换为统一格式"""
        return {
            "scan_id": self.scan_id,
            "scan_type": self.scan_type.value,
            "target": self.target,
            "timestamp": self.timestamp.isoformat(),
            "execution_time": self.execution_time,
            "success": self.success,
            "assets": [
                {
                    "ip": host.ip,
                    "hostname": host.hostname,
                    "os": host.os,
                    "services": [
                        {
                            "port": service.port,
                            "protocol": service.protocol,
                            "service": service.service,
                            "version": service.version,
                            "state": service.state
                        } for service in host.services
                    ],
                    "vulnerabilities": [
                        {
                            "cve": vuln.cve,
                            "severity": vuln.severity,
                            "description": vuln.description,
                            "confidence": vuln.confidence
                        } for vuln in self.vulnerabilities
                    ]
                } for host in self.hosts
            ],
            "web_findings": [
                {
                    "path": finding.path,
                    "status_code": finding.status_code,
                    "size": finding.size,
                    "url": finding.url
                } for finding in self.web_findings
            ],
            "statistics": self.statistics
        }
```

---

## Phase 3: AI 决策和调度 (核心层)

### Task 4: 实现 task_decomposer.py

#### 目标
实现 AI 任务分解逻辑，根据输入目标智能规划执行步骤

#### 实现步骤

**4.1 创建任务分解器**
```python
# core/scheduler/task_decomposer.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class TaskStep:
    """任务步骤"""
    step_id: str
    task_type: str  # 'port_scan', 'web_discovery', 'vuln_scan'
    target: str
    parameters: Dict[str, Any]
    dependencies: List[str] = None  # 依赖的步骤ID
    priority: int = 1  # 优先级 1-5
    estimated_duration: int = 300  # 预估时间(秒)
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class TaskPlan:
    """任务执行计划"""
    plan_id: str
    objective: str
    target: str
    steps: List[TaskStep]
    created_at: datetime
    estimated_total_duration: int

class TaskDecomposer:
    """任务分解器"""
    
    def __init__(self):
        self.task_templates = self._load_task_templates()
    
    def _load_task_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载任务模板"""
        return {
            "full_penetration_test": {
                "description": "完整渗透测试",
                "steps": [
                    {
                        "task_type": "port_scan",
                        "priority": 5,
                        "parameters": {
                            "scan_type": "syn",
                            "ports": "1-1000",
                            "timing": 3
                        }
                    },
                    {
                        "task_type": "web_discovery", 
                        "priority": 4,
                        "parameters": {
                            "threads": 10,
                            "extensions": [".php", ".html", ".js"]
                        },
                        "dependencies": ["port_scan"]
                    },
                    {
                        "task_type": "vulnerability_scan",
                        "priority": 3,
                        "parameters": {
                            "severity_threshold": "medium"
                        },
                        "dependencies": ["port_scan", "web_discovery"]
                    }
                ]
            },
            "reconnaissance_only": {
                "description": "仅信息收集",
                "steps": [
                    {
                        "task_type": "port_scan",
                        "priority": 5,
                        "parameters": {
                            "scan_type": "syn",
                            "ports": "1-1000"
                        }
                    },
                    {
                        "task_type": "web_discovery",
                        "priority": 4,
                        "parameters": {},
                        "dependencies": ["port_scan"]
                    }
                ]
            }
        }
    
    async def decompose_task(self, objective: str, target: str, 
                           context: Dict[str, Any] = None) -> TaskPlan:
        """分解任务为执行步骤"""
        try:
            # 分析目标类型
            target_type = self._analyze_target(target)
            
            # 选择任务模板
            template = self._select_template(objective, target_type)
            
            # 生成执行步骤
            steps = await self._generate_steps(template, target, context)
            
            # 估算总时间
            total_duration = sum(step.estimated_duration for step in steps)
            
            # 创建任务计划
            plan = TaskPlan(
                plan_id=f"plan_{int(datetime.now().timestamp())}",
                objective=objective,
                target=target,
                steps=steps,
                created_at=datetime.now(),
                estimated_total_duration=total_duration
            )
            
            logger.info(f"Task decomposed: {objective} -> {len(steps)} steps")
            return plan
            
        except Exception as e:
            logger.error(f"Task decomposition failed: {e}")
            raise
    
    def _analyze_target(self, target: str) -> str:
        """分析目标类型"""
        if target.startswith("http"):
            return "web_application"
        elif "/" in target and "." in target:
            return "network_range"
        else:
            return "single_host"
    
    def _select_template(self, objective: str, target_type: str) -> Dict[str, Any]:
        """选择任务模板"""
        objective_lower = objective.lower()
        
        if "full" in objective_lower or "complete" in objective_lower:
            return self.task_templates["full_penetration_test"]
        elif "recon" in objective_lower or "discover" in objective_lower:
            return self.task_templates["reconnaissance_only"]
        else:
            # 默认使用完整测试模板
            return self.task_templates["full_penetration_test"]
    
    async def _generate_steps(self, template: Dict[str, Any], target: str, 
                            context: Dict[str, Any] = None) -> List[TaskStep]:
        """生成执行步骤"""
        steps = []
        
        for i, step_config in enumerate(template["steps"]):
            step_id = f"step_{i+1}"
            
            # 合并参数
            parameters = step_config["parameters"].copy()
            parameters["target"] = target
            
            if context:
                parameters.update(context.get("parameters", {}))
            
            # 创建任务步骤
            step = TaskStep(
                step_id=step_id,
                task_type=step_config["task_type"],
                target=target,
                parameters=parameters,
                dependencies=step_config.get("dependencies", []),
                priority=step_config["priority"],
                estimated_duration=self._estimate_duration(step_config["task_type"], parameters)
            )
            
            steps.append(step)
        
        return steps
    
    def _estimate_duration(self, task_type: str, parameters: Dict[str, Any]) -> int:
        """估算任务执行时间"""
        base_durations = {
            "port_scan": 300,
            "web_discovery": 600,
            "vulnerability_scan": 900,
            "subdomain_enum": 1200,
            "smb_enum": 300
        }
        
        base_duration = base_durations.get(task_type, 300)
        
        # 根据参数调整时间
        if task_type == "port_scan":
            ports = parameters.get("ports", "1-1000")
            if "1-65535" in ports:
                base_duration *= 4
            elif "top-1000" in ports:
                base_duration *= 0.5
        
        elif task_type == "web_discovery":
            threads = parameters.get("threads", 10)
            base_duration = base_duration * (10 / max(threads, 1))
        
        return int(base_duration)
```

**4.2 实现 AI 决策逻辑**
```python
# servers/ai/capabilities/task_planner.py
from typing import Dict, Any, List
from core.scheduler.task_decomposer import TaskDecomposer, TaskPlan
import logging

logger = logging.getLogger(__name__)

class TaskPlanner:
    """AI 任务规划器"""
    
    def __init__(self):
        self.decomposer = TaskDecomposer()
        self.execution_history = []
    
    async def plan_execution(self, objective: str, target: str, 
                           available_services: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """规划任务执行"""
        try:
            # 分解任务
            task_plan = await self.decomposer.decompose_task(objective, target)
            
            # 优化执行顺序
            optimized_steps = await self._optimize_execution_order(
                task_plan.steps, available_services
            )
            
            # 分配服务节点
            assigned_steps = await self._assign_services(optimized_steps, available_services)
            
            # 生成执行计划
            execution_plan = {
                "plan_id": task_plan.plan_id,
                "objective": objective,
                "target": target,
                "steps": assigned_steps,
                "estimated_duration": task_plan.estimated_total_duration,
                "created_at": task_plan.created_at.isoformat(),
                "execution_graph": self._build_execution_graph(assigned_steps)
            }
            
            logger.info(f"Execution plan created: {len(assigned_steps)} steps")
            return execution_plan
            
        except Exception as e:
            logger.error(f"Task planning failed: {e}")
            raise
    
    async def _optimize_execution_order(self, steps: List[TaskStep], 
                                      available_services: List[Dict[str, Any]] = None) -> List[TaskStep]:
        """优化执行顺序"""
        # 基于依赖关系和优先级排序
        optimized = []
        remaining = steps.copy()
        
        while remaining:
            # 找到没有未完成依赖的步骤
            ready_steps = [
                step for step in remaining 
                if all(dep not in [s.step_id for s in remaining] for dep in step.dependencies)
            ]
            
            if not ready_steps:
                # 如果没有就绪的步骤，可能有循环依赖
                logger.warning("Circular dependency detected, adding remaining steps")
                ready_steps = remaining
            
            # 按优先级排序
            ready_steps.sort(key=lambda x: x.priority, reverse=True)
            
            # 添加最高优先级的步骤
            next_step = ready_steps[0]
            optimized.append(next_step)
            remaining.remove(next_step)
        
        return optimized
    
    async def _assign_services(self, steps: List[TaskStep], 
                             available_services: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """分配服务节点"""
        assigned_steps = []
        
        for step in steps:
            # 找到支持该任务类型的服务
            suitable_services = [
                service for service in (available_services or [])
                if step.task_type in service.get("capabilities", [])
            ]
            
            if suitable_services:
                # 选择负载最低的服务
                best_service = min(suitable_services, 
                                 key=lambda x: x.get("load", 0))
                
                assigned_step = {
                    "step_id": step.step_id,
                    "task_type": step.task_type,
                    "target": step.target,
                    "parameters": step.parameters,
                    "dependencies": step.dependencies,
                    "priority": step.priority,
                    "estimated_duration": step.estimated_duration,
                    "assigned_service": best_service["service_id"],
                    "service_endpoint": best_service["endpoint"]
                }
            else:
                # 没有找到合适的服务
                assigned_step = {
                    "step_id": step.step_id,
                    "task_type": step.task_type,
                    "target": step.target,
                    "parameters": step.parameters,
                    "dependencies": step.dependencies,
                    "priority": step.priority,
                    "estimated_duration": step.estimated_duration,
                    "assigned_service": None,
                    "service_endpoint": None
                }
            
            assigned_steps.append(assigned_step)
        
        return assigned_steps
    
    def _build_execution_graph(self, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """构建执行图"""
        nodes = []
        edges = []
        
        for step in steps:
            nodes.append({
                "id": step["step_id"],
                "type": step["task_type"],
                "status": "pending"
            })
            
            for dep in step["dependencies"]:
                edges.append({
                    "from": dep,
                    "to": step["step_id"],
                    "type": "dependency"
                })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
```

### Task 5: 实现 DAG 调度

#### 目标
管理任务依赖关系，实现基于 DAG 的任务调度

#### 实现步骤

**5.1 创建 DAG 调度器**
```python
# core/scheduler/dag_scheduler.py
from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class DAGNode:
    """DAG 节点"""
    node_id: str
    task_type: str
    target: str
    parameters: Dict[str, Any]
    dependencies: Set[str]
    assigned_service: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

class DAGScheduler:
    """DAG 任务调度器"""
    
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
        self.execution_queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Set[str] = set()
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        self.max_concurrent_tasks = 5
        self._scheduler_task: Optional[asyncio.Task] = None
    
    def add_task(self, task_data: Dict[str, Any]) -> str:
        """添加任务到 DAG"""
        node = DAGNode(
            node_id=task_data["step_id"],
            task_type=task_data["task_type"],
            target=task_data["target"],
            parameters=task_data["parameters"],
            dependencies=set(task_data.get("dependencies", [])),
            assigned_service=task_data.get("assigned_service")
        )
        
        self.nodes[node.node_id] = node
        logger.info(f"Task added to DAG: {node.node_id}")
        return node.node_id
    
    def build_from_execution_plan(self, execution_plan: Dict[str, Any]) -> None:
        """从执行计划构建 DAG"""
        for step in execution_plan["steps"]:
            self.add_task(step)
        
        logger.info(f"DAG built with {len(self.nodes)} tasks")
    
    async def start_execution(self) -> None:
        """开始执行 DAG"""
        if self._scheduler_task is None:
            self._scheduler_task = asyncio.create_task(self._scheduler_loop())
            logger.info("DAG scheduler started")
    
    async def stop_execution(self) -> None:
        """停止执行 DAG"""
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
            self._scheduler_task = None
            logger.info("DAG scheduler stopped")
    
    async def _scheduler_loop(self) -> None:
        """调度器主循环"""
        while True:
            try:
                # 检查可以执行的任务
                ready_tasks = self._get_ready_tasks()
                
                # 启动就绪的任务
                for task_id in ready_tasks:
                    if len(self.running_tasks) < self.max_concurrent_tasks:
                        await self._start_task(task_id)
                
                # 等待一段时间再检查
                await asyncio.sleep(1)
                
                # 检查是否所有任务都完成
                if self._is_execution_complete():
                    break
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(5)
    
    def _get_ready_tasks(self) -> List[str]:
        """获取可以执行的任务"""
        ready_tasks = []
        
        for task_id, node in self.nodes.items():
            if (node.status == "pending" and 
                task_id not in self.running_tasks and
                self._are_dependencies_completed(task_id)):
                ready_tasks.append(task_id)
        
        # 按优先级排序（这里简化为按任务类型）
        priority_order = {"port_scan": 1, "web_discovery": 2, "vulnerability_scan": 3}
        ready_tasks.sort(key=lambda x: priority_order.get(self.nodes[x].task_type, 99))
        
        return ready_tasks
    
    def _are_dependencies_completed(self, task_id: str) -> bool:
        """检查依赖是否完成"""
        node = self.nodes[task_id]
        return all(dep in self.completed_tasks for dep in node.dependencies)
    
    async def _start_task(self, task_id: str) -> None:
        """启动任务执行"""
        node = self.nodes[task_id]
        
        try:
            node.status = "running"
            node.start_time = datetime.now()
            self.running_tasks.add(task_id)
            
            logger.info(f"Starting task: {task_id}")
            
            # 执行任务（这里需要调用实际的服务）
            result = await self._execute_task(node)
            
            # 更新任务状态
            node.end_time = datetime.now()
            node.result = result
            node.status = "completed"
            
            self.running_tasks.remove(task_id)
            self.completed_tasks.add(task_id)
            
            logger.info(f"Task completed: {task_id}")
            
        except Exception as e:
            node.end_time = datetime.now()
            node.status = "failed"
            node.result = {"error": str(e)}
            
            self.running_tasks.remove(task_id)
            self.failed_tasks.add(task_id)
            
            logger.error(f"Task failed: {task_id}, error: {e}")
    
    async def _execute_task(self, node: DAGNode) -> Dict[str, Any]:
        """执行具体任务"""
        # 这里需要根据任务类型调用相应的服务
        if node.task_type == "port_scan":
            return await self._execute_port_scan(node)
        elif node.task_type == "web_discovery":
            return await self._execute_web_discovery(node)
        elif node.task_type == "vulnerability_scan":
            return await self._execute_vulnerability_scan(node)
        else:
            raise ValueError(f"Unsupported task type: {node.task_type}")
    
    async def _execute_port_scan(self, node: DAGNode) -> Dict[str, Any]:
        """执行端口扫描任务"""
        # 模拟执行
        await asyncio.sleep(5)  # 模拟扫描时间
        
        return {
            "task_type": "port_scan",
            "target": node.target,
            "open_ports": [22, 80, 443, 8080],
            "services": [
                {"port": 22, "service": "ssh"},
                {"port": 80, "service": "http"},
                {"port": 443, "service": "https"},
                {"port": 8080, "service": "http-alt"}
            ]
        }
    
    async def _execute_web_discovery(self, node: DAGNode) -> Dict[str, Any]:
        """执行 Web 发现任务"""
        # 模拟执行
        await asyncio.sleep(10)
        
        return {
            "task_type": "web_discovery",
            "target": node.target,
            "directories": ["/admin", "/login", "/api"],
            "files": ["/index.html", "/config.php"]
        }
    
    async def _execute_vulnerability_scan(self, node: DAGNode) -> Dict[str, Any]:
        """执行漏洞扫描任务"""
        # 模拟执行
        await asyncio.sleep(15)
        
        return {
            "task_type": "vulnerability_scan",
            "target": node.target,
            "vulnerabilities": [
                {"cve": "CVE-2021-1234", "severity": "high"},
                {"cve": "CVE-2021-5678", "severity": "medium"}
            ]
        }
    
    def _is_execution_complete(self) -> bool:
        """检查执行是否完成"""
        total_tasks = len(self.nodes)
        completed_and_failed = len(self.completed_tasks) + len(self.failed_tasks)
        return completed_and_failed >= total_tasks
    
    def get_execution_status(self) -> Dict[str, Any]:
        """获取执行状态"""
        return {
            "total_tasks": len(self.nodes),
            "pending_tasks": len([n for n in self.nodes.values() if n.status == "pending"]),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "progress": len(self.completed_tasks) / len(self.nodes) if self.nodes else 0
        }
    
    def get_task_details(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务详情"""
        if task_id not in self.nodes:
            return None
        
        node = self.nodes[task_id]
        return {
            "task_id": node.node_id,
            "task_type": node.task_type,
            "target": node.target,
            "status": node.status,
            "start_time": node.start_time.isoformat() if node.start_time else None,
            "end_time": node.end_time.isoformat() if node.end_time else None,
            "duration": (node.end_time - node.start_time).total_seconds() if node.start_time and node.end_time else None,
            "result": node.result
        }
```

---

## 开发最佳实践

### 1. 代码质量保证
```python
# 使用类型注解
def process_scan_result(result: Dict[str, Any]) -> ScanResult:
    """处理扫描结果"""
    pass

# 异常处理
try:
    result = await tool.execute(params)
except ToolExecutionError as e:
    logger.error(f"Tool execution failed: {e}")
    return ToolResult(success=False, data={"error": str(e)})

# 日志记录
logger.info(f"Starting {task_type} on {target}")
logger.debug(f"Parameters: {params}")
```

### 2. 性能优化
```python
# 使用连接池
import aiohttp
session = aiohttp.ClientSession()

# 批量处理
async def batch_execute(tasks: List[Dict]) -> List[ToolResult]:
    semaphore = asyncio.Semaphore(10)
    async with semaphore:
        results = await asyncio.gather(*[execute_task(task) for task in tasks])
    return results
```

### 3. 测试策略
```python
# 单元测试
@pytest.mark.asyncio
async def test_nmap_wrapper():
    wrapper = NmapWrapper()
    result = await wrapper.execute({"target": "127.0.0.1"})
    assert result.success

# 集成测试
async def test_end_to_end_workflow():
    # 测试完整的工作流程
    pass
```

---

## 总结

本实现指南提供了 HexStrike AI 系统的完整开发路径：

1. **Phase 1** 建立了坚实的通信基础，实现了 MCP 协议和服务发现
2. **Phase 2** 封装了渗透测试工具，提供了统一的异步接口
3. **Phase 3** 实现了智能任务分解和 DAG 调度，支持复杂的依赖关系

通过遵循本指南，开发团队可以构建一个功能完整、性能优异的分布式渗透测试协同系统，为学术研究和实际应用提供强有力的技术支撑。
