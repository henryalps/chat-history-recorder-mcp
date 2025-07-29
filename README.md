<div align="center">
  <img src="logo.png" alt="Local Memory MCP Logo" width="128" height="128">
  <h1>Chat History Recorder MCP Server</h1>
  <p>An MCP (Model Context Protocol) server for automatically recording AI conversation history.</p>
  <p>
    <a href="https://smithery.ai/server/@henryalps/chat-history-recorder-mcp"><img alt="smithery badge" src="https://smithery.ai/badge/@henryalps/chat-history-recorder-mcp"></a>
  </p>
</div>

> **Common Issue**: AI conversation history is easily lost, lacking persistent recording and cross-session memory.

> **Core Value**: Automatically record every AI conversation, build a local knowledge base, and give your AI "memory".

**🎯 What Problem Does This MCP Solve?**
- **Memory Loss**: AI conversations are ephemeral and lost after sessions end.
- **Context Fragmentation**: No way to maintain conversation context across different sessions.
- **Knowledge Waste**: Valuable insights and solutions from AI interactions are not preserved.
- **Repetitive Queries**: Users have to re-explain context in new conversations.

**💡 How This MCP Helps:**
- **Persistent Memory**: Automatically saves every AI interaction to local files.
- **Cross-Session Context**: Build a searchable knowledge base of past conversations.
- **Zero-Effort Logging**: Works transparently without user intervention.
- **Flexible Storage**: Local files with optional global memory support.

[中文版 README](README_zh.md)

## Features

- 🤖 **Automatic Recording**: Automatically records conversation history after AI conversations
- 📁 **Flexible Configuration**: Configure recording format and options via `.chat_history` file
- 🌍 **Global Memory**: Optional global memory file support (`~/.my_chat_history_mcp`)
- 📝 **Standard Format**: 4-line format records (timestamp, user input, system output summary, file operations)
- 🔧 **Fallback Mechanism**: Automatically uses default configuration when config file is missing
- 📋 **Smart Summarization**: System outputs are automatically summarized for concise storage

## Installation

### Installing via Smithery

To install Chat History Local Memory Recorder for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@henryalps/chat-history-recorder-mcp):

```bash
npx -y @smithery/cli install @henryalps/chat-history-recorder-mcp --client claude
```

1. Clone or download the project locally
2. Install dependencies:

```bash
pip install -e .
```

Or using uv (recommended):

```bash
uv sync
```

## Configuration

On first run, the server will create a `.chat_history` file in the current directory that serves dual purposes:

```
# Local Memory MCP Configuration
# Format: global_memory=true/false,format=format_description
global_memory=false,format=timestamp|user_input|system_output_summary|file_operations_or_mcp_calls|llm_name

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

# === CHAT HISTORY RECORDS ===
```

### Configuration Options

- `global_memory`: Whether to enable global memory file (default: false)
- `format`: Description of conversation record format (default: 5-line format)

### File Structure

The `.chat_history` file combines configuration and history storage:
- **Configuration section**: Contains settings and documentation
- **History section**: Contains actual conversation records after the separator
- **Unix timestamps**: Used to save file space compared to ISO format

## Usage

### 1. Start the Server

Using stdio transport:
```bash
python -m src.server stdio
```

Using SSE transport:
```bash
python -m src.server sse
```

### 2. Configure in Claude Desktop

Add to Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "local-memory": {
      "command": "python",
      "args": ["-m", "src.server", "stdio"],
      "cwd": "/path/to/chat-history-recorder"
    }
  }
}
```

### 3. Automatic Conversation Recording

The server provides the following tools for AI to automatically call:

### Important Note for AI/LLM Integrators

To ensure reliable conversation history logging, it is crucial to include this execution sequence in your integration logic such as .cursorrules or .clinerules:

```markdown
# Core Execution Rule

1.  **Formulate Response**: First, formulate the complete response to the user's query.
2.  **Record History**: Immediately after formulating the response, you **MUST** call the `record_chat_history` tool to log the interaction.
3.  **Finalize Turn**: Only after the history has been recorded, you may use a concluding tool like `attempt_completion` to finalize the turn.

This sequence is mandatory and must be followed in every turn.
```

#### `record_chat_history`
This is the main tool for recording conversation history. It **MUST** be called after every AI response to log the interaction. This should happen after the AI has formulated its response but before using a concluding tool like `attempt_completion`.
```python
record_chat_history(
    user_input="User's original input",
    system_output="A summary of the AI's response and actions taken.",
    project_dir="/path/to/your/project",  # The root directory of the project
    file_operations="File modifications or MCP calls description (optional)",
    llm_name="openai gpt-4o"  # Optional LLM identifier
)
```

#### `get_config_info`
Get current configuration information:
```python
get_config_info()
```

## File Structure

```
chat-history-recorder/
├── src/
│   ├── __init__.py
│   ├── server.py          # Main MCP server file
│   ├── config.py          # Configuration and history management
│   ├── history_writer.py  # History record writing
│   └── utils.py           # Utility functions
├── pyproject.toml         # Project configuration
├── README.md              # Usage documentation
└── .chat_history          # Combined config and history file (created at runtime)
```

## Conversation Record Format

Each conversation record contains 5 lines stored after the separator in `.chat_history`:

```
1706188245
U: User asked how to create a Python script
S: Created Python script with error handling and documentation (summarized)
S: This is another line of the system output.
file_op: script.py; mcp_call: file_write
openai gpt-4o

```

The Unix timestamp format (e.g., `1706188245`) saves significant space compared to ISO format while maintaining full precision.

## Development

### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black src/
isort src/
```

### Type Checking
```bash
mypy src/
```

## License

MIT License
