import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from pydantic import AnyUrl
import mcp.types as types

# In-memory tracking for file changes
file_timestamps = {}

server = Server("code-index")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available filesystem tools"""
    return [
        Tool(
            name="search_files",
            description="Search for files by name/pattern in a codebase or project directory. Use this for finding Programming language file such as Python files, config files, or any file by name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Root directory to search from"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Filename pattern (supports wildcards: *.py, test_*.js)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 50
                    }
                },
                "required": ["directory", "pattern"]
            }
        ),
        Tool(
            name="search_content",
            description="Search for text content within files (grep-like). Use this for finding specific code snippets, comments, or configuration settings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Root directory to search in"
                    },
                    "search_term": {
                        "type": "string",
                        "description": "Text or regex pattern to search for"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Only search files matching this pattern (e.g., *.py)",
                        "default": "*"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether search should be case-sensitive",
                        "default": False
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of matching files to return",
                        "default": 20
                    }
                },
                "required": ["directory", "search_term"]
            }
        ),
        Tool(
            name="read_file",
            description="Read the complete contents of a file. Use this for viewing the content of code files, configuration files, or any text-based file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Full path to the file to read"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="list_directory",
            description="List all files and subdirectories in a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path to list"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to list recursively",
                        "default": False
                    }
                },
                "required": ["directory"]
            }
        ),
        Tool(
            name="get_file_changes",
            description="Get list of files that have been modified since last check",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to check for changes"
                    }
                },
                "required": ["directory"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool execution"""

    if name == "search_files":
        return await search_files(
            arguments["directory"],
            arguments["pattern"],
            arguments.get("max_results", 50)
        )

    elif name == "search_content":
        return await search_content(
            arguments["directory"],
            arguments["search_term"],
            arguments.get("file_pattern", "*"),
            arguments.get("case_sensitive", False),
            arguments.get("max_results", 20)
        )

    elif name == "read_file":
        return await read_file(arguments["file_path"])

    elif name == "list_directory":
        return await list_directory(
            arguments["directory"],
            arguments.get("recursive", False)
        )

    elif name == "get_file_changes":
        return await get_file_changes(arguments["directory"])

    else:
        raise ValueError(f"Unknown tool: {name}")

# Tool implementations
async def search_files(directory: str, pattern: str, max_results: int) -> list[TextContent]:
    """Search for files matching a pattern"""
    try:
        dir_path = Path(directory).expanduser().resolve()
        if not dir_path.exists():
            return [TextContent(type="text", text=f"Directory not found: {directory}")]

        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace(".", r"\.").replace("*", ".*").replace("?", ".")
        regex = re.compile(regex_pattern, re.IGNORECASE)

        results = []
        for root, dirs, files in os.walk(dir_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]

            for file in files:
                if regex.search(file):
                    full_path = Path(root) / file
                    results.append(str(full_path))
                    if len(results) >= max_results:
                        break
            if len(results) >= max_results:
                break

        if not results:
            return [TextContent(type="text", text=f"No files found matching pattern: {pattern}")]

        return [TextContent(
            type="text",
            text=f"Found {len(results)} file(s):\n" + "\n".join(results)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"Error searching files: {str(e)}")]


async def search_content(directory: str, search_term: str, file_pattern: str, 
                        case_sensitive: bool, max_results: int) -> list[TextContent]:
    """Search for content within files"""
    try:
        dir_path = Path(directory).expanduser().resolve()
        if not dir_path.exists():
            return [TextContent(type="text", text=f"Directory not found: {directory}")]

        # Compile search regex
        flags = 0 if case_sensitive else re.IGNORECASE
        search_regex = re.compile(search_term, flags)

        # Convert file pattern to regex
        file_regex_pattern = file_pattern.replace(".", r"\.").replace("*", ".*").replace("?", ".")
        file_regex = re.compile(file_regex_pattern, re.IGNORECASE)

        matches = []
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]

            for file in files:
                if not file_regex.search(file):
                    continue
                
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if search_regex.search(content):
                            # Find matching lines
                            lines = content.split('\n')
                            matching_lines = [
                                f"  Line {i+1}: {line.strip()}" 
                                for i, line in enumerate(lines) 
                                if search_regex.search(line)
                            ][:5]  # Limit to 5 lines per file
                            
                            matches.append(f"{file_path}:\n" + "\n".join(matching_lines))
                            
                            if len(matches) >= max_results:
                                break
                except:
                    continue  # Skip binary files or files with encoding issues
            
            if len(matches) >= max_results:
                break

        if not matches:
            return [TextContent(type="text", text=f"No matches found for: {search_term}")]

        return [TextContent(
            type="text",
            text=f"Found matches in {len(matches)} file(s):\n\n" + "\n\n".join(matches)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"Error searching content: {str(e)}")]


async def read_file(file_path: str) -> list[TextContent]:
    """Read complete file contents"""
    try:
        path = Path(file_path).expanduser().resolve()
        if not path.exists():
            return [TextContent(type="text", text=f"File not found: {file_path}")]

        if not path.is_file():
            return [TextContent(type="text", text=f"Not a file: {file_path}")]

        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        return [TextContent(
            type="text",
            text=f"File: {file_path}\n{'='*50}\n{content}"
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"Error reading file: {str(e)}")]


async def list_directory(directory: str, recursive: bool) -> list[TextContent]:
    """List directory contents"""
    try:
        dir_path = Path(directory).expanduser().resolve()
        if not dir_path.exists():
            return [TextContent(type="text", text=f"Directory not found: {directory}")]

        items = []

        if recursive:
            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
                level = root.replace(str(dir_path), '').count(os.sep)
                indent = '  ' * level
                items.append(f"{indent}{Path(root).name}/")
                sub_indent = '  ' * (level + 1)
                for file in files:
                    items.append(f"{sub_indent}{file}")
        else:
            for item in sorted(dir_path.iterdir()):
                if item.name.startswith('.'):
                    continue
                marker = "/" if item.is_dir() else ""
                items.append(f"{item.name}{marker}")

        return [TextContent(
            type="text",
            text=f"Contents of {directory}:\n" + "\n".join(items)
        )]

    except Exception as e:
        return [TextContent(type="text", text=f"Error listing directory: {str(e)}")]


async def get_file_changes(directory: str) -> list[TextContent]:
    """Track file modifications since last check"""
    try:
        dir_path = Path(directory).expanduser().resolve()
        if not dir_path.exists():
            return [TextContent(type="text", text=f"Directory not found: {directory}")]
        
        current_files = {}
        changes = {
            'new': [],
            'modified': [],
            'deleted': []
        }

        # Scan current state
        for root, dirs, files in os.walk(dir_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
            
            for file in files:
                file_path = str(Path(root) / file)
                try:
                    mtime = os.path.getmtime(file_path)
                    current_files[file_path] = mtime
                    
                    # Check if file is new or modified
                    if file_path not in file_timestamps:
                        changes['new'].append(file_path)
                    elif file_timestamps[file_path] < mtime:
                        changes['modified'].append(file_path)
                except:
                    continue

        # Check for deleted files
        for old_file in file_timestamps:
            if old_file.startswith(str(dir_path)) and old_file not in current_files:
                changes['deleted'].append(old_file)

        # Update tracking
        file_timestamps.update(current_files)

        # Format response
        result_parts = []
        if changes['new']:
            result_parts.append(f"New files ({len(changes['new'])}):\n" + "\n".join(f"  + {f}" for f in changes['new']))
        if changes['modified']:
            result_parts.append(f"Modified files ({len(changes['modified'])}):\n" + "\n".join(f"  ~ {f}" for f in changes['modified']))
        if changes['deleted']:
            result_parts.append(f"Deleted files ({len(changes['deleted'])}):\n" + "\n".join(f"  - {f}" for f in changes['deleted']))
        
        if not result_parts:
            return [TextContent(type="text", text="No changes detected")]

        return [TextContent(type="text", text="\n\n".join(result_parts))]

    except Exception as e:
        return [TextContent(type="text", text=f"Error tracking changes: {str(e)}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="code-index",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
