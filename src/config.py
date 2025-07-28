"""Configuration management for chat history logging."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ChatHistoryConfig:
    """Configuration for chat history logging."""
    
    global_memory: bool = False
    format_description: str = "timestamp|user_input|system_output_summary|file_operations_or_mcp_calls|llm_name"
    global_memory_dir: str = "~/.my_chat_history_mcp"
    
    def to_config_line(self) -> str:
        """Convert config to file format."""
        return f"global_memory={str(self.global_memory).lower()},format={self.format_description}"
    
    @classmethod
    def from_config_line(cls, line: str) -> "ChatHistoryConfig":
        """Parse config from file line."""
        config = cls()  # Start with defaults
        
        if not line.strip() or line.strip().startswith('#'):
            return config
            
        try:
            parts = line.strip().split(',', 1)
            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'global_memory':
                        config.global_memory = value.lower() in ('true', '1', 'yes')
                    elif key == 'format':
                        config.format_description = value
        except Exception:
            # If parsing fails, return default config
            pass
            
        return config


class ConfigManager:
    """Manages the .chat_history configuration and history file."""

    def __init__(self, project_dir: Optional[str] = None):
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.config_file = self.project_dir / ".chat_history"
        self.default_config = ChatHistoryConfig()
        self.config_separator = "# === CHAT HISTORY RECORDS ==="

    def set_project_dir(self, project_dir: str):
        """Set the project directory and update the config file path."""
        self.project_dir = Path(project_dir)
        self.config_file = self.project_dir / ".chat_history"
    
    def ensure_config_exists(self) -> ChatHistoryConfig:
        """Ensure config file exists and return configuration."""
        if not self.config_file.exists():
            # Create with default configuration
            self._create_default_config()
            return self.default_config

        return self.read_config()
    
    def read_config(self) -> ChatHistoryConfig:
        """Read configuration from file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find the config line (should be the first non-comment line)
            lines = content.split('\n')
            config_line = None

            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    config_line = line
                    break

            if config_line:
                config = ChatHistoryConfig.from_config_line(config_line)
                # Apply fallback for any missing values
                return self._apply_fallback(config)
            else:
                return self.default_config

        except Exception:
            # If reading fails, return default config
            return self.default_config
    
    def _create_default_config(self) -> None:
        """Create default configuration file."""
        config_content = f"""# Local Memory MCP Configuration
# Format: global_memory=true/false,format=format_description
{self.default_config.to_config_line()}

# This file serves dual purposes:
# 1. Configuration: Lines above control how chat history is recorded
# 2. History Storage: Chat records are stored below the separator
#
# Configuration options:
# - global_memory: whether to write to global memory file (~/.my_chat_history_mcp)
# - format: description of the 5-line format for each conversation record
#   Line 1: Unix timestamp (saves space compared to ISO format)
#   Line 2: User input
#   Line 3: System output summary (brief summary instead of full output)
#   Line 4: File modifications or MCP calls summary
#   Line 5: LLM name, such as openai gpt-4o or gemini-2.5-pro

{self.config_separator}
"""

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
        except Exception as e:
            print(f"Warning: Could not create config file: {e}")
    
    def _apply_fallback(self, config: ChatHistoryConfig) -> ChatHistoryConfig:
        """Apply fallback values for missing configuration."""
        # Ensure all required fields have values
        if not config.format_description:
            config.format_description = self.default_config.format_description
        if not config.global_memory_dir:
            config.global_memory_dir = self.default_config.global_memory_dir
            
        return config
    
    def get_global_memory_path(self, config: ChatHistoryConfig) -> Optional[Path]:
        """Get the global memory file path if enabled."""
        if not config.global_memory:
            return None

        global_dir = Path(config.global_memory_dir).expanduser()
        global_dir.mkdir(parents=True, exist_ok=True)
        return global_dir / "chat_history.txt"

    def append_history_record(self, record: str) -> bool:
        """Append a history record to the .chat_history file."""
        try:
            # Ensure the file exists with proper structure
            self.ensure_config_exists()

            with open(self.config_file, 'a', encoding='utf-8') as f:
                f.write(record)
            return True
        except Exception as e:
            print(f"Error appending history record: {e}")
            return False

