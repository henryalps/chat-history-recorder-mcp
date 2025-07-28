"""Utility functions for the local memory MCP server."""

import re
from datetime import datetime
from typing import Any, Dict, List


def get_current_timestamp() -> str:
    """Get current timestamp as Unix timestamp string."""
    return str(int(datetime.now().timestamp()))


def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def clean_text_for_logging(text: str) -> str:
    """Clean text for logging by removing excessive whitespace and newlines."""
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text.strip())
    return text


def create_system_output_summary(system_output: str, max_length: int = 150) -> str:
    """Create a brief summary of system output instead of full content."""
    # Clean the text first
    cleaned_output = clean_text_for_logging(system_output)

    # If already short enough, return as is
    if len(cleaned_output) <= max_length:
        return cleaned_output

    # Try to find a good breaking point (sentence end)
    sentences = re.split(r'[.!?]+\s+', cleaned_output)
    summary = ""

    for sentence in sentences:
        if len(summary + sentence) <= max_length - 3:  # Leave room for "..."
            summary += sentence + ". "
        else:
            break

    # If we got a good summary, return it
    if summary.strip():
        return summary.strip()

    # Otherwise, truncate at word boundary
    words = cleaned_output.split()
    summary = ""

    for word in words:
        if len(summary + word) <= max_length - 3:
            summary += word + " "
        else:
            break

    return (summary.strip() + "...") if summary.strip() else cleaned_output[:max_length-3] + "..."


def extract_file_operations(system_output: str) -> str:
    """Extract file operations and MCP calls from system output."""
    operations = []

    # Look for common file operation patterns
    file_patterns = [
        r'(?:created?|wrote|saved|modified|updated|edited)\s+(?:file\s+)?[`\'"]?([^\s`\'"]+)[`\'"]?',
        r'(?:reading|opened|loaded)\s+(?:file\s+)?[`\'"]?([^\s`\'"]+)[`\'"]?',
        r'(?:deleted|removed)\s+(?:file\s+)?[`\'"]?([^\s`\'"]+)[`\'"]?',
    ]

    for pattern in file_patterns:
        matches = re.findall(pattern, system_output, re.IGNORECASE)
        for match in matches:
            operations.append(f"file_op: {match}")

    # Look for MCP tool calls
    mcp_patterns = [
        r'(?:called?|invoked?|used?)\s+(\w+)\s*(?:tool|function)',
        r'(?:executed?|performed?)\s+(\w+)\s*(?:operation|action)',
        r'(?:调用了?|使用了?|执行了?)\s*(\w+)\s*(?:工具|功能|操作)',
    ]

    for pattern in mcp_patterns:
        matches = re.findall(pattern, system_output, re.IGNORECASE)
        for match in matches:
            operations.append(f"mcp_call: {match}")

    if not operations:
        # If no specific operations found, provide a generic summary
        if len(system_output) > 100:
            return "complex_operation"
        else:
            return "regular_response"

    return "; ".join(operations[:3])  # Limit to first 3 operations


def format_chat_record(
    user_input: str,
    system_output: str,
    timestamp: str = None,
    file_operations: str = None,
    llm_name: str = None
) -> str:
    """Format a chat record according to the 5-line format."""
    if timestamp is None:
        timestamp = get_current_timestamp()

    if file_operations is None:
        file_operations = extract_file_operations(system_output)

    if llm_name is None:
        llm_name = "unknown"

    # Clean and process inputs
    # Prefix each line for readability
    prefixed_user_input = "\n".join([f"U: {line}" for line in user_input.strip().split('\n')])
    prefixed_system_output = "\n".join([f"S: {line}" for line in system_output.strip().split('\n')])

    # Create summary instead of using full system output
    system_output_summary = create_system_output_summary(prefixed_system_output, 20000)
    clean_file_operations = clean_text_for_logging(file_operations)
    clean_llm_name = clean_text_for_logging(llm_name)

    # Truncate to reasonable lengths
    clean_file_operations = truncate_text(clean_file_operations, 200)
    clean_llm_name = truncate_text(clean_llm_name, 100)

    # Format as 5 lines
    record = f"""{timestamp}
{prefixed_user_input}
{system_output_summary}
{clean_file_operations}
{clean_llm_name}

"""

    return record


def validate_chat_inputs(user_input: Any, system_output: Any) -> tuple[str, str]:
    """Validate and convert chat inputs to strings."""
    if not isinstance(user_input, str):
        user_input = str(user_input) if user_input is not None else ""
    
    if not isinstance(system_output, str):
        system_output = str(system_output) if system_output is not None else ""
    
    if not user_input.strip():
        raise ValueError("User input cannot be empty")
    
    if not system_output.strip():
        raise ValueError("System output cannot be empty")
    
    return user_input.strip(), system_output.strip()
