"""
MCP Task Management Server

This is a custom MCP server that provides task management capabilities
using PostgreSQL as the backend database.

The server exposes tools for:
- Creating, reading, updating, and deleting tasks
- Managing task categories and comments
- Querying database schema information
- Executing custom SQL queries (read-only)

Resources provided:
- Task lists and individual tasks
- Database schema information
- Task statistics and summaries
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

from .database import TaskDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPTaskServer:
    """MCP server for task management with PostgreSQL backend."""
    
    def __init__(self, database_url: str):
        self.server = Server("mcp-task-server")
        self.db = TaskDatabase(database_url)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up MCP protocol handlers."""
        
        # List available tools
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """Return the list of tools available in this server."""
            return [
                types.Tool(
                    name="list_tasks",
                    description="List all tasks, optionally filtered by status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed", "cancelled"],
                                "description": "Filter tasks by status (optional)"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="get_task",
                    description="Get details of a specific task by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to retrieve"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="create_task",
                    description="Create a new task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Task title"
                            },
                            "description": {
                                "type": "string",
                                "description": "Task description (optional)"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "Task priority (default: medium)"
                            },
                            "assigned_to": {
                                "type": "string",
                                "description": "Person assigned to the task (optional)"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of tags for the task (optional)"
                            }
                        },
                        "required": ["title"]
                    }
                ),
                types.Tool(
                    name="update_task_status",
                    description="Update the status of a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to update"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed", "cancelled"],
                                "description": "New status for the task"
                            }
                        },
                        "required": ["task_id", "status"]
                    }
                ),
                types.Tool(
                    name="delete_task",
                    description="Delete a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task to delete"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="add_task_comment",
                    description="Add a comment to a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task"
                            },
                            "comment": {
                                "type": "string",
                                "description": "The comment text"
                            },
                            "author": {
                                "type": "string",
                                "description": "Comment author (optional)"
                            }
                        },
                        "required": ["task_id", "comment"]
                    }
                ),
                types.Tool(
                    name="get_task_comments",
                    description="Get all comments for a task",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "integer",
                                "description": "The ID of the task"
                            }
                        },
                        "required": ["task_id"]
                    }
                ),
                types.Tool(
                    name="list_categories",
                    description="List all available task categories",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="execute_query",
                    description="Execute a read-only SQL query on the database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL SELECT query to execute (read-only)"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="get_schema",
                    description="Get database schema information",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        # Handle tool calls
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool execution requests."""
            try:
                if name == "list_tasks":
                    return await self._handle_list_tasks(arguments)
                elif name == "get_task":
                    return await self._handle_get_task(arguments)
                elif name == "create_task":
                    return await self._handle_create_task(arguments)
                elif name == "update_task_status":
                    return await self._handle_update_task_status(arguments)
                elif name == "delete_task":
                    return await self._handle_delete_task(arguments)
                elif name == "add_task_comment":
                    return await self._handle_add_task_comment(arguments)
                elif name == "get_task_comments":
                    return await self._handle_get_task_comments(arguments)
                elif name == "list_categories":
                    return await self._handle_list_categories(arguments)
                elif name == "execute_query":
                    return await self._handle_execute_query(arguments)
                elif name == "get_schema":
                    return await self._handle_get_schema(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]
        
        # List available resources
        @self.server.list_resources()
        async def handle_list_resources() -> List[types.Resource]:
            """Return available resources."""
            return [
                types.Resource(
                    uri="task://all",
                    name="All Tasks",
                    description="Complete list of all tasks in the system",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="task://pending",
                    name="Pending Tasks",
                    description="List of tasks with pending status",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="task://in_progress",
                    name="In Progress Tasks", 
                    description="List of tasks currently in progress",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="task://completed",
                    name="Completed Tasks",
                    description="List of completed tasks",
                    mimeType="application/json"
                ),
                types.Resource(
                    uri="schema://database",
                    name="Database Schema",
                    description="Database schema information for all tables",
                    mimeType="application/json"
                )
            ]
        
        # Handle resource reads
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Handle resource read requests."""
            try:
                if uri.startswith("task://"):
                    status = uri.split("//")[1]
                    if status == "all":
                        tasks = await self.db.get_all_tasks()
                    else:
                        tasks = await self.db.get_tasks_by_status(status)
                    return json.dumps(tasks, default=str, indent=2)
                elif uri == "schema://database":
                    schema = await self.db.get_database_schema()
                    return json.dumps(schema, indent=2)
                else:
                    raise ValueError(f"Unknown resource: {uri}")
            except Exception as e:
                logger.error(f"Resource read failed: {e}")
                return f"Error reading resource: {str(e)}"
    
    # Tool handler methods
    
    async def _handle_list_tasks(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle list_tasks tool call."""
        status = arguments.get("status")
        if status:
            tasks = await self.db.get_tasks_by_status(status)
            result = f"Tasks with status '{status}':\n\n"
        else:
            tasks = await self.db.get_all_tasks()
            result = "All tasks:\n\n"
        
        if not tasks:
            result += "No tasks found."
        else:
            for task in tasks:
                result += f"ID: {task['id']}\n"
                result += f"Title: {task['title']}\n"
                result += f"Status: {task['status']}\n"
                result += f"Priority: {task['priority']}\n"
                if task['assigned_to']:
                    result += f"Assigned to: {task['assigned_to']}\n"
                if task['categories']:
                    result += f"Categories: {', '.join(task['categories'])}\n"
                result += f"Created: {task['created_at']}\n"
                result += "---\n"
        
        return [types.TextContent(type="text", text=result)]
    
    async def _handle_get_task(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get_task tool call."""
        task_id = arguments["task_id"]
        task = await self.db.get_task_by_id(task_id)
        
        if not task:
            return [types.TextContent(type="text", text=f"Task with ID {task_id} not found.")]
        
        result = f"Task Details:\n\n"
        result += f"ID: {task['id']}\n"
        result += f"Title: {task['title']}\n"
        result += f"Description: {task['description'] or 'No description'}\n"
        result += f"Status: {task['status']}\n"
        result += f"Priority: {task['priority']}\n"
        result += f"Assigned to: {task['assigned_to'] or 'Unassigned'}\n"
        result += f"Categories: {', '.join(task['categories']) if task['categories'] else 'None'}\n"
        result += f"Tags: {', '.join(task['tags']) if task['tags'] else 'None'}\n"
        result += f"Created: {task['created_at']}\n"
        result += f"Updated: {task['updated_at']}\n"
        if task['due_date']:
            result += f"Due date: {task['due_date']}\n"
        
        return [types.TextContent(type="text", text=result)]
    
    async def _handle_create_task(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle create_task tool call."""
        title = arguments["title"]
        description = arguments.get("description")
        priority = arguments.get("priority", "medium")
        assigned_to = arguments.get("assigned_to")
        tags = arguments.get("tags", [])
        
        task = await self.db.create_task(
            title=title,
            description=description,
            priority=priority,
            assigned_to=assigned_to,
            tags=tags
        )
        
        if task:
            result = f"Task created successfully!\n\n"
            result += f"ID: {task['id']}\n"
            result += f"Title: {task['title']}\n"
            result += f"Status: {task['status']}\n"
            result += f"Priority: {task['priority']}\n"
        else:
            result = "Failed to create task."
        
        return [types.TextContent(type="text", text=result)]
    
    async def _handle_update_task_status(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle update_task_status tool call."""
        task_id = arguments["task_id"]
        status = arguments["status"]
        
        success = await self.db.update_task_status(task_id, status)
        
        if success:
            result = f"Task {task_id} status updated to '{status}' successfully."
        else:
            result = f"Failed to update task {task_id} status."
        
        return [types.TextContent(type="text", text=result)]
    
    async def _handle_delete_task(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle delete_task tool call."""
        task_id = arguments["task_id"]
        
        success = await self.db.delete_task(task_id)
        
        if success:
            result = f"Task {task_id} deleted successfully."
        else:
            result = f"Failed to delete task {task_id}."
        
        return [types.TextContent(type="text", text=result)]
    
    async def _handle_add_task_comment(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle add_task_comment tool call."""
        task_id = arguments["task_id"]
        comment = arguments["comment"]
        author = arguments.get("author", "Anonymous")
        
        comment_obj = await self.db.add_task_comment(task_id, comment, author)
        
        if comment_obj:
            result = f"Comment added to task {task_id}:\n"
            result += f"Author: {comment_obj['author']}\n"
            result += f"Comment: {comment_obj['comment']}\n"
            result += f"Created: {comment_obj['created_at']}"
        else:
            result = f"Failed to add comment to task {task_id}."
        
        return [types.TextContent(type="text", text=result)]
    
    async def _handle_get_task_comments(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get_task_comments tool call."""
        task_id = arguments["task_id"]
        
        comments = await self.db.get_task_comments(task_id)
        
        if not comments:
            result = f"No comments found for task {task_id}."
        else:
            result = f"Comments for task {task_id}:\n\n"
            for comment in comments:
                result += f"Author: {comment['author']}\n"
                result += f"Date: {comment['created_at']}\n"
                result += f"Comment: {comment['comment']}\n"
                result += "---\n"
        
        return [types.TextContent(type="text", text=result)]
    
    async def _handle_list_categories(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle list_categories tool call."""
        categories = await self.db.get_all_categories()
        
        if not categories:
            result = "No categories found."
        else:
            result = "Available categories:\n\n"
            for category in categories:
                result += f"ID: {category['id']}\n"
                result += f"Name: {category['name']}\n"
                result += f"Description: {category['description'] or 'No description'}\n"
                result += f"Color: {category['color']}\n"
                result += "---\n"
        
        return [types.TextContent(type="text", text=result)]
    
    async def _handle_execute_query(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle execute_query tool call (read-only)."""
        query = arguments["query"].strip()
        
        # Security check: only allow SELECT queries
        if not query.upper().startswith("SELECT"):
            return [types.TextContent(
                type="text", 
                text="Error: Only SELECT queries are allowed for security reasons."
            )]
        
        try:
            results = await self.db.execute_query(query)
            
            if not results:
                result = "Query executed successfully. No results returned."
            else:
                result = f"Query Results ({len(results)} rows):\n\n"
                result += json.dumps(results, default=str, indent=2)
        except Exception as e:
            result = f"Query execution failed: {str(e)}"
        
        return [types.TextContent(type="text", text=result)]
    
    async def _handle_get_schema(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle get_schema tool call."""
        schema = await self.db.get_database_schema()
        
        result = "Database Schema:\n\n"
        for table_name, columns in schema.items():
            result += f"Table: {table_name}\n"
            for column in columns:
                nullable = " (nullable)" if column['nullable'] else " (not null)"
                default = f" default: {column['default']}" if column['default'] else ""
                result += f"  - {column['name']}: {column['type']}{nullable}{default}\n"
            result += "\n"
        
        return [types.TextContent(type="text", text=result)]
    
    async def start(self):
        """Start the MCP server."""
        await self.db.connect()
        logger.info("MCP Task Server started")
    
    async def stop(self):
        """Stop the MCP server."""
        await self.db.disconnect()
        logger.info("MCP Task Server stopped")
    
    async def run(self):
        """Run the MCP server with stdio transport."""
        await self.start()
        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="mcp-task-server",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=None,
                            experimental_capabilities={}
                        ),
                    ),
                )
        finally:
            await self.stop()
