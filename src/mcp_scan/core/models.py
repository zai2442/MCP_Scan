from enum import Enum
from typing import List, Dict, Optional, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from datetime import datetime

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Vulnerability(BaseModel):
    title: str
    severity: Severity
    description: Optional[str] = None
    evidence: Optional[str] = None

class Service(BaseModel):
    port: int
    protocol: str
    service_name: str = "unknown"
    product: Optional[str] = None
    version: Optional[str] = None

class Host(BaseModel):
    ip: str
    hostname: Optional[str] = None
    os: Optional[str] = None
    services: List[Service] = Field(default_factory=list)
    vulnerabilities: List[Vulnerability] = Field(default_factory=list)

class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    tool_name: str
    params: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    dependencies: List[UUID] = Field(default_factory=list)
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class Job(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    target: str
    status: TaskStatus = TaskStatus.PENDING
    tasks: List[Task] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    assets: List[Host] = Field(default_factory=list)
