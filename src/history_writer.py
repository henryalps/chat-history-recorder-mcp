"""Chat history writing functionality."""

import os
from pathlib import Path
from typing import Optional
from datetime import datetime

try:
    from .config import ChatHistoryConfig, ConfigManager
    from .utils import format_chat_record, validate_chat_inputs, get_current_timestamp
except ImportError:
    # For direct execution or mcp dev
    from config import ChatHistoryConfig, ConfigManager
    from utils import format_chat_record, validate_chat_inputs, get_current_timestamp


class HistoryWriter:
    """Handles writing chat history to .chat_history and global files."""

    def __init__(self, config_manager: ConfigManager = None):
        self.config_manager = config_manager if config_manager else ConfigManager()
    
    def write_chat_history(
        self,
        user_input: str,
        system_output: str,
        project_dir: str,
        file_operations: Optional[str] = None,
        llm_name: Optional[str] = None
    ) -> dict:
        """Write chat history to .chat_history and optionally global files."""
        try:
            # Validate inputs
            user_input, system_output = validate_chat_inputs(user_input, system_output)

            # Get current configuration for the specified project directory
            self.config_manager.set_project_dir(project_dir)
            config = self.config_manager.ensure_config_exists()

            # Format the chat record
            timestamp = get_current_timestamp()
            record = format_chat_record(
                user_input=user_input,
                system_output=system_output,
                timestamp=timestamp,
                file_operations=file_operations,
                llm_name=llm_name
            )

            # Write to .chat_history file
            local_success = self.config_manager.append_history_record(record)

            # Write to global file if enabled
            global_success = None
            global_path = None
            if config.global_memory:
                global_path = self.config_manager.get_global_memory_path(config)
                if global_path:
                    global_success = self._write_to_global_file(record, global_path)

            return {
                "success": True,
                "timestamp": timestamp,
                "local_file": str(self.config_manager.config_file),
                "local_success": local_success,
                "global_file": str(global_path) if global_path else None,
                "global_success": global_success,
                "record_length": len(record),
                "config": {
                    "global_memory_enabled": config.global_memory,
                    "format": config.format_description
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": get_current_timestamp()
            }
    

    
    def _write_to_global_file(self, record: str, global_path: Path) -> bool:
        """Write record to global memory file."""
        try:
            # Ensure directory exists
            global_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(global_path, 'a', encoding='utf-8') as f:
                f.write(record)
            return True
        except Exception as e:
            print(f"Error writing to global file: {e}")
            return False
    
    def get_config_info(self) -> dict:
        """Get current configuration information."""
        try:
            config = self.config_manager.read_config()
            global_path = self.config_manager.get_global_memory_path(config)
            
            return {
                "success": True,
                "config": {
                    "global_memory": config.global_memory,
                    "format_description": config.format_description,
                    "global_memory_dir": config.global_memory_dir,
                    "global_file_path": str(global_path) if global_path else None
                },
                "files": {
                    "config_and_history_file": str(self.config_manager.config_file),
                    "config_exists": self.config_manager.config_file.exists(),
                    "global_history_exists": global_path.exists() if global_path else False
                },
                "reminder": "REMINDER: You MUST call `record_chat_history` after formulating your response and before using a concluding tool like `attempt_completion`."
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
