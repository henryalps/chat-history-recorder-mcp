<div align="center">
  <img src="logo.png" alt="本地内存 MCP 标志" width="128" height="128">
  <h1>对话历史记录 MCP 服务器</h1>
  <p>一个用于自动记录 AI 对话历史的 MCP (模型上下文协议) 服务器。</p>
  <p>
    <a href="https://github.com/psf/black"><img alt="代码风格: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
  </p>
</div>

> **常见问题**: AI 对话历史容易丢失，缺乏持久化记录和跨会话记忆。

> **核心价值**: 自动记录每一次 AI 对话，建立本地知识库，赋予你的 AI “记忆”。

**🎯 这解决了什么问题？**
- **记忆丢失**: AI 对话是短暂的，会话结束后即丢失。
- **上下文碎片化**: 无法在不同会话间保持对话上下文。
- **知识浪费**: AI 互动中宝贵的见解和解决方案未能保存。
- **重复查询**: 用户不得不在新的对话中重新解释上下文。

**💡 这个 MCP 如何提供帮助:**
- **持久化记忆**: 自动将每一次 AI 互动保存到本地文件。
- **跨会话上下文**: 建立一个可搜索的过往对话知识库。
- **零操作记录**: 在用户无干预的情况下透明工作。
- **灵活存储**: 本地文件，并可选支持全局内存。

## 功能特性

- 🤖 **自动记录**: 在 AI 对话后自动记录对话历史。
- 📁 **灵活配置**: 通过 `.chat_history` 文件配置记录格式和选项。
- 🌍 **全局内存**: 可选的全局内存文件支持 (`~/.my_chat_history_mcp`)。
- 📝 **标准格式**: 4行格式的记录 (时间戳, 用户输入, 系统输出摘要, 文件操作)。
- 🔧 **回退机制**: 在配置文件丢失时自动使用默认配置。
- 📋 **智能摘要**: 系统输出被自动摘要以实现简洁存储。

## 安装

1.  在本地克隆或下载项目。
2.  安装依赖：

    ```bash
    pip install -e .
    ```

    或者使用 uv (推荐):

    ```bash
    uv sync
    ```

## 配置

首次运行时，服务器将在当前目录创建一个 `.chat_history` 文件，该文件具有双重用途：

```
# 本地内存 MCP 配置
# 格式: global_memory=true/false,format=format_description
global_memory=false,format=timestamp|user_input|system_output_summary|file_operations_or_mcp_calls|llm_name

# 此文件具有双重用途:
# 1. 配置: 上面的行控制对话历史的记录方式
# 2. 历史存储: 对话记录存储在分隔符下方
#
# 配置选项:
# - global_memory: 是否写入全局内存文件 (~/.my_chat_history_mcp)
# - format: 每个对话记录的5行格式描述
#   第1行: Unix 时间戳 (与 ISO 格式相比节省空间)
#   第2行: 用户输入
#   第3行: 系统输出摘要 (简短摘要而非完整输出)
#   第4行: 文件修改或 MCP 调用摘要
#   第5行: LLM 名称，例如 openai gpt-4o 或 gemini-2.5-pro

# === CHAT HISTORY RECORDS ===
```

### 配置选项

-   `global_memory`: 是否启用全局内存文件 (默认: false)。
-   `format`: 对话记录格式的描述 (默认: 5行格式)。

### 文件结构

`.chat_history` 文件结合了配置和历史存储：

-   **配置部分**: 包含设置和文档。
-   **历史部分**: 在分隔符后包含实际的对话记录。
-   **Unix 时间戳**: 用于节省文件空间，与 ISO 格式相比。

## 使用方法

### 1. 启动服务器

使用 stdio 传输:

```bash
python -m src.server stdio
```

使用 SSE 传输:

```bash
python -m src.server sse
```

### 2. 在 Claude Desktop 中配置

添加到 Claude Desktop 配置文件:

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

### 3. 自动对话记录

服务器提供以下工具供 AI 自动调用：

### AI/LLM 集成商重要提示

为确保可靠的对话历史记录，请在您的.cursorules 或.clinerules 中包含以下提示词：

```markdown
# Core Execution Rule

1.  **Formulate Response**: First, formulate the complete response to the user's query.
2.  **Record History**: Immediately after formulating the response, you **MUST** call the `record_chat_history` tool to log the interaction.
3.  **Finalize Turn**: Only after the history has been recorded, you may use a concluding tool like `attempt_completion` to finalize the turn.

This sequence is mandatory and must be followed in every turn.
```

#### `record_chat_history`

这是记录对话历史的主要工具。**必须**在每次 AI 响应后调用以记录交互。这应该在 AI 制定其响应之后，但在使用像 `attempt_completion` 这样的结束工具之前发生。

```python
record_chat_history(
    user_input="用户的原始输入",
    system_output="AI 响应和已执行操作的摘要。",
    project_dir="/path/to/your/project",  # 项目的根目录
    file_operations="文件修改或 MCP 调用描述 (可选)",
    llm_name="openai gpt-4o"  # 可选的 LLM 标识符
)
```

#### `get_config_info`

获取当前配置信息：

```python
get_config_info()
```

## 文件结构

```
chat-history-recorder/
├── src/
│   ├── __init__.py
│   ├── server.py          # 主 MCP 服务器文件
│   ├── config.py          # 配置和历史管理
│   ├── history_writer.py  # 历史记录写入
│   └── utils.py           # 实用功能
├── pyproject.toml         # 项目配置
├── README.md              # 使用文档
└── .chat_history          # 组合的配置和历史文件 (在运行时创建)
```

## 对话记录格式

每个对话记录在 `.chat_history` 的分隔符后包含5行：

```
1706188245
U: 用户询问如何创建 Python 脚本
S: 创建了带有错误处理和文档的 Python 脚本 (摘要)
S: 这是系统输出的另一行。
file_op: script.py; mcp_call: file_write
openai gpt-4o
```

Unix 时间戳格式 (例如, `1706188245`) 与 ISO 格式相比节省了大量空间，同时保持了完全的精度。

## 开发

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black src/
isort src/
```

### 类型检查

```bash
mypy src/
```

## 许可证

MIT 许可证