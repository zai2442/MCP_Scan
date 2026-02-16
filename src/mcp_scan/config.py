import os
import yaml
from pydantic import BaseModel, Field, ValidationError
from typing import Dict, List, Optional

class ToolConfig(BaseModel):
    path: str
    args: List[str] = Field(default_factory=list)

class ServerConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000

class MCPConfig(BaseModel):
    log_level: str = "INFO"
    tools: Dict[str, ToolConfig] = Field(default_factory=dict)
    server: ServerConfig = Field(default_factory=ServerConfig)

def load_config(config_path: str = "config.yaml") -> MCPConfig:
    """Load configuration from a YAML file."""
    if not os.path.exists(config_path):
        # Return default config if file doesn't exist
        return MCPConfig()

    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f) or {}
        return MCPConfig(**data)
    except (yaml.YAMLError, ValidationError) as e:
        raise ValueError(f"Invalid configuration file: {e}")

# Global config instance
# In a real app, this might be initialized at startup
_config_instance = None

def get_config() -> MCPConfig:
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance
