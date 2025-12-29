# 实验室环境设置指南

## 概述

本文档详细记录了 HexStrike AI 分布式渗透测试协同系统的实验环境配置，确保实验结果的"可重现性"。包含虚拟机布局、网络配置、漏洞类型描述等关键信息。

---

## 实验环境架构

### 网络拓扑图

```
┌─────────────────────────────────────────────────────────────┐
│                    Host Machine (Windows/Linux)              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Kali Linux    │  │  Metasploitable3│  │    DVWA      │ │
│  │   (Attacker)    │  │   (Target)      │  │  (Web Target)│ │
│  │  192.168.56.101 │  │  192.168.56.102 │  │192.168.56.103│ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│         │                     │                     │       │
│         └─────────────────────┼─────────────────────┘       │
│                               │                             │
│                    ┌─────────────────┐                     │
│                    │  Virtual Switch │                     │
│                    │  (Host-only)    │                     │
│                    │   192.168.56.0/24│                    │
│                    └─────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

### IP 地址分配

| 虚拟机 | IP 地址 | 用途 | 操作系统 | 主要服务 |
|--------|---------|------|----------|----------|
| Kali Linux | 192.168.56.101 | 攻击者节点 | Kali Linux 2023.4 | 渗透测试工具 |
| Metasploitable3 | 192.168.56.102 | 目标系统 | Ubuntu 14.04 | 多种漏洞服务 |
| DVWA | 192.168.56.103 | Web 目标 | Debian 10 | Web 应用漏洞 |

---

## 虚拟机详细配置

### 1. Kali Linux (攻击者节点)

#### 基础配置
```yaml
vm_name: "Kali-Linux-HexStrike"
os_type: "Linux"
version: "2023.4"
memory: "4GB"
cpu_cores: 2
disk_space: "80GB"
network_adapter: "Host-only Adapter"
ip_address: "192.168.56.101"
netmask: "255.255.255.0"
gateway: "192.168.56.1"
```

#### 安装的渗透测试工具
```bash
# 网络扫描工具
sudo apt update && sudo apt install -y nmap masscan rustscan

# Web 发现工具
sudo apt install -y gobuster dirb dirsearch ffuf

# 漏洞扫描工具
sudo apt install -y nuclei nikto

# 子域名枚举
sudo apt install -y amass subfinder

# SMB 枚举
sudo apt install -y smbclient enum4linux-ng smbmap

# 数据库工具
sudo apt install -y sqlmap

# Python 环境
sudo apt install -y python3 python3-pip
pip3 install requests beautifulsoup4 lxml

# 其他依赖
sudo apt install -y git curl wget vim
```

#### Python 环境配置
```bash
# 创建虚拟环境
python3 -m venv /opt/hexstrike-env
source /opt/hexstrike-env/bin/activate

# 安装项目依赖
pip install fastapi uvicorn pydantic
pip install redis celery
pip install psutil
pip install aiohttp aiofiles
pip install xmltodict
```

#### 服务配置
```yaml
# Redis 服务
redis_port: 6379
redis_bind: "127.0.0.1"

# HexStrike 服务配置
mcp_port: 8080
recon_server_port: 8081
exploit_server_port: 8082
ai_server_port: 8083
```

### 2. Metasploitable3 (目标系统)

#### 基础配置
```yaml
vm_name: "Metasploitable3-HexStrike"
os_type: "Linux"
distribution: "Ubuntu 14.04 LTS"
memory: "2GB"
cpu_cores: 1
disk_space: "40GB"
network_adapter: "Host-only Adapter"
ip_address: "192.168.56.102"
netmask: "255.255.255.0"
gateway: "192.168.56.1"
```

#### 漏洞服务详情

| 端口 | 服务 | 版本 | 漏洞类型 | 描述 |
|------|------|------|----------|------|
| 21 | FTP | vsftpd 2.3.4 | 远程代码执行 | vsftpd 后门漏洞 |
| 22 | SSH | OpenSSH 5.1p1 | 弱密码 | 默认凭据 msfadmin:msfadmin |
| 23 | Telnet | Linux telnetd | 明文传输 | 无认证访问 |
| 25 | SMTP | Postfix 2.7.1 | 信息泄露 | 版本信息泄露 |
| 53 | DNS | BIND 9.7.0 | DNS 劫持 | 区域传输漏洞 |
| 80 | HTTP | Apache 2.2.14 | 多种漏洞 | 目录遍历、文件包含 |
| 110 | POP3 | Dovecot 1.0.10 | 明文认证 | 弱认证机制 |
| 139 | SMB | Samba 3.4.7 | 远程代码执行 | Samba 蠕虫漏洞 |
| 143 | IMAP | Dovecot 1.0.10 | 明文认证 | 弱认证机制 |
| 445 | SMB | Samba 3.4.7 | 远程代码执行 | MS08-067 |
| 512 | Rexec | Linux rexecd | 信任关系 | 无认证执行 |
| 513 | Rlogin | Linux rlogind | 信任关系 | 无认证登录 |
| 514 | Rsh | Linux rshd | 信任关系 | 无认证执行 |
| 1524 | IngresDB | Ingres | 后门 | 后门服务 |
| 2049 | NFS | nfs-kernel-server | 权限提升 | 未授权访问 |
| 3306 | MySQL | MySQL 5.1.41 | 弱密码 | root:root |
| 5432 | PostgreSQL | PostgreSQL 8.3.7 | 弱密码 | postgres:postgres |
| 5900 | VNC | RealVNC 4.1 | 弱密码 | password:vnc |
| 6000 | X11 | X.Org Server | 权限提升 | 未授权访问 |
| 6667 | IRC | UnrealIRCd 3.2.8.1 | 远程代码执行 | 后门命令执行 |
| 8009 | AJP | Tomcat 6.0.18 | 信息泄露 | AJP 协议泄露 |
| 8180 | HTTP | Tomcat 6.0.18 | 弱密码 | manager:tomcat |

#### 配置文件示例
```bash
# /etc/ssh/sshd_config (部分)
PermitRootLogin yes
PasswordAuthentication yes
UsePAM yes

# /etc/samba/smb.conf (部分)
security = share
guest ok = yes
```

### 3. DVWA (Web 应用目标)

#### 基础配置
```yaml
vm_name: "DVWA-HexStrike"
os_type: "Linux"
distribution: "Debian 10"
memory: "1GB"
cpu_cores: 1
disk_space: "20GB"
network_adapter: "Host-only Adapter"
ip_address: "192.168.56.103"
netmask: "255.255.255.0"
gateway: "192.168.56.1"
```

#### DVWA 配置
```php
// /var/www/html/config/config.inc.php
$_DVWA[ 'db_server' ]   = '127.0.0.1';
$_DVWA[ 'db_database' ] = 'dvwa';
$_DVWA[ 'db_user' ]     = 'dvwa';
$_DVWA[ 'db_password' ] = 'p@ssw0rd';

// 安全级别设置
$_DVWA[ 'default_security_level' ] = 'low';
```

#### Web 应用漏洞详情

| 漏洞类型 | 路径 | 参数 | 描述 | 影响级别 |
|----------|------|------|------|----------|
| SQL 注入 | /vulnerabilities/sqli/ | id, submit | 盲注、联合查询 | 高 |
| XSS (反射型) | /vulnerabilities/xss_r/ | name, submit | 反射型 XSS | 中 |
| XSS (存储型) | /vulnerabilities/xss_s/ | txtName, txtMessage, btnSign | 存储型 XSS | 高 |
| CSRF | /vulnerabilities/csrf/ | password_new, password_conf, Change | CSRF 攻击 | 中 |
| 文件包含 | /vulnerabilities/fi/ | page | 本地/远程文件包含 | 高 |
| 文件上传 | /vulnerabilities/upload/ | uploaded, Upload | 任意文件上传 | 高 |
| 弱认证 | /login.php | username, password | 弱密码保护 | 中 |
| 命令注入 | /vulnerabilities/exec/ | ip, submit | 系统命令注入 | 高 |
| 暴力破解 | /vulnerabilities/brute/ | username, password, Login | 暴力破解 | 低 |

#### 数据库配置
```sql
-- DVWA 数据库用户
CREATE USER 'dvwa'@'localhost' IDENTIFIED BY 'p@ssw0rd';
CREATE DATABASE dvwa;
GRANT ALL PRIVILEGES ON dvwa.* TO 'dvwa'@'localhost';
```

---

## 网络配置详解

### Host-only 网络设置

#### VirtualBox 网络配置
```bash
# 创建 Host-only 网络
VBoxManage hostonlyif create
VBoxManage hostonlyif ipconfig "VirtualBox Host-Only Ethernet Adapter" --ip 192.168.56.1 --netmask 255.255.255.0

# 启用 DHCP 服务器
VBoxManage dhcpserver add --ifname "VirtualBox Host-Only Ethernet Adapter" --ip 192.168.56.100 --netmask 255.255.255.0 --lowerip 192.168.56.101 --upperip 192.168.56.200 --enable
```

#### 静态 IP 配置模板

**Kali Linux (/etc/network/interfaces)**
```bash
auto eth1
iface eth1 inet static
address 192.168.56.101
netmask 255.255.255.0
gateway 192.168.56.1
dns-nameservers 8.8.8.8 8.8.4.4
```

**Metasploitable3 (/etc/network/interfaces)**
```bash
auto eth0
iface eth0 inet static
address 192.168.56.102
netmask 255.255.255.0
gateway 192.168.56.1
```

**DVWA (/etc/network/interfaces)**
```bash
auto eth0
iface eth0 inet static
address 192.168.56.103
netmask 255.255.255.0
gateway 192.168.56.1
```

---

## 实验场景配置

### 场景 1: 基础网络扫描
```yaml
scenario_id: "basic_network_scan"
target_range: "192.168.56.102/32"
expected_findings:
  - open_ports: [21, 22, 23, 25, 53, 80, 110, 139, 143, 445, 512, 513, 514, 1524, 2049, 3306, 5432, 5900, 6000, 6667, 8009, 8180]
  - services: ["vsftpd", "ssh", "telnet", "smtp", "dns", "http", "pop3", "smb"]
  - os_fingerprint: "Linux"
```

### 场景 2: Web 应用发现
```yaml
scenario_id: "web_discovery"
target_range: "192.168.56.103/32"
expected_findings:
  - web_ports: [80]
  - web_applications: ["DVWA"]
  - directories: ["/admin", "/login", "/vulnerabilities"]
  - technologies: ["PHP", "MySQL", "Apache"]
```

### 场景 3: 漏洞验证
```yaml
scenario_id: "vulnerability_verification"
targets: ["192.168.56.102", "192.168.56.103"]
expected_vulnerabilities:
  metasploitable3:
    - cve: "CVE-2011-2523"
      service: "vsftpd"
      port: 21
      severity: "critical"
    - cve: "CVE-2008-4250"
      service: "samba"
      port: 445
      severity: "high"
  dvwa:
    - type: "sql_injection"
      path: "/vulnerabilities/sqli/"
      severity: "high"
    - type: "xss_stored"
      path: "/vulnerabilities/xss_s/"
      severity: "medium"
```

---

## 自动化部署脚本

### Vagrant 配置文件 (Vagrantfile)
```ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  
  # Kali Linux
  config.vm.define "kali" do |kali|
    kali.vm.box = "kalilinux/rolling"
    kali.vm.hostname = "kali-hexstrike"
    kali.vm.network "private_network", ip: "192.168.56.101"
    kali.vm.provider "virtualbox" do |vb|
      vb.memory = "4096"
      vb.cpus = 2
    end
    kali.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y nmap gobuster nuclei python3-pip
      pip3 install fastapi uvicorn
    SHELL
  end
  
  # Metasploitable3
  config.vm.define "metasploitable" do |meta|
    meta.vm.box = "rapid7/metasploitable3-ub1404"
    meta.vm.hostname = "metasploitable3"
    meta.vm.network "private_network", ip: "192.168.56.102"
    meta.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 1
    end
  end
  
  # DVWA
  config.vm.define "dvwa" do |dvwa|
    dvwa.vm.box = "debian/buster64"
    dvwa.vm.hostname = "dvwa"
    dvwa.vm.network "private_network", ip: "192.168.56.103"
    dvwa.vm.provider "virtualbox" do |vb|
      vb.memory = "1024"
      vb.cpus = 1
    end
    dvwa.vm.provision "shell", inline: <<-SHELL
      apt-get update
      apt-get install -y apache2 mysql-server php php-mysql php-gd
      # Download and configure DVWA
      cd /var/www/html
      wget https://github.com/digininja/DVWA/archive/master.zip
      unzip master.zip
      mv DVWA-master dvwa
      chown -R www-data:www-data dvwa
      chmod -R 755 dvwa
    SHELL
  end
end
```

### Docker Compose 配置 (docker-compose.yml)
```yaml
version: '3.8'

services:
  # Redis for message queue
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  # HexStrike Core Services
  hexstrike-core:
    build: .
    ports:
      - "8080:8080"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
  
  # Reconnaissance Server
  recon-server:
    build: .
    command: python -m servers.recon.recon_server
    ports:
      - "8081:8081"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379
      - SERVER_TYPE=recon
    volumes:
      - /usr/bin/nmap:/usr/bin/nmap:ro
      - /usr/share/nmap:/usr/share/nmap:ro
  
  # Exploit Server
  exploit-server:
    build: .
    command: python -m servers.exploit.exploit_server
    ports:
      - "8082:8082"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379
      - SERVER_TYPE=exploit
    volumes:
      - /usr/bin/nuclei:/usr/bin/nuclei:ro
      - /usr/share/nuclei:/usr/share/nuclei:ro
  
  # AI Decision Server
  ai-server:
    build: .
    command: python -m servers.ai.ai_server
    ports:
      - "8083:8083"
    depends_on:
      - redis
    environment:
      - REDIS_URL=redis://redis:6379
      - SERVER_TYPE=ai

volumes:
  redis_data:
```

---

## 验证测试脚本

### 环境连通性测试 (test_connectivity.py)
```python
#!/usr/bin/env python3
"""
测试实验环境的网络连通性和服务可用性
"""

import subprocess
import socket
import requests
import time
from typing import List, Dict, Any

def test_ping(host: str) -> bool:
    """测试主机连通性"""
    try:
        result = subprocess.run(['ping', '-c', '1', host], 
                              capture_output=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def test_port(host: str, port: int) -> bool:
    """测试端口开放性"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_http_service(url: str) -> bool:
    """测试 HTTP 服务"""
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def run_environment_tests() -> Dict[str, Any]:
    """运行完整的环境测试"""
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'connectivity': {},
        'services': {},
        'summary': {}
    }
    
    # 测试主机连通性
    hosts = {
        'kali': '192.168.56.101',
        'metasploitable': '192.168.56.102',
        'dvwa': '192.168.56.103'
    }
    
    for name, ip in hosts.items():
        results['connectivity'][name] = test_ping(ip)
    
    # 测试关键端口
    critical_ports = {
        'metasploitable_ftp': ('192.168.56.102', 21),
        'metasploitable_ssh': ('192.168.56.102', 22),
        'metasploitable_http': ('192.168.56.102', 80),
        'metasploitable_smb': ('192.168.56.102', 445),
        'dvwa_http': ('192.168.56.103', 80),
    }
    
    for name, (host, port) in critical_ports.items():
        results['services'][name] = test_port(host, port)
    
    # 测试 HTTP 服务
    http_services = {
        'metasploitable_web': 'http://192.168.56.102',
        'dvwa_web': 'http://192.168.56.103'
    }
    
    for name, url in http_services.items():
        results['services'][name] = test_http_service(url)
    
    # 计算汇总统计
    total_connectivity = sum(results['connectivity'].values())
    total_services = sum(results['services'].values())
    max_connectivity = len(results['connectivity'])
    max_services = len(results['services'])
    
    results['summary'] = {
        'connectivity_rate': total_connectivity / max_connectivity,
        'service_availability_rate': total_services / max_services,
        'overall_ready': (total_connectivity == max_connectivity and 
                         total_services == max_services)
    }
    
    return results

if __name__ == "__main__":
    print("🔍 测试实验环境...")
    results = run_environment_tests()
    
    print(f"\n📊 测试结果 ({results['timestamp']})")
    print("=" * 50)
    
    print("\n🌐 网络连通性:")
    for host, status in results['connectivity'].items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {host}")
    
    print("\n🔧 服务可用性:")
    for service, status in results['services'].items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {service}")
    
    print(f"\n📈 汇总统计:")
    summary = results['summary']
    print(f"  连通性: {summary['connectivity_rate']:.1%}")
    print(f"  服务可用性: {summary['service_availability_rate']:.1%}")
    
    if summary['overall_ready']:
        print("  🎉 环境就绪，可以开始实验！")
    else:
        print("  ⚠️  环境未完全就绪，请检查配置")
```

### 漏洞验证脚本 (verify_vulnerabilities.py)
```python
#!/usr/bin/env python3
"""
验证目标系统中的预期漏洞
"""

import requests
import socket
import subprocess
from typing import List, Dict, Any

def check_vsftpd_backdoor(host: str) -> Dict[str, Any]:
    """检查 vsftpd 2.3.4 后门漏洞"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, 21))
        
        # 发送用户名触发后门
        sock.send(b"USER lolcat:)\r\n")
        response = sock.recv(1024)
        
        if b"230" in response:
            sock.send(b"PASS any\r\n")
            response = sock.recv(1024)
            if b"230" in response:
                sock.close()
                return {
                    'vulnerability': 'vsftpd_backdoor',
                    'status': 'vulnerable',
                    'details': 'Backdoor triggered successfully'
                }
        
        sock.close()
        return {
            'vulnerability': 'vsftpd_backdoor',
            'status': 'not_vulnerable',
            'details': 'Backdoor not triggered'
        }
    except Exception as e:
        return {
            'vulnerability': 'vsftpd_backdoor',
            'status': 'error',
            'details': str(e)
        }

def check_dvwa_sqli(host: str) -> Dict[str, Any]:
    """检查 DVWA SQL 注入漏洞"""
    try:
        # 首先登录 DVWA
        session = requests.Session()
        login_url = f"http://{host}/login.php"
        
        # 获取 CSRF token
        login_page = session.get(login_url)
        csrf_token = ""
        
        # 执行 SQL 注入测试
        sqli_url = f"http://{host}/vulnerabilities/sqli/"
        payload = "1' OR '1'='1"
        
        params = {
            'id': payload,
            'Submit': 'Submit'
        }
        
        response = session.post(sqli_url, params=params)
        
        if "Surname" in response.text and len(response.text) > 1000:
            return {
                'vulnerability': 'dvwa_sqli',
                'status': 'vulnerable',
                'details': 'SQL injection successful'
            }
        else:
            return {
                'vulnerability': 'dvwa_sqli',
                'status': 'not_vulnerable',
                'details': 'SQL injection failed'
            }
    except Exception as e:
        return {
            'vulnerability': 'dvwa_sqli',
            'status': 'error',
            'details': str(e)
        }

def run_vulnerability_verification() -> Dict[str, Any]:
    """运行漏洞验证测试"""
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'vulnerabilities': {},
        'summary': {}
    }
    
    # 测试 Metasploitable3 漏洞
    metasploitable_host = "192.168.56.102"
    results['vulnerabilities']['vsftpd_backdoor'] = check_vsftpd_backdoor(metasploitable_host)
    
    # 测试 DVWA 漏洞
    dvwa_host = "192.168.56.103"
    results['vulnerabilities']['dvwa_sqli'] = check_dvwa_sqli(dvwa_host)
    
    # 计算汇总统计
    total_vulns = len(results['vulnerabilities'])
    vulnerable_count = sum(1 for v in results['vulnerabilities'].values() 
                          if v['status'] == 'vulnerable')
    
    results['summary'] = {
        'total_vulnerabilities': total_vulns,
        'vulnerable_count': vulnerable_count,
        'vulnerability_rate': vulnerable_count / total_vulns if total_vulns > 0 else 0
    }
    
    return results

if __name__ == "__main__":
    print("🔍 验证目标漏洞...")
    results = run_vulnerability_verification()
    
    print(f"\n📊 漏洞验证结果 ({results['timestamp']})")
    print("=" * 50)
    
    for vuln_name, vuln_result in results['vulnerabilities'].items():
        status_icon = {
            'vulnerable': '🚨',
            'not_vulnerable': '✅',
            'error': '❌'
        }.get(vuln_result['status'], '❓')
        
        print(f"\n{status_icon} {vuln_result['vulnerability']}")
        print(f"   状态: {vuln_result['status']}")
        print(f"   详情: {vuln_result['details']}")
    
    summary = results['summary']
    print(f"\n📈 汇总统计:")
    print(f"  总漏洞数: {summary['total_vulnerabilities']}")
    print(f"  可利用漏洞: {summary['vulnerable_count']}")
    print(f"  漏洞率: {summary['vulnerability_rate']:.1%}")
```

---

## 实验数据收集

### 预期扫描结果模板

#### Metasploitable3 扫描结果 (expected_metasploitable_results.json)
```json
{
  "target": "192.168.56.102",
  "scan_type": "comprehensive",
  "timestamp": "2024-01-01T00:00:00Z",
  "expected_findings": {
    "open_ports": [
      {"port": 21, "protocol": "tcp", "service": "ftp", "version": "vsftpd 2.3.4"},
      {"port": 22, "protocol": "tcp", "service": "ssh", "version": "OpenSSH 5.1p1"},
      {"port": 23, "protocol": "tcp", "service": "telnet"},
      {"port": 80, "protocol": "tcp", "service": "http", "version": "Apache 2.2.14"},
      {"port": 139, "protocol": "tcp", "service": "netbios-ssn"},
      {"port": 445, "protocol": "tcp", "service": "microsoft-ds", "version": "Samba 3.4.7"},
      {"port": 3306, "protocol": "tcp", "service": "mysql", "version": "MySQL 5.1.41"}
    ],
    "vulnerabilities": [
      {
        "cve": "CVE-2011-2523",
        "service": "vsftpd",
        "port": 21,
        "severity": "critical",
        "description": "vsftpd 2.3.4 backdoor vulnerability"
      },
      {
        "cve": "CVE-2008-4250",
        "service": "samba",
        "port": 445,
        "severity": "high",
        "description": "Samba remote code execution vulnerability"
      }
    ],
    "os_fingerprint": {
      "family": "Linux",
      "version": "Ubuntu 14.04",
      "confidence": 0.95
    }
  }
}
```

#### DVWA 扫描结果 (expected_dvwa_results.json)
```json
{
  "target": "192.168.56.103",
  "scan_type": "web_application",
  "timestamp": "2024-01-01T00:00:00Z",
  "expected_findings": {
    "web_applications": [
      {
        "url": "http://192.168.56.103",
        "name": "DVWA",
        "version": "1.10",
        "technology": ["PHP", "MySQL", "Apache"]
      }
    ],
    "vulnerabilities": [
      {
        "type": "sql_injection",
        "path": "/vulnerabilities/sqli/",
        "parameter": "id",
        "severity": "high",
        "description": "SQL injection vulnerability in DVWA"
      },
      {
        "type": "xss_stored",
        "path": "/vulnerabilities/xss_s/",
        "parameters": ["txtName", "txtMessage"],
        "severity": "medium",
        "description": "Stored XSS vulnerability"
      },
      {
        "type": "file_upload",
        "path": "/vulnerabilities/upload/",
        "parameter": "uploaded",
        "severity": "high",
        "description": "Arbitrary file upload vulnerability"
      }
    ],
    "directories": [
      "/admin",
      "/login",
      "/vulnerabilities",
      "/config",
      "/docs"
    ]
  }
}
```

---

## 故障排除指南

### 常见问题及解决方案

#### 1. 网络连通性问题
```bash
# 检查虚拟机网络配置
VBoxManage list vms
VBoxManage showvminfo "Kali-Linux-HexStrike"

# 重置网络适配器
VBoxManage modifyvm "Kali-Linux-HexStrike" --nic1 none
VBoxManage modifyvm "Kali-Linux-HexStrike" --nic1 hostonly
```

#### 2. 服务启动失败
```bash
# 检查端口占用
netstat -tlnp | grep :8080

# 检查服务状态
systemctl status redis
systemctl start redis

# 检查防火墙设置
sudo ufw status
sudo ufw allow 8080/tcp
```

#### 3. 工具路径问题
```bash
# 检查工具安装
which nmap
which gobuster
which nuclei

# 更新工具数据库
sudo nmap --script-updatedb
nuclei -update-templates
```

---

## 实验记录模板

### 实验日志格式
```markdown
# 实验记录 - [日期]

## 实验环境
- 主机系统: [操作系统版本]
- 虚拟化软件: [VirtualBox/VMware 版本]
- 网络配置: Host-only 192.168.56.0/24

## 虚拟机状态
- Kali Linux: [正常/异常] - IP: 192.168.56.101
- Metasploitable3: [正常/异常] - IP: 192.168.56.102
- DVWA: [正常/异常] - IP: 192.168.56.103

## 实验执行
### 串行扫描
- 开始时间: [时间戳]
- 结束时间: [时间戳]
- 总耗时: [秒数]
- 发现漏洞: [数量]

### 协同扫描
- 开始时间: [时间戳]
- 结束时间: [时间戳]
- 总耗时: [秒数]
- 发现漏洞: [数量]

## 性能对比
- 效率提升: [百分比]
- 漏洞覆盖率: [百分比]
- 资源利用率: [百分比]

## 问题记录
[记录遇到的问题和解决方案]

## 结论
[实验结论和建议]
```

---

## 总结

本实验室环境配置文档提供了完整的可重现实验环境，包括：

1. **标准化的虚拟机配置** - 确保每次实验的一致性
2. **详细的网络拓扑** - 清晰的 IP 分配和连接关系
3. **已知的漏洞配置** - 用于验证扫描效果
4. **自动化部署脚本** - 简化环境搭建过程
5. **验证测试工具** - 确保环境正确性
6. **故障排除指南** - 解决常见问题

通过遵循本指南，研究人员可以快速搭建标准化的渗透测试实验环境，确保实验结果的可重现性和可比性。
