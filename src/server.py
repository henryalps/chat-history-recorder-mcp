"""Local Memory MCP Server - Main server implementation."""

import asyncio
import sys
from typing import Dict, Any, Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context

try:
    from .config import ConfigManager
    from .history_writer import HistoryWriter
except ImportError:
    # For direct execution or mcp dev
    from config import ConfigManager
    from history_writer import HistoryWriter


# Create the MCP server
mcp = FastMCP("local-memory-mcp")

# Initialize components
config_manager = ConfigManager()
history_writer = HistoryWriter(config_manager)


@mcp.tool()
def record_chat_history(
    user_input: str,
    system_output: str,
    project_dir: str,
    file_operations: Optional[str] = None,
    llm_name: Optional[str] = None
) -> Dict[str, Any]:
    """**MANDATORY ACTION**: Call this after every AI response to log the interaction.

    This tool MUST be called after you have formulated your response, but BEFORE
    you use a concluding tool like `attempt_completion`. It ensures every turn
    is recorded.

    Args:
        user_input: The user's original prompt.
        system_output: A summary of the AI's response and actions taken.
        project_dir: The root directory of the current project.
        file_operations: Summary of file changes or tools used (optional).
        llm_name: Name of the LLM used (optional).
    """
    return history_writer.write_chat_history(
        user_input=user_input,
        system_output=system_output,
        project_dir=project_dir,
        file_operations=file_operations,
        llm_name=llm_name
    )


@mcp.tool()
def get_config_info() -> Dict[str, Any]:
    """Gets current configuration and file status."""
    return history_writer.get_config_info()


@mcp.resource("config://chat-history")
def get_config_resource() -> str:
    """Get the current chat history configuration as a resource."""
    config_info = history_writer.get_config_info()
    
    if not config_info["success"]:
        return f"Error reading configuration: {config_info.get('error', 'Unknown error')}"
    
    config = config_info["config"]
    files = config_info["files"]
    
    return f"""# Chat History Config
- Global Memory: {'Enabled' if config['global_memory'] else 'Disabled'}
- Format: {config['format_description']}
- Global Dir: {config['global_memory_dir']}
- History File: {files['config_and_history_file']} ({'exists' if files['config_exists'] else 'missing'})
- Global History: {files.get('global_file_path', 'N/A')} ({'exists' if files.get('global_history_exists') else 'missing/disabled'})
- Usage: Call `record_chat_history` after each turn.
"""




def main() -> None:
    """Main entry point for the MCP server."""
    if len(sys.argv) < 2:
        print("Usage: python -m src.server <transport>")
        print("Available transports: stdio, sse")
        sys.exit(1)
    
    transport = sys.argv[1]
    
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "sse":
        mcp.run(transport="sse")
    else:
        print(f"Unknown transport: {transport}")
        print("Available transports: stdio, sse")
        sys.exit(1)


if __name__ == "__main__":
    main()
