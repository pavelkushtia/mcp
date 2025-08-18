# Building a Custom MCP Server: Complete Guide

This comprehensive tutorial walks you through building a Model Context Protocol (MCP) server from scratch. By the end, you'll understand how MCP works internally and be able to build your own custom servers that seamlessly integrate with AI assistants.

## 🎯 Learning Objectives

- Master MCP architecture, protocol, and communication patterns
- Build a production-ready MCP server with PostgreSQL backend
- Understand the differences between MCP servers and traditional API servers
- Learn MCP tools, resources, and advanced features
- Test, debug, and deploy MCP servers for AI assistants
- Implement security, performance optimization, and monitoring

## 📚 Part 1: Understanding MCP Architecture

### What is MCP?
MCP (Model Context Protocol) is a **standardized communication protocol** that enables AI assistants to securely connect to external data sources and tools. Think of it as a **universal translator** that allows AI models to interact with your custom business logic, databases, APIs, and services without needing to understand the specifics of each system.

### MCP vs Traditional API Servers

| **Aspect** | **Traditional HTTP/API Server** | **MCP Server** |
|------------|------------------------------|----------------|
| **Discovery** | Manual API documentation | Automatic tool/resource discovery |
| **Schema** | OpenAPI/Swagger docs | Built-in JSON schema validation |
| **Communication** | HTTP requests/responses | JSON-RPC over stdin/stdout |
| **Integration** | Custom client development | Native AI assistant integration |
| **Error Handling** | HTTP status codes | Structured protocol-level errors |
| **Authentication** | API keys, OAuth, JWT | Process-level security |
| **Data Types** | Generic JSON | Rich MCP types (Tools, Resources) |
| **Real-time** | WebSockets/SSE | Protocol-native streaming |

### Complete MCP Architecture

```mermaid
graph TB
    subgraph "AI Assistant Environment"
        A["Claude Desktop / AI Assistant"]
        B["MCP Client (Built-in)"]
        C["User Interface"]
    end
    
    subgraph "Configuration Layer"
        D["claude_config.json<br/>Server Registration"]
        E["Environment Variables<br/>DATABASE_URL, etc."]
    end
    
    subgraph "MCP Server Process"
        F["main.py<br/>Entry Point & Startup"]
        G["MCPTaskServer<br/>Protocol Handler"]
        H["Tools Registry<br/>Function Definitions"]
        I["Resources Registry<br/>Data Endpoints"]
        J["Database Layer<br/>Business Logic"]
    end
    
    subgraph "Protocol Communication"
        K["JSON-RPC over stdio<br/>Request/Response Cycle"]
        L["Tool Discovery<br/>list_tools()"]
        M["Tool Execution<br/>call_tool()"]
        N["Resource Access<br/>read_resource()"]
    end
    
    subgraph "Data Storage"
        O[("PostgreSQL Database<br/>Tasks, Categories, Comments")]
    end
    
    C --> A
    A --> B
    B --> D
    D --> K
    K --> F
    F --> G
    G --> H
    G --> I
    G --> J
    J --> O
    
    B --> L
    B --> M
    B --> N
    
    style A fill:#e1f5fe
    style B fill:#e8f5e8
    style G fill:#f3e5f5
    style H fill:#fce4ec
    style I fill:#e0f2f1
    style O fill:#e3f2fd
```

**Plain English Explanation:**
1. **User** interacts with Claude Desktop (or any MCP-compatible AI assistant)
2. **Claude** has a built-in MCP client that reads your `claude_config.json` file
3. **Configuration file** tells Claude how to start your MCP server process
4. **Your MCP server** runs as a separate Python process, communicating via stdin/stdout
5. **Protocol communication** happens through JSON-RPC messages for tool discovery and execution
6. **Your server** connects to PostgreSQL and executes business logic
7. **Results** flow back through the same channel to the user

### MCP Protocol Deep Dive

MCP defines three core concepts:

#### 1. **Tools** - Actions the AI Can Perform
Tools are like **function definitions** that tell the AI what operations it can perform:

   ```json
   {
     "name": "create_task",
  "description": "Create a new task in the system",
     "inputSchema": {
       "type": "object",
       "properties": {
      "title": {"type": "string", "description": "Task title"},
      "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"]}
    },
    "required": ["title"]
     }
   }
   ```

#### 2. **Resources** - Data the AI Can Read
Resources are like **data endpoints** that provide structured information:

   ```json
   {
     "uri": "task://all",
     "name": "All Tasks",
  "description": "Complete list of all tasks in the system",
     "mimeType": "application/json"
   }
   ```

#### 3. **Communication Protocol** - JSON-RPC Messages
All communication happens through standardized JSON-RPC messages:

   ```json
// Tool execution request
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/call",
     "params": {
       "name": "create_task",
    "arguments": {"title": "Buy groceries", "priority": "high"}
  }
}

// Tool execution response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Task created successfully! ID: 123, Title: Buy groceries"
      }
    ]
     }
   }
   ```

### The Magic of Simple Configuration

Here's how a simple config file enables Claude to call your functions:

```json
{
  "mcpServers": {
    "mcp-task-server": {
      "command": "python",
      "args": ["/home/user/mcp/main.py"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/tasks"
      }
    }
  }
}
```

**What happens behind the scenes:**
1. Claude reads this config and spawns a new Python process
2. Your process starts and implements the MCP protocol
3. Claude sends a "list_tools" request to discover capabilities
4. Your server responds with available tools and their schemas
5. Claude makes these tools available in its interface
6. When user requests an action, Claude calls the appropriate tool
7. Your server executes the function and returns results

## 🏗️ Part 2: Building the Database Layer

The database layer is the foundation of your MCP server. Unlike traditional web APIs that might use simple database connections, MCP servers need to be highly efficient since they're long-running processes that handle multiple concurrent requests from AI assistants.

### Database Architecture Design

```mermaid
graph TB
    subgraph "MCP Server Process"
        A["MCPTaskServer<br/>Main Server Class"]
        B["TaskDatabase<br/>Database Abstraction"]
        C["Connection Pool<br/>2-10 connections"]
    end
    
    subgraph "Database Operations"
        D["Query Methods<br/>get_all_tasks(), create_task()"]
        E["Command Methods<br/>update_task_status(), delete_task()"]
        F["Schema Introspection<br/>get_database_schema()"]
    end
    
    subgraph "PostgreSQL Database"
        G[("tasks table<br/>Core task data")]
        H[("categories table<br/>Task categorization")]
        I[("task_comments table<br/>Task discussions")]
        J[("task_categories table<br/>Many-to-many relationship")]
    end
    
    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    C --> G
    C --> H
    C --> I
    C --> J
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style G fill:#fff3e0
    style H fill:#fff3e0
    style I fill:#fff3e0
    style J fill:#fff3e0
```

**Plain English Explanation:**
1. **MCPTaskServer** manages the overall server and protocol handling
2. **TaskDatabase** provides a clean interface to all database operations
3. **Connection Pool** maintains efficient connections to PostgreSQL
4. **Query/Command Methods** handle different types of database operations
5. **PostgreSQL tables** store the actual task management data

### Step 1: Complete Database Schema Design

```sql
-- Core entities for comprehensive task management
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending' 
        CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    priority VARCHAR(10) DEFAULT 'medium' 
        CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    assigned_to VARCHAR(100),
    due_date TIMESTAMP WITH TIME ZONE,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#3498db' -- Hex color codes
);

CREATE TABLE task_categories (
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, category_id)
);

CREATE TABLE task_comments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    author VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_task_comments_task_id ON task_comments(task_id);

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at 
    BEFORE UPDATE ON tasks
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
```

### Step 2: Advanced Database Abstraction Layer

```python
import asyncio
import asyncpg
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

class TaskDatabase:
    """
    Advanced PostgreSQL database interface optimized for MCP servers.
    
    Features:
    - Connection pooling for efficiency
    - Async/await for non-blocking operations
    - Parameterized queries for security
    - Rich error handling and logging
    - Schema introspection for MCP resources
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
        self.logger = logging.getLogger(__name__)
    
    async def connect(self):
        """Establish optimized connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,        # Minimum connections
                max_size=10,       # Maximum connections
                command_timeout=60, # Query timeout
                server_settings={
                    'jit': 'off',  # Disable JIT for predictable performance
                    'application_name': 'mcp-task-server'
                }
            )
            self.logger.info("Database connection pool established")
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute SELECT queries with automatic connection management."""
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            try:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
            except Exception as e:
                self.logger.error(f"Query failed: {query[:100]}... | Error: {e}")
                raise
    
    async def execute_command(self, command: str, *args) -> str:
        """Execute INSERT/UPDATE/DELETE commands."""
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            try:
                result = await conn.execute(command, *args)
                self.logger.debug(f"Command executed: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Command failed: {command[:100]}... | Error: {e}")
                raise
```

### Key Database Design Principles for MCP

#### **1. Async/Await Architecture**
- **Non-blocking operations** - Essential for MCP servers that handle concurrent AI requests
- **Connection pooling** - Efficient resource management for long-running processes
- **Proper connection lifecycle** - Clean startup and shutdown

#### **2. Security-First Approach**
- **Parameterized queries** - Prevents SQL injection attacks
- **Input validation** - Validates data before database operations
- **Read-only query tools** - Separate permissions for different operation types

#### **3. Performance Optimization**
- **Strategic indexing** - Fast lookups on commonly queried fields
- **Connection pooling** - Reuse database connections efficiently
- **Query optimization** - Efficient JOINs and aggregations

#### **4. MCP-Specific Features**
- **Schema introspection** - Automatically expose database structure as MCP resources
- **Rich data types** - Support for arrays, JSON, and complex relationships
- **Structured error handling** - Meaningful error messages for AI assistants

## 🔧 Part 3: Implementing the MCP Server Core

This is where the MCP magic happens! The MCP server implementation is fundamentally different from traditional web servers - instead of handling HTTP requests, it implements a sophisticated protocol for AI assistant communication.

### MCP Server Communication Flow

```mermaid
sequenceDiagram
    participant Claude as Claude Desktop
    participant Client as MCP Client
    participant Server as MCP Server
    participant DB as PostgreSQL
    
    Note over Claude, DB: Server Startup & Discovery
    Claude->>Client: Start MCP Server
    Client->>Server: spawn python main.py
    Server->>DB: connect()
    Server-->>Client: Ready
    
    Note over Claude, DB: Tool Discovery
    Claude->>Client: What tools are available?
    Client->>Server: list_tools()
    Server-->>Client: [create_task, list_tasks, ...]
    Client-->>Claude: Available tools with schemas
    
    Note over Claude, DB: User Interaction
    Claude->>Client: User wants to create task
    Client->>Server: call_tool("create_task", {...})
    Server->>DB: INSERT INTO tasks(...)
    DB-->>Server: Task created (ID: 123)
    Server-->>Client: TextContent("Task created!")
    Client-->>Claude: Success response
    
    Note over Claude, DB: Resource Access
    Claude->>Client: Show me all tasks
    Client->>Server: read_resource("task://all")
    Server->>DB: SELECT * FROM tasks
    DB-->>Server: Task data
    Server-->>Client: JSON task list
    Client-->>Claude: Formatted task display
```

**Plain English Explanation:**
1. **Startup**: Claude spawns your Python process based on config
2. **Discovery**: Claude asks what tools your server provides
3. **Schema Exchange**: Your server describes each tool's input requirements
4. **User Interaction**: User requests an action through Claude
5. **Function Execution**: Claude calls your tool with validated arguments
6. **Database Operations**: Your server executes business logic
7. **Response**: Results flow back to the user through Claude

### Step 1: Advanced Server Architecture

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.server.models import InitializationOptions
import mcp.types as types
import asyncio
import logging
from typing import List, Dict, Any, Optional

class MCPTaskServer:
    """
    Production-ready MCP server for task management.
    
    This server demonstrates:
    - Complete MCP protocol implementation
    - Advanced tool definitions with validation
    - Resource management for data access
    - Error handling and logging
    - Database integration patterns
    """
    
    def __init__(self, database_url: str):
        # Initialize core components
        self.server = Server("mcp-task-server")
        self.db = TaskDatabase(database_url)
        self.logger = logging.getLogger(__name__)
        
        # Set up MCP protocol handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """
        Configure all MCP protocol handlers.
        
        This method registers handlers for:
        - Tool discovery and execution
        - Resource listing and reading
        - Error handling and validation
        """
        self._setup_tool_handlers()
        self._setup_resource_handlers()
        self._setup_error_handlers()
```

### Step 2: Comprehensive Tool System

Tools are the **heart of MCP** - they define what actions the AI can perform. Here's how to create robust, production-ready tools:

```python
def _setup_tool_handlers(self):
    """Register all tool-related handlers."""
    
@self.server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
        """
        Return the complete list of available tools.
        
        This is called once during MCP handshake to establish
        what capabilities this server provides.
        """
    return [
            # CRUD Operations
        types.Tool(
            name="create_task",
                description="Create a new task with optional metadata",
            inputSchema={
                "type": "object",
                "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (required)",
                            "minLength": 1,
                            "maxLength": 255
                        },
                        "description": {
                            "type": "string",
                            "description": "Detailed task description",
                            "maxLength": 1000
                        },
                    "priority": {
                        "type": "string", 
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Task priority level",
                            "default": "medium"
                        },
                        "assigned_to": {
                            "type": "string",
                            "description": "Person assigned to this task",
                            "maxLength": 100
                        },
                        "due_date": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Due date in ISO format"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of tags for categorization",
                            "maxItems": 10
                        }
                    },
                    "required": ["title"],
                    "additionalProperties": False
                }
            ),
            
            types.Tool(
                name="list_tasks",
                description="List tasks with optional filtering and sorting",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "cancelled"],
                            "description": "Filter by task status"
                        },
                        "assigned_to": {
                            "type": "string",
                            "description": "Filter by assignee"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Filter by priority"
                        },
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 20,
                            "description": "Maximum number of tasks to return"
                        }
                    },
                    "additionalProperties": False
                }
            ),
            
            # Advanced Operations
            types.Tool(
                name="execute_query",
                description="Execute read-only SQL queries for advanced data analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SELECT query to execute (read-only for security)",
                            "pattern": "^\\s*SELECT\\s+.*",
                            "maxLength": 1000
                        }
                    },
                    "required": ["query"],
                    "additionalProperties": False
                }
            )
        ]
    
@self.server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """
        Execute tool calls with comprehensive error handling.
        
        This is the main entry point for all tool executions.
        It routes to specific handlers and ensures consistent
        error handling and response formatting.
        """
        try:
            self.logger.info(f"Tool called: {name} with args: {arguments}")
            
            # Route to specific tool handlers
    if name == "create_task":
                return await self._handle_create_task(arguments)
            elif name == "list_tasks":
                return await self._handle_list_tasks(arguments)
            elif name == "execute_query":
                return await self._handle_execute_query(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
                
        except ValueError as e:
            # Validation errors
            self.logger.warning(f"Validation error in {name}: {e}")
            return [types.TextContent(
                type="text", 
                text=f"Input validation error: {str(e)}"
            )]
        except Exception as e:
            # Unexpected errors
            self.logger.error(f"Tool execution failed for {name}: {e}")
            return [types.TextContent(
                type="text", 
                text=f"Tool execution failed: {str(e)}"
            )]
```

### Step 3: Advanced Tool Implementation

```python
async def _handle_create_task(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """
    Handle task creation with full validation and error handling.
    
    This demonstrates best practices for MCP tool implementation:
    - Input validation and sanitization
    - Database error handling
    - Rich response formatting
    - Proper logging
    """
    
    # Extract and validate inputs
    title = arguments["title"].strip()
    description = arguments.get("description", "").strip() or None
        priority = arguments.get("priority", "medium")
    assigned_to = arguments.get("assigned_to", "").strip() or None
    tags = arguments.get("tags", [])
    
    # Additional validation
    if not title:
        raise ValueError("Task title cannot be empty")
    
    if len(tags) > 10:
        raise ValueError("Maximum 10 tags allowed")
    
    # Create task in database
    task = await self.db.create_task(
        title=title,
        description=description,
        priority=priority,
        assigned_to=assigned_to,
        tags=tags
    )
    
    if not task:
        raise RuntimeError("Failed to create task in database")
    
    # Format success response
    result = f"✅ Task created successfully!\n\n"
    result += f"**ID:** {task['id']}\n"
    result += f"**Title:** {task['title']}\n"
    result += f"**Status:** {task['status']}\n"
    result += f"**Priority:** {task['priority']}\n"
    
    if task['assigned_to']:
        result += f"**Assigned to:** {task['assigned_to']}\n"
    
    if task['tags']:
        result += f"**Tags:** {', '.join(task['tags'])}\n"
    
    result += f"**Created:** {task['created_at']}\n"
    
    self.logger.info(f"Task created successfully: ID {task['id']}")
    
        return [types.TextContent(type="text", text=result)]
```

### Step 4: Resource System Implementation

Resources provide **data access** capabilities - they're like API endpoints that the AI can read:

```python
def _setup_resource_handlers(self):
    """Register all resource-related handlers."""
    
@self.server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
        """
        Define all available resources.
        
        Resources are data endpoints that Claude can read
        to understand your system's current state.
        """
    return [
            # Task collections
        types.Resource(
            uri="task://all",
            name="All Tasks",
                description="Complete list of all tasks in the system",
                mimeType="application/json"
            ),
            types.Resource(
                uri="task://pending",
                name="Pending Tasks",
                description="Tasks that haven't been started yet",
                mimeType="application/json"
            ),
            types.Resource(
                uri="task://active",
                name="Active Tasks",
                description="Tasks currently in progress",
                mimeType="application/json"
            ),
            
            # System metadata
            types.Resource(
                uri="schema://database",
                name="Database Schema",
                description="Complete database schema information",
                mimeType="application/json"
            ),
            types.Resource(
                uri="stats://summary",
                name="Task Statistics",
                description="Summary statistics about tasks",
            mimeType="application/json"
        )
    ]

@self.server.read_resource()
async def handle_read_resource(uri: str) -> str:
        """
        Handle resource read requests.
        
        This method routes URI requests to appropriate
        data sources and returns formatted responses.
        """
        try:
            self.logger.debug(f"Reading resource: {uri}")
            
            if uri.startswith("task://"):
                return await self._read_task_resource(uri)
            elif uri.startswith("schema://"):
                return await self._read_schema_resource(uri)
            elif uri.startswith("stats://"):
                return await self._read_stats_resource(uri)
            else:
                raise ValueError(f"Unknown resource URI: {uri}")
                
        except Exception as e:
            self.logger.error(f"Resource read failed for {uri}: {e}")
            return f"Error reading resource: {str(e)}"
    
    async def _read_task_resource(self, uri: str) -> str:
        """Handle task-related resource requests."""
        resource_type = uri.split("//")[1]
        
        if resource_type == "all":
        tasks = await self.db.get_all_tasks()
        elif resource_type == "pending":
            tasks = await self.db.get_tasks_by_status("pending")
        elif resource_type == "active":
            tasks = await self.db.get_tasks_by_status("in_progress")
        else:
            raise ValueError(f"Unknown task resource: {resource_type}")
        
        return json.dumps({
            "resource_type": resource_type,
            "count": len(tasks),
            "tasks": tasks
        }, default=str, indent=2)
```

### Key MCP Server Design Principles

#### **1. Protocol-First Architecture**
- **Declarative tool definitions** - Tools are defined by their schemas, not implementation
- **Type safety** - JSON schemas ensure valid inputs
- **Self-documenting** - Tools include descriptions and examples

#### **2. Async/Await Throughout**
- **Non-blocking operations** - Essential for handling multiple AI requests
- **Proper error propagation** - Errors bubble up correctly through async chains
- **Resource cleanup** - Proper connection and resource management

#### **3. Rich Error Handling**
- **Validation errors** - Clear messages for invalid inputs
- **System errors** - Graceful handling of database/network issues
- **Structured responses** - Consistent error format for AI consumption

#### **4. Security Considerations**
- **Input validation** - All inputs validated against JSON schemas
- **Query restrictions** - SQL execution limited to read-only operations
- **Resource isolation** - Each tool has specific, limited database access

## 🧪 Part 4: Comprehensive Testing Strategy

Testing MCP servers requires a multi-layered approach since you're dealing with protocol communication, database operations, and AI assistant integration.

### Testing Architecture Overview

```mermaid
graph TB
    subgraph "Testing Layers"
        A["Unit Tests<br/>Individual functions"]
        B["Integration Tests<br/>Database + MCP protocol"]
        C["MCP Inspector<br/>Interactive testing"]
        D["End-to-End Tests<br/>Full Claude integration"]
    end
    
    subgraph "Test Targets"
        E["Database Layer<br/>CRUD operations"]
        F["MCP Protocol<br/>Tool/resource handling"]
        G["Error Handling<br/>Validation & recovery"]
        H["Performance<br/>Concurrent requests"]
    end
    
    subgraph "Testing Tools"
        I["pytest + pytest-asyncio<br/>Test framework"]
        J["MCP Inspector<br/>Protocol debugging"]
        K["PostgreSQL Test DB<br/>Isolated testing"]
        L["Claude Desktop<br/>Real-world testing"]
    end
    
    A --> E
    B --> F
    C --> G
    D --> H
    
    A --> I
    B --> I
    C --> J
    D --> L
    
    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
```

**Plain English Explanation:**
1. **Unit Tests** verify individual functions work correctly in isolation
2. **Integration Tests** ensure database and MCP protocol work together
3. **MCP Inspector** provides interactive debugging and protocol validation
4. **End-to-End Tests** verify the complete system works with Claude Desktop

### Method 1: MCP Inspector (Essential for Development)

The MCP Inspector is your primary debugging tool - it's like a web browser for MCP servers:

```bash
# Install inspector globally
npm install -g @modelcontextprotocol/inspector

# Test your server interactively
npx @modelcontextprotocol/inspector python /home/sanzad/git/mcp/main.py

# Or with environment variables
DATABASE_URL="postgresql://user:pass@localhost/db" \
npx @modelcontextprotocol/inspector python main.py
```

**What the Inspector provides:**
- **Interactive UI** - Click to test tools and view resources
- **Real-time JSON-RPC** - See exact protocol messages
- **Schema validation** - Verify tool input schemas work correctly
- **Error debugging** - Detailed error messages and stack traces
- **Performance monitoring** - See response times for each operation

**Inspector Testing Workflow:**
1. **Start Inspector** - Opens web interface
2. **Verify Tool Discovery** - Check all tools are listed correctly
3. **Test Tool Execution** - Try each tool with valid/invalid inputs
4. **Check Resources** - Verify resource URIs return expected data
5. **Error Testing** - Intentionally cause errors to verify handling

### Method 2: Comprehensive Unit Testing

```python
# tests/test_database.py
import pytest
import asyncio
import os
from src.database import TaskDatabase

class TestTaskDatabase:
    """Comprehensive database testing."""
    
    @pytest.fixture
    async def db(self):
        """Create test database connection."""
        test_db_url = os.getenv('TEST_DATABASE_URL', 
                               'postgresql://test_user:test_pass@localhost/test_mcp')
        db = TaskDatabase(test_db_url)
    await db.connect()
    
        # Clean up before each test
        await db.execute_command("TRUNCATE tasks, categories, task_comments RESTART IDENTITY CASCADE")
        
        yield db
        await db.disconnect()
    
    async def test_create_task_basic(self, db):
        """Test basic task creation."""
        task = await db.create_task(
            title="Test Task",
            description="Test description",
            priority="high"
        )
        
    assert task is not None
    assert task['title'] == "Test Task"
        assert task['description'] == "Test description"
        assert task['priority'] == "high"
        assert task['status'] == "pending"
        assert task['id'] is not None
    
    async def test_create_task_with_tags(self, db):
        """Test task creation with tags."""
        task = await db.create_task(
            title="Tagged Task",
            tags=["urgent", "frontend", "bug"]
        )
        
        assert task['tags'] == ["urgent", "frontend", "bug"]
    
    async def test_get_tasks_by_status(self, db):
        """Test status filtering."""
        # Create tasks with different statuses
        await db.create_task("Pending Task", priority="low")
        
        task2 = await db.create_task("In Progress Task", priority="high")
        await db.update_task_status(task2['id'], "in_progress")
        
        # Test filtering
        pending_tasks = await db.get_tasks_by_status("pending")
        progress_tasks = await db.get_tasks_by_status("in_progress")
        
        assert len(pending_tasks) == 1
        assert len(progress_tasks) == 1
        assert pending_tasks[0]['title'] == "Pending Task"
        assert progress_tasks[0]['title'] == "In Progress Task"
    
    async def test_error_handling(self, db):
        """Test database error handling."""
        # Test with invalid status
        with pytest.raises(Exception):
            await db.create_task("Test", priority="invalid_priority")
    
    async def test_concurrent_operations(self, db):
        """Test concurrent database access."""
        async def create_task(i):
            return await db.create_task(f"Concurrent Task {i}")
        
        # Create 10 tasks concurrently
        tasks = await asyncio.gather(*[create_task(i) for i in range(10)])
        
        assert len(tasks) == 10
        assert all(task is not None for task in tasks)
        assert len(set(task['id'] for task in tasks)) == 10  # All unique IDs

# tests/test_mcp_server.py
import pytest
from src.mcp_server import MCPTaskServer
import mcp.types as types

class TestMCPServer:
    """Test MCP protocol implementation."""
    
    @pytest.fixture
    async def server(self):
        """Create test MCP server."""
        test_db_url = os.getenv('TEST_DATABASE_URL')
        server = MCPTaskServer(test_db_url)
        await server.start()
        yield server
        await server.stop()
    
    async def test_list_tools(self, server):
        """Test tool discovery."""
        tools = await server.server._tool_handlers['list_tools']()
        
        assert len(tools) > 0
        tool_names = [tool.name for tool in tools]
        
        # Verify essential tools exist
        assert "create_task" in tool_names
        assert "list_tasks" in tool_names
        assert "update_task_status" in tool_names
        assert "delete_task" in tool_names
    
    async def test_create_task_tool(self, server):
        """Test create_task tool execution."""
        result = await server.server._tool_handlers['call_tool'](
            "create_task",
            {"title": "Test Task", "priority": "high"}
        )
        
        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)
        assert "created successfully" in result[0].text.lower()
        assert "Test Task" in result[0].text
    
    async def test_tool_validation(self, server):
        """Test input validation."""
        # Test missing required field
        result = await server.server._tool_handlers['call_tool'](
            "create_task",
            {}  # Missing title
        )
        
        assert "error" in result[0].text.lower()
    
    async def test_list_resources(self, server):
        """Test resource discovery."""
        resources = await server.server._resource_handlers['list_resources']()
        
        assert len(resources) > 0
        resource_uris = [resource.uri for resource in resources]
        
        assert "task://all" in resource_uris
        assert "schema://database" in resource_uris
    
    async def test_read_resource(self, server):
        """Test resource reading."""
        # Create a test task first
        await server.server._tool_handlers['call_tool'](
            "create_task",
            {"title": "Resource Test Task"}
        )
        
        # Read all tasks resource
        result = await server.server._resource_handlers['read_resource']("task://all")
        
        assert "Resource Test Task" in result
        # Should be valid JSON
        import json
        data = json.loads(result)
        assert isinstance(data, dict)
```

### Method 3: Integration Testing with Real Protocol

```python
# tests/test_integration.py
import pytest
import asyncio
import json
from mcp.server.stdio import stdio_server
from src.main import MCPTaskServer

class TestMCPIntegration:
    """Test full MCP protocol integration."""
    
    async def test_full_protocol_flow(self):
        """Test complete MCP handshake and operations."""
        server = MCPTaskServer("postgresql://test_user:test_pass@localhost/test_mcp")
        
        # Simulate MCP protocol messages
        async def send_request(method, params=None):
            """Simulate MCP client request."""
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method
            }
            if params:
                request["params"] = params
            return request
        
        # Test initialization
        await server.start()
        
        # Test tool listing
        tools_response = await server.server._tool_handlers['list_tools']()
        assert len(tools_response) > 0

# Test tool execution
        create_response = await server.server._tool_handlers['call_tool'](
            "create_task",
            {"title": "Integration Test Task", "priority": "medium"}
        )
        assert "created successfully" in create_response[0].text.lower()
        
        # Test resource reading
        resource_response = await server.server._resource_handlers['read_resource']("task://all")
        data = json.loads(resource_response)
        assert data['count'] >= 1
        
        await server.stop()
```

### Method 4: Performance and Load Testing

```python
# tests/test_performance.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

class TestPerformance:
    """Test server performance under load."""
    
    async def test_concurrent_tool_calls(self, server):
        """Test handling multiple concurrent requests."""
        async def create_task(i):
            start_time = time.time()
            result = await server.server._tool_handlers['call_tool'](
                "create_task",
                {"title": f"Load Test Task {i}"}
            )
            end_time = time.time()
            return end_time - start_time, result
        
        # Execute 50 concurrent requests
        tasks = [create_task(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        # Verify all succeeded
        assert len(results) == 50
        assert all("created successfully" in result[1][0].text.lower() 
                  for result in results)
        
        # Check performance
        avg_time = sum(result[0] for result in results) / len(results)
        assert avg_time < 1.0  # Should complete within 1 second on average
    
    async def test_database_connection_pool(self, server):
        """Test connection pool efficiency."""
        # Create many rapid database queries
        async def rapid_query():
            return await server.db.get_all_tasks()
        
        start_time = time.time()
        results = await asyncio.gather(*[rapid_query() for _ in range(100)])
        end_time = time.time()
        
        assert len(results) == 100
        assert end_time - start_time < 5.0  # Should complete quickly with pooling
```

### Method 5: End-to-End Testing with Claude

For the most comprehensive testing, test with actual Claude Desktop:

#### **1. Set up Test Configuration**
```json
// claude_config_test.json
{
  "mcpServers": {
    "mcp-task-server-test": {
      "command": "python",
      "args": ["/home/sanzad/git/mcp/main.py"],
      "env": {
        "DATABASE_URL": "postgresql://test_user:test_pass@localhost/test_mcp_e2e",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

#### **2. Manual Testing Checklist**
- [ ] **Server Discovery**: Does Claude find your server?
- [ ] **Tool Availability**: Are all tools visible in Claude's interface?
- [ ] **Tool Execution**: Can Claude successfully call each tool?
- [ ] **Error Handling**: Does Claude show meaningful errors for invalid inputs?
- [ ] **Resource Access**: Can Claude read and display resources correctly?
- [ ] **Performance**: Do operations complete in reasonable time?

#### **3. Automated E2E Testing**
```python
# tests/test_e2e.py
import subprocess
import time
import requests
import json

class TestEndToEnd:
    """End-to-end testing with real MCP client."""
    
    def test_server_startup(self):
        """Test that server starts correctly."""
        # Start server process
        process = subprocess.Popen(
            ["python", "main.py"],
            env={"DATABASE_URL": "postgresql://test_user:pass@localhost/test_db"},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            # Give server time to start
            time.sleep(2)
            
            # Check if process is running
            assert process.poll() is None, "Server process died"
            
        finally:
            process.terminate()
            process.wait()
```

### Testing Best Practices for MCP Servers

#### **1. Isolated Test Environment**
- Use separate test database
- Clean data between tests
- Mock external dependencies when needed

#### **2. Async Testing Patterns**
- Use `pytest-asyncio` for async test support
- Properly manage connection lifecycles
- Test concurrent operations

#### **3. Protocol Validation**
- Verify JSON-RPC message format
- Test schema validation thoroughly
- Check error response format

#### **4. Performance Monitoring**
- Set reasonable timeout expectations
- Test connection pool behavior
- Monitor memory usage during tests

#### **5. Error Scenario Testing**
- Test database connection failures
- Test invalid tool arguments
- Test resource not found scenarios
- Test malformed requests

## 🚀 Part 5: Production Deployment and Integration

Deploying MCP servers requires careful consideration of security, performance, and reliability. This section covers comprehensive deployment strategies for production environments.

### Deployment Architecture Options

```mermaid
graph TB
    subgraph "Development Environment"
        A["Local Claude Desktop"]
        B["Local MCP Server<br/>Python Process"]
        C["Local PostgreSQL<br/>Development DB"]
    end
    
    subgraph "Production Environment"
        D["Claude Desktop<br/>Multiple Users"]
        E["MCP Server Cluster<br/>Docker Containers"]
        F["Load Balancer<br/>nginx/HAProxy"]
        G["PostgreSQL Cluster<br/>Primary + Replicas"]
        H["Redis Cache<br/>Session Management"]
        I["Monitoring<br/>Prometheus + Grafana"]
    end
    
    subgraph "Cloud Deployment"
        J["Kubernetes Cluster"]
        K["Managed Database<br/>AWS RDS / Google Cloud SQL"]
        L["Container Registry<br/>Docker Hub / ECR"]
        M["Secret Management<br/>Vault / K8s Secrets"]
    end
    
    A --> B
    B --> C
    
    D --> F
    F --> E
    E --> G
    E --> H
    E --> I
    
    J --> E
    J --> K
    J --> L
    J --> M
    
    style A fill:#e3f2fd
    style D fill:#e3f2fd
    style E fill:#f3e5f5
    style G fill:#fff3e0
    style J fill:#e8f5e8
```

**Plain English Explanation:**
1. **Development**: Simple setup with local components for rapid iteration
2. **Production**: Scalable architecture with clustering, load balancing, and monitoring
3. **Cloud**: Managed services with automatic scaling and enterprise features

### Claude Desktop Configuration (Production-Ready)

```json
{
  "mcpServers": {
    "mcp-task-server": {
      "command": "python",
      "args": ["/home/sanzad/git/mcp/main.py"],
      "env": {
        "DATABASE_URL": "postgresql://mcp_user:secure_password@prod-db.company.com:5432/mcp_tasks",
        "LOG_LEVEL": "INFO",
        "POOL_SIZE": "20",
        "CACHE_TTL": "300",
        "ENVIRONMENT": "production"
      },
      "timeout": 30000,
      "retries": 3
    }
  }
}
```

### VS Code Configuration
```json
{
  "mcp": {
    "servers": {
      "task-server": {
        "command": "python",
        "args": ["/home/sanzad/git/mcp/main.py"],
        "env": {
          "DATABASE_URL": "postgresql://user:pass@localhost/mcp_tasks"
        }
      }
    }
  }
}
```

### Cursor IDE Integration: AI-Enhanced Development

Cursor IDE provides a unique integration pattern for MCP servers, focusing on **developer productivity** and **AI-assisted coding workflows**. Unlike Claude Desktop's general-purpose chat interface, Cursor embeds MCP capabilities directly into the development environment.

#### **Cursor vs Claude Desktop: Key Differences**

```mermaid
graph TB
    subgraph "Claude Desktop Usage"
        A1["💬 Chat Interface"]
        A2["🎯 General Productivity"]
        A3["📋 Task Management"]
        A4["📊 Data Analysis"]
        A5["📧 Communication"]
    end
    
    subgraph "Cursor IDE Usage"  
        B1["⌨️ Code Editor Integration"]
        B2["🛠️ Development Focus"]
        B3["🔧 Code Analysis"]
        B4["📁 Repository Management"]
        B5["🚀 DevOps Integration"]
    end
    
    subgraph "Shared MCP Server"
        C1["🏗️ Same Protocol"]
        C2["🔄 Same Tools"]
        C3["💾 Same Database"]
        C4["⚡ Different Context"]
    end
    
    A1 --> C1
    A2 --> C2
    A3 --> C3
    A4 --> C4
    A5 --> C4
    
    B1 --> C1
    B2 --> C2
    B3 --> C3
    B4 --> C4
    B5 --> C4
    
    style A1 fill:#e1f5fe
    style B1 fill:#e8f5e8
    style C1 fill:#f3e5f5
```

**Plain English Explanation:**
1. **Claude Desktop** uses MCP servers for general productivity tasks through a chat interface
2. **Cursor IDE** integrates MCP servers directly into the coding environment for development-specific workflows
3. **Same MCP Server** can serve both clients, but provides different experiences based on context
4. **Tools adapt** to the client context - general tasks for Claude, development tasks for Cursor

#### **Cursor MCP Configuration Methods**

##### **Method 1: Workspace Settings (Recommended)**
```json
// .vscode/settings.json (works for Cursor too)
{
  "mcp.servers": {
    "development-task-server": {
      "command": "python",
      "args": ["/home/sanzad/git/mcp/main.py"],
      "env": {
        "DATABASE_URL": "postgresql://dev_user:dev_pass@localhost:5432/mcp_dev_tasks",
        "LOG_LEVEL": "DEBUG",
        "ENVIRONMENT": "development"
      },
      "autoStart": true,
      "scope": "workspace"
    }
  },
  "mcp.enableContextualSuggestions": true,
  "mcp.showInlineTools": true
}
```

##### **Method 2: User Settings (Global)**
```json
// User settings for Cursor
{
  "mcp.servers": {
    "global-task-server": {
      "command": "python",
      "args": ["/path/to/your/mcp/server/main.py"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/mcp_tasks"
      },
      "scope": "global",
      "enabledLanguages": ["python", "javascript", "typescript", "*"]
    }
  }
}
```

##### **Method 3: Project-Specific Configuration**
```yaml
# .cursor/mcp-config.yaml
servers:
  task-management:
    command: python
    args: ["./scripts/start-mcp-server.py"]
    environment:
      DATABASE_URL: "${DATABASE_URL}"
      PROJECT_ROOT: "${workspaceRoot}"
      GIT_BRANCH: "${git.branch}"
    triggers:
      - fileChanged: "src/**/*.py"
      - gitCommit: true
      - debugStart: true
    tools:
      - create_task
      - link_task_to_file
      - generate_code_task
      - analyze_code_complexity
```

#### **Development-Focused MCP Tools for Cursor**

When your MCP server detects it's being used by Cursor IDE, you can provide development-specific tools:

```python
# Enhanced MCP server with development tools
class DevelopmentMCPServer(MCPTaskServer):
    """MCP server optimized for development environments."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_context = "cursor"  # Detected from environment
    
    def _get_development_tools(self) -> List[types.Tool]:
        """Development-specific tools for Cursor IDE."""
        return [
            types.Tool(
                name="create_code_task",
                description="Create a task linked to specific code files and lines",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title"},
                        "file_path": {"type": "string", "description": "Related file path"},
                        "line_number": {"type": "integer", "description": "Specific line number"},
                        "code_snippet": {"type": "string", "description": "Relevant code snippet"},
                        "task_type": {
                            "type": "string",
                            "enum": ["bug", "feature", "refactor", "test", "documentation"],
                            "description": "Type of development task"
                        },
                        "complexity": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Estimated complexity"
                        }
                    },
                    "required": ["title", "task_type"]
                }
            ),
            
            types.Tool(
                name="analyze_code_complexity",
                description="Analyze code complexity and suggest tasks for improvement",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "File to analyze"},
                        "include_suggestions": {
                            "type": "boolean", 
                            "default": True,
                            "description": "Include improvement suggestions"
                        }
                    },
                    "required": ["file_path"]
                }
            ),
            
            types.Tool(
                name="link_commit_to_task",
                description="Link git commits to tasks for better tracking",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "integer", "description": "Task ID"},
                        "commit_hash": {"type": "string", "description": "Git commit hash"},
                        "commit_message": {"type": "string", "description": "Commit message"},
                        "files_changed": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of files changed"
                        }
                    },
                    "required": ["task_id", "commit_hash"]
                }
            ),
            
            types.Tool(
                name="generate_test_tasks",
                description="Automatically generate testing tasks for code changes",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "File that needs testing"},
                        "functions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific functions to test"
                        },
                        "test_types": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["unit", "integration", "performance", "security"]
                            },
                            "description": "Types of tests to create"
                        }
                    },
                    "required": ["file_path"]
                }
            )
        ]
    
    async def _handle_create_code_task(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Create a development-specific task with code context."""
        
        # Standard task creation
        task_args = {
            'title': arguments['title'],
            'description': self._build_code_description(arguments),
            'priority': self._calculate_priority_from_complexity(arguments.get('complexity', 'medium')),
            'tags': [arguments['task_type'], 'development']
        }
        
        # Add code context to task
        if 'file_path' in arguments:
            task_args['tags'].append(f"file:{arguments['file_path']}")
        
        task = await self.db.create_task(**task_args)
        
        # Store code-specific metadata
        await self._store_code_metadata(task['id'], arguments)
        
        result = f"🔧 **Development Task Created**\n\n"
        result += f"**ID:** {task['id']}\n"
        result += f"**Title:** {task['title']}\n"
        result += f"**Type:** {arguments['task_type']}\n"
        result += f"**Priority:** {task['priority']}\n"
        
        if 'file_path' in arguments:
            result += f"**File:** `{arguments['file_path']}`\n"
            if 'line_number' in arguments:
                result += f"**Line:** {arguments['line_number']}\n"
        
        result += f"**Tags:** {', '.join(task['tags'])}\n"
        
        return [types.TextContent(type="text", text=result)]
    
    def _build_code_description(self, arguments: Dict[str, Any]) -> str:
        """Build rich description with code context."""
        description = []
        
        if 'file_path' in arguments:
            description.append(f"**File:** `{arguments['file_path']}`")
            
        if 'line_number' in arguments:
            description.append(f"**Line:** {arguments['line_number']}")
            
        if 'code_snippet' in arguments:
            description.append(f"**Code:**\n```\n{arguments['code_snippet']}\n```")
            
        return "\n\n".join(description)
    
    def _calculate_priority_from_complexity(self, complexity: str) -> str:
        """Map complexity to priority."""
        mapping = {
            'low': 'medium',
            'medium': 'high', 
            'high': 'urgent'
        }
        return mapping.get(complexity, 'medium')
    
    async def _store_code_metadata(self, task_id: int, arguments: Dict[str, Any]):
        """Store development-specific metadata."""
        metadata = {
            'file_path': arguments.get('file_path'),
            'line_number': arguments.get('line_number'),
            'code_snippet': arguments.get('code_snippet'),
            'task_type': arguments.get('task_type'),
            'complexity': arguments.get('complexity')
        }
        
        # Store in database (you'd need to create this table)
        await self.db.execute_command("""
            INSERT INTO task_code_metadata (task_id, metadata)
            VALUES ($1, $2)
            ON CONFLICT (task_id) DO UPDATE SET metadata = $2
        """, task_id, json.dumps(metadata))
```

#### **Cursor-Specific Workflow Examples**

##### **Workflow 1: Code Review Task Creation**
```python
# Cursor detects code changes and suggests task creation
async def _handle_code_review_tasks(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Create tasks for code review process."""
    
    file_changes = arguments.get('file_changes', [])
    review_tasks = []
    
    for file_change in file_changes:
        # Analyze the changed file
        complexity = await self._analyze_file_complexity(file_change['path'])
        
        # Create review task
        task = await self.db.create_task(
            title=f"Review changes in {file_change['path']}",
            description=f"Review {file_change['lines_added']} lines added, {file_change['lines_removed']} lines removed",
            priority='high' if complexity > 0.7 else 'medium',
            tags=['code-review', 'development', f"complexity:{complexity:.2f}"]
        )
        
        review_tasks.append(task)
    
    result = f"📋 **Code Review Tasks Created**\n\n"
    for i, task in enumerate(review_tasks, 1):
        result += f"{i}. **{task['title']}** (Priority: {task['priority']})\n"
    
    return [types.TextContent(type="text", text=result)]
```

##### **Workflow 2: Automatic Test Task Generation**
```python
async def _handle_generate_test_tasks(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Generate comprehensive testing tasks."""
    
    file_path = arguments['file_path']
    test_types = arguments.get('test_types', ['unit'])
    
    # Analyze the file to understand what needs testing
    functions = await self._extract_functions_from_file(file_path)
    
    test_tasks = []
    for test_type in test_types:
        for function in functions:
            task = await self.db.create_task(
                title=f"Write {test_type} tests for {function['name']}()",
                description=self._generate_test_description(function, test_type),
                priority=self._get_test_priority(function, test_type),
                tags=[f'{test_type}-test', 'testing', f'function:{function["name"]}']
            )
            test_tasks.append(task)
    
    result = f"🧪 **Test Tasks Generated**\n\n"
    result += f"Created {len(test_tasks)} test tasks for `{file_path}`\n\n"
    
    by_type = {}
    for task in test_tasks:
        test_type = task['tags'][0].replace('-test', '')
        if test_type not in by_type:
            by_type[test_type] = []
        by_type[test_type].append(task)
    
    for test_type, tasks in by_type.items():
        result += f"**{test_type.title()} Tests ({len(tasks)})**:\n"
        for task in tasks:
            result += f"• {task['title']}\n"
        result += "\n"
    
    return [types.TextContent(type="text", text=result)]
```

#### **Enhanced Resource Endpoints for Development**

```python
# Development-specific resources
@self.server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """Enhanced resources for development context."""
    base_resources = await super().handle_list_resources()
    
    if self.client_context == "cursor":
        dev_resources = [
            types.Resource(
                uri="dev://active-branch-tasks",
                name="Current Branch Tasks",
                description="Tasks related to the current git branch",
                mimeType="application/json"
            ),
            types.Resource(
                uri="dev://code-complexity-report",
                name="Code Complexity Report",
                description="Analysis of code complexity across the project",
                mimeType="application/json"
            ),
            types.Resource(
                uri="dev://test-coverage-gaps",
                name="Test Coverage Gaps",
                description="Areas of code that need test coverage",
                mimeType="application/json"
            ),
            types.Resource(
                uri="dev://technical-debt-tasks",
                name="Technical Debt Tasks",
                description="Tasks focused on reducing technical debt",
                mimeType="application/json"
            )
        ]
        return base_resources + dev_resources
    
    return base_resources

async def _read_dev_resource(self, uri: str) -> str:
    """Handle development-specific resource requests."""
    
    if uri == "dev://active-branch-tasks":
        # Get current git branch (would need git integration)
        current_branch = await self._get_current_git_branch()
        tasks = await self.db.execute_query("""
            SELECT t.*, array_agg(tm.metadata->'file_path') as related_files
            FROM tasks t
            LEFT JOIN task_code_metadata tm ON t.id = tm.task_id
            WHERE t.tags @> ARRAY[$1]
            AND t.status != 'completed'
            GROUP BY t.id
            ORDER BY t.priority DESC, t.created_at DESC
        """, f"branch:{current_branch}")
        
        return json.dumps({
            "branch": current_branch,
            "task_count": len(tasks),
            "tasks": tasks
        }, default=str, indent=2)
    
    elif uri == "dev://code-complexity-report":
        # Analyze code complexity across the project
        complexity_data = await self._generate_complexity_report()
        return json.dumps(complexity_data, default=str, indent=2)
    
    # ... handle other dev resources
```

#### **Cursor IDE Integration Best Practices**

##### **1. Context-Aware Tool Selection**
```python
def _get_tools_for_context(self, client_context: str, file_type: str = None) -> List[str]:
    """Return relevant tools based on context."""
    
    base_tools = ["create_task", "list_tasks", "update_task_status"]
    
    if client_context == "cursor":
        dev_tools = [
            "create_code_task",
            "analyze_code_complexity", 
            "link_commit_to_task",
            "generate_test_tasks"
        ]
        
        if file_type == "python":
            dev_tools.extend(["analyze_python_imports", "suggest_refactoring"])
        elif file_type == "javascript":
            dev_tools.extend(["check_npm_vulnerabilities", "optimize_bundle"])
        
        return base_tools + dev_tools
    
    return base_tools
```

##### **2. Intelligent Task Suggestions**
```python
async def _suggest_tasks_for_cursor(self, file_path: str, changes: List[str]) -> List[Dict]:
    """Suggest relevant tasks based on code changes."""
    
    suggestions = []
    
    # Analyze the changes
    for change in changes:
        if "TODO" in change:
            suggestions.append({
                "type": "todo_task",
                "title": f"Address TODO in {file_path}",
                "priority": "medium",
                "description": f"TODO found: {change.strip()}"
            })
        
        if "FIXME" in change:
            suggestions.append({
                "type": "bug_task", 
                "title": f"Fix issue in {file_path}",
                "priority": "high",
                "description": f"FIXME found: {change.strip()}"
            })
        
        if any(keyword in change.lower() for keyword in ["test", "spec"]):
            suggestions.append({
                "type": "test_task",
                "title": f"Update tests for {file_path}",
                "priority": "medium", 
                "description": "Test-related changes detected"
            })
    
    return suggestions
```

##### **3. Development Metrics Integration**
```python
# Add development-specific metrics
class CursorMCPMetrics:
    """Metrics specific to development workflows."""
    
    def __init__(self):
        self.code_tasks_created = 0
        self.files_analyzed = 0
        self.test_tasks_generated = 0
        self.commits_linked = 0
    
    async def track_development_activity(self, activity_type: str, metadata: Dict):
        """Track development-specific activities."""
        
        if activity_type == "code_task_created":
            self.code_tasks_created += 1
            
        elif activity_type == "file_analyzed":
            self.files_analyzed += 1
            
        elif activity_type == "test_task_generated":
            self.test_tasks_generated += 1
            
        # Store metrics for analysis
        await self._store_metric(activity_type, metadata)
    
    async def get_development_report(self) -> Dict:
        """Generate development productivity report."""
        return {
            "code_tasks_created": self.code_tasks_created,
            "files_analyzed": self.files_analyzed,
            "test_tasks_generated": self.test_tasks_generated,
            "commits_linked": self.commits_linked,
            "productivity_score": self._calculate_productivity_score()
        }
```

This comprehensive Cursor IDE integration transforms your MCP server into a powerful development companion that enhances coding workflows, automates task creation, and provides intelligent insights directly within the development environment.

#### **Testing Cursor IDE Integration**

To ensure your MCP server works perfectly with Cursor IDE, follow this comprehensive testing approach:

##### **1. Setup Test Environment**
```bash
# Create a test project for Cursor integration
mkdir cursor-mcp-test && cd cursor-mcp-test

# Initialize git repository
git init
git config user.name "Test User"
git config user.email "test@example.com"

# Create test files
echo "# Test Project for MCP Integration" > README.md
mkdir src tests
echo "def hello_world(): pass" > src/main.py
echo "# TODO: Add comprehensive tests" > tests/test_main.py

# Commit initial files
git add . && git commit -m "Initial project setup"
```

##### **2. Configure MCP Server for Testing**
```json
// .vscode/settings.json
{
  "mcp.servers": {
    "cursor-test-server": {
      "command": "python",
      "args": ["/path/to/your/mcp/main.py"],
      "env": {
        "DATABASE_URL": "postgresql://test_user:test_pass@localhost:5432/mcp_cursor_test",
        "LOG_LEVEL": "DEBUG",
        "CLIENT_CONTEXT": "cursor",
        "PROJECT_ROOT": "${workspaceRoot}"
      },
      "autoStart": true,
      "enabledLanguages": ["python", "javascript", "*"]
    }
  }
}
```

##### **3. Test Development Workflows**
```python
# Test script: test_cursor_integration.py
import asyncio
import json
from pathlib import Path

async def test_cursor_workflows():
    """Test all Cursor-specific MCP workflows."""
    
    test_cases = [
        {
            "name": "Create Code Task",
            "tool": "create_code_task",
            "arguments": {
                "title": "Fix TODO in main.py",
                "file_path": "src/main.py",
                "line_number": 1,
                "task_type": "bug",
                "complexity": "low",
                "code_snippet": "def hello_world(): pass  # TODO: implement"
            }
        },
        {
            "name": "Analyze Code Complexity", 
            "tool": "analyze_code_complexity",
            "arguments": {
                "file_path": "src/main.py",
                "include_suggestions": True
            }
        },
        {
            "name": "Generate Test Tasks",
            "tool": "generate_test_tasks", 
            "arguments": {
                "file_path": "src/main.py",
                "functions": ["hello_world"],
                "test_types": ["unit", "integration"]
            }
        }
    ]
    
    results = {}
    for test_case in test_cases:
        try:
            # Simulate MCP tool call
            result = await call_mcp_tool(test_case["tool"], test_case["arguments"])
            results[test_case["name"]] = {"status": "✅ PASSED", "result": result}
        except Exception as e:
            results[test_case["name"]] = {"status": "❌ FAILED", "error": str(e)}
    
    return results

# Run tests
if __name__ == "__main__":
    results = asyncio.run(test_cursor_workflows())
    for test_name, result in results.items():
        print(f"{result['status']} {test_name}")
```

##### **4. Interactive Testing Checklist**

**✅ Basic Integration**
- [ ] Cursor can discover the MCP server
- [ ] Tools appear in Cursor's command palette
- [ ] Server starts automatically when Cursor opens
- [ ] Error messages are clear and actionable

**✅ Development Workflows**  
- [ ] Create code task from file context
- [ ] Link tasks to specific code lines
- [ ] Generate test tasks for functions
- [ ] Analyze code complexity
- [ ] Link git commits to tasks

**✅ Context Awareness**
- [ ] Server detects Cursor as client
- [ ] Development-specific tools are available
- [ ] Resources show current branch tasks
- [ ] File types trigger appropriate tools

**✅ Performance**
- [ ] Tool calls complete within 2 seconds
- [ ] No memory leaks during long sessions
- [ ] Multiple concurrent requests work
- [ ] Server handles file changes efficiently

##### **5. Debugging Cursor Integration Issues**

```python
# Debug helper for Cursor MCP integration
class CursorMCPDebugger:
    """Debug utilities for Cursor MCP integration."""
    
    def __init__(self, server):
        self.server = server
        self.debug_log = []
    
    async def debug_tool_call(self, tool_name: str, arguments: dict):
        """Debug a specific tool call."""
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "arguments": arguments,
            "client_context": getattr(self.server, 'client_context', 'unknown')
        }
        
        try:
            result = await self.server.handle_call_tool(tool_name, arguments)
            debug_info["status"] = "success"
            debug_info["result"] = result
        except Exception as e:
            debug_info["status"] = "error" 
            debug_info["error"] = str(e)
            debug_info["traceback"] = traceback.format_exc()
        
        self.debug_log.append(debug_info)
        return debug_info
    
    def get_debug_report(self) -> str:
        """Generate comprehensive debug report."""
        report = "🔍 **Cursor MCP Debug Report**\n\n"
        
        successful_calls = [log for log in self.debug_log if log["status"] == "success"]
        failed_calls = [log for log in self.debug_log if log["status"] == "error"]
        
        report += f"**Total Calls:** {len(self.debug_log)}\n"
        report += f"**Successful:** {len(successful_calls)}\n"
        report += f"**Failed:** {len(failed_calls)}\n\n"
        
        if failed_calls:
            report += "**Failed Calls:**\n"
            for call in failed_calls:
                report += f"• {call['tool_name']}: {call['error']}\n"
        
        return report
```

##### **6. Production Readiness for Cursor**

```yaml
# cursor-production-checklist.yaml
cursor_mcp_production:
  configuration:
    - workspace_specific_settings: true
    - auto_start_enabled: true
    - appropriate_timeouts: true
    - debug_mode_disabled: true
    
  performance:
    - tool_response_time: "< 2 seconds"
    - memory_usage: "< 100MB"
    - cpu_usage: "< 10% sustained"
    - file_watch_efficiency: true
    
  development_features:
    - code_task_creation: enabled
    - git_integration: enabled
    - test_generation: enabled
    - complexity_analysis: enabled
    - branch_awareness: enabled
    
  monitoring:
    - tool_usage_metrics: enabled
    - error_tracking: enabled
    - performance_monitoring: enabled
    - user_productivity_analytics: enabled
```

This testing framework ensures your MCP server provides a seamless, productive experience for developers using Cursor IDE.

### Docker Deployment

#### **Dockerfile for Production**
```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY main.py .
COPY sql/ ./sql/

# Create non-root user
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app
USER mcpuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; from src.database import TaskDatabase; \
                   asyncio.run(TaskDatabase('$DATABASE_URL').connect())" || exit 1

# Run the server
CMD ["python", "main.py"]
```

#### **Docker Compose for Development**
```yaml
version: '3.8'

services:
  mcp-server:
    build: .
    environment:
      - DATABASE_URL=postgresql://mcp_user:mcp_password@postgres:5432/mcp_tasks
      - LOG_LEVEL=DEBUG
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./src:/app/src
      - ./main.py:/app/main.py
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=mcp_tasks
      - POSTGRES_USER=mcp_user
      - POSTGRES_PASSWORD=mcp_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./sql/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mcp_user -d mcp_tasks"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

#### **Production Docker Compose**
```yaml
version: '3.8'

services:
  mcp-server:
    image: your-registry/mcp-task-server:latest
    replicas: 3
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - LOG_LEVEL=INFO
      - POOL_SIZE=20
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
      restart_policy:
        condition: on-failure
        max_attempts: 3
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - mcp-server
```

### Kubernetes Deployment

#### **Kubernetes Manifests**
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mcp-system

---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-task-server
  namespace: mcp-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-task-server
  template:
    metadata:
      labels:
        app: mcp-task-server
    spec:
      containers:
      - name: mcp-server
        image: your-registry/mcp-task-server:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: database-url
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: mcp-task-server-service
  namespace: mcp-system
spec:
  selector:
    app: mcp-task-server
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP

---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: mcp-secrets
  namespace: mcp-system
type: Opaque
data:
  database-url: <base64-encoded-database-url>
```

### Environment-Specific Configuration

#### **Production Environment Setup**
```python
# config/production.py
import os
from dataclasses import dataclass

@dataclass
class ProductionConfig:
    """Production configuration settings."""
    
    # Database settings
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    DB_POOL_MIN_SIZE: int = int(os.getenv('DB_POOL_MIN_SIZE', '5'))
    DB_POOL_MAX_SIZE: int = int(os.getenv('DB_POOL_MAX_SIZE', '20'))
    DB_TIMEOUT: int = int(os.getenv('DB_TIMEOUT', '30'))
    
    # Server settings
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    ENABLE_METRICS: bool = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'
    METRICS_PORT: int = int(os.getenv('METRICS_PORT', '9090'))
    
    # Security settings
    ENABLE_RATE_LIMITING: bool = True
    MAX_REQUESTS_PER_MINUTE: int = 60
    ENABLE_REQUEST_LOGGING: bool = True
    
    # Cache settings
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', '300'))
    
    def validate(self):
        """Validate configuration."""
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set")
        
        if self.DB_POOL_MAX_SIZE < self.DB_POOL_MIN_SIZE:
            raise ValueError("DB_POOL_MAX_SIZE must be >= DB_POOL_MIN_SIZE")

# main.py updates for production
async def main():
    """Production-ready main function."""
    # Load configuration
    config = ProductionConfig()
    config.validate()
    
    # Set up enhanced logging
    setup_production_logging(config.LOG_LEVEL)
    
    # Start metrics server if enabled
    if config.ENABLE_METRICS:
        start_metrics_server(config.METRICS_PORT)
    
    # Create and run server
    server = MCPTaskServer(config.DATABASE_URL, config)
    await server.run()

def setup_production_logging(log_level: str):
    """Set up structured logging for production."""
    import structlog
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
```

### Advanced Configuration Management

#### **Configuration with Environment Override**
```python
# config/settings.py
import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
import json

class ConfigManager:
    """Advanced configuration management with multiple sources."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._config = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from multiple sources in priority order."""
        # 1. Default values
        self._config = self._get_defaults()
        
        # 2. Config file (if provided)
        if self.config_file and Path(self.config_file).exists():
            file_config = self._load_config_file(self.config_file)
            self._merge_config(file_config)
        
        # 3. Environment variables (highest priority)
        env_config = self._load_from_env()
        self._merge_config(env_config)
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Default configuration values."""
        return {
            'database': {
                'url': 'postgresql://localhost/mcp_tasks',
                'pool_size': {'min': 2, 'max': 10},
                'timeout': 60
            },
            'server': {
                'name': 'mcp-task-server',
                'version': '1.0.0',
                'log_level': 'INFO'
            },
            'features': {
                'enable_metrics': False,
                'enable_caching': False,
                'enable_rate_limiting': False
            }
        }
    
    def _load_config_file(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file."""
        with open(file_path, 'r') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                return yaml.safe_load(f)
            elif file_path.endswith('.json'):
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {file_path}")
    
    def _load_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_mapping = {
            'DATABASE_URL': 'database.url',
            'DB_POOL_MIN_SIZE': 'database.pool_size.min',
            'DB_POOL_MAX_SIZE': 'database.pool_size.max',
            'DB_TIMEOUT': 'database.timeout',
            'LOG_LEVEL': 'server.log_level',
            'ENABLE_METRICS': 'features.enable_metrics',
            'ENABLE_CACHING': 'features.enable_caching',
            'ENABLE_RATE_LIMITING': 'features.enable_rate_limiting'
        }
        
        config = {}
        for env_var, config_path in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(config, config_path, self._convert_value(value))
        
        return config
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """Recursively merge new configuration into existing."""
        def merge_dict(base: dict, update: dict):
            for key, value in update.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self._config, new_config)
    
    def _set_nested_value(self, config: dict, path: str, value: Any):
        """Set nested dictionary value using dot notation."""
        keys = path.split('.')
        current = config
        
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        
        current[keys[-1]] = value
    
    def _convert_value(self, value: str) -> Any:
        """Convert string environment variable to appropriate type."""
        # Boolean conversion
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Integer conversion
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float conversion
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation."""
        keys = path.split('.')
        current = self._config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def to_dict(self) -> Dict[str, Any]:
        """Return complete configuration as dictionary."""
        return self._config.copy()

# Usage in main.py
def main():
    config_manager = ConfigManager(os.getenv('CONFIG_FILE'))
    
    database_url = config_manager.get('database.url')
    log_level = config_manager.get('server.log_level')
    enable_metrics = config_manager.get('features.enable_metrics')
    
    server = MCPTaskServer(database_url, config_manager)
    asyncio.run(server.run())
```

### Security and Authentication

#### **Environment-based Security**
```python
# security/auth.py
import os
import jwt
from datetime import datetime, timedelta
from typing import Optional

class SecurityManager:
    """Handle security and authentication for MCP server."""
    
    def __init__(self):
        self.jwt_secret = os.getenv('JWT_SECRET', 'dev-secret-change-in-prod')
        self.enable_auth = os.getenv('ENABLE_AUTH', 'false').lower() == 'true'
        self.allowed_clients = set(os.getenv('ALLOWED_CLIENTS', '').split(','))
    
    def validate_client(self, client_info: dict) -> bool:
        """Validate client connection."""
        if not self.enable_auth:
            return True
        
        client_id = client_info.get('client_id')
        return client_id in self.allowed_clients
    
    def generate_token(self, client_id: str) -> str:
        """Generate JWT token for client."""
        payload = {
            'client_id': client_id,
            'issued_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def validate_token(self, token: str) -> Optional[dict]:
        """Validate JWT token."""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check expiration
            expires_at = datetime.fromisoformat(payload['expires_at'])
            if datetime.utcnow() > expires_at:
                return None
            
            return payload
        except jwt.InvalidTokenError:
            return None
```

### Monitoring and Observability

#### **Metrics Collection**
```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from functools import wraps

# Metrics definitions
TOOL_CALLS_TOTAL = Counter('mcp_tool_calls_total', 'Total tool calls', ['tool_name', 'status'])
TOOL_CALL_DURATION = Histogram('mcp_tool_call_duration_seconds', 'Tool call duration', ['tool_name'])
ACTIVE_CONNECTIONS = Gauge('mcp_active_connections', 'Active MCP connections')
DATABASE_CONNECTIONS = Gauge('mcp_database_connections', 'Active database connections')

def monitor_tool_call(func):
    """Decorator to monitor tool call metrics."""
    @wraps(func)
    async def wrapper(self, name: str, arguments: dict):
        start_time = time.time()
        
        try:
            result = await func(self, name, arguments)
            TOOL_CALLS_TOTAL.labels(tool_name=name, status='success').inc()
            return result
        except Exception as e:
            TOOL_CALLS_TOTAL.labels(tool_name=name, status='error').inc()
            raise
        finally:
            duration = time.time() - start_time
            TOOL_CALL_DURATION.labels(tool_name=name).observe(duration)
    
    return wrapper

def start_metrics_server(port: int = 9090):
    """Start Prometheus metrics server."""
    start_http_server(port)
    print(f"Metrics server started on port {port}")
```

This comprehensive deployment section covers everything from local development to enterprise-scale production deployments with security, monitoring, and configuration management.

## 🎯 Part 6: Advanced MCP Patterns and Features

Advanced MCP servers require sophisticated patterns for handling complex scenarios, optimizing performance, and providing rich user experiences.

### Advanced Error Handling and Recovery

```mermaid
graph TB
    subgraph "Error Handling Pipeline"
        A["User Request"]
        B["Input Validation"]
        C["Tool Execution"]
        D["Database Operation"]
        E["Success Response"]
        F["Validation Error"]
        G["Execution Error"]
        H["Database Error"]
        I["Recovery Strategy"]
        J["Error Response"]
    end
    
    A --> B
    B --> C
    B --> F
    C --> D
    C --> G
    D --> E
    D --> H
    F --> J
    G --> I
    H --> I
    I --> J
    
    style A fill:#e3f2fd
    style E fill:#e8f5e8
    style F fill:#ffebee
    style G fill:#ffebee
    style H fill:#ffebee
    style I fill:#fff3e0
    style J fill:#fce4ec
```

**Plain English Explanation:**
1. **User Request** enters the system through MCP protocol
2. **Input Validation** checks for proper format and required fields
3. **Tool Execution** runs the business logic
4. **Database Operation** performs data persistence
5. **Error Types** are categorized for appropriate handling
6. **Recovery Strategy** attempts to fix or work around issues
7. **Error Response** provides meaningful feedback to the user

#### **Comprehensive Error Handling Framework**
```python
# errors/handling.py
from enum import Enum
from typing import Optional, Dict, Any, List
import traceback
import mcp.types as types

class ErrorSeverity(Enum):
    LOW = "low"           # Recoverable, user can retry
    MEDIUM = "medium"     # Partial failure, some features unavailable
    HIGH = "high"         # Operation failed, manual intervention needed
    CRITICAL = "critical" # System-level failure

class MCPError(Exception):
    """Base exception for MCP server errors."""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.MEDIUM, 
                 details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.details = details or {}

class ValidationError(MCPError):
    """Input validation errors."""
    
    def __init__(self, field: str, message: str, value: Any = None):
        super().__init__(f"Validation failed for '{field}': {message}", ErrorSeverity.LOW)
        self.field = field
        self.value = value

class DatabaseError(MCPError):
    """Database operation errors."""
    
    def __init__(self, operation: str, message: str, query: Optional[str] = None):
        super().__init__(f"Database {operation} failed: {message}", ErrorSeverity.HIGH)
        self.operation = operation
        self.query = query

class BusinessLogicError(MCPError):
    """Business rule violations."""
    
    def __init__(self, rule: str, message: str):
        super().__init__(f"Business rule '{rule}' violated: {message}", ErrorSeverity.MEDIUM)
        self.rule = rule

class ErrorHandler:
    """Advanced error handling with recovery strategies."""
    
    def __init__(self, logger):
        self.logger = logger
        self.error_counts = {}  # Track error patterns
    
    async def handle_tool_error(self, tool_name: str, error: Exception, 
                               arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Handle tool execution errors with recovery attempts."""
        
        # Log error details
        self._log_error(tool_name, error, arguments)
        
        # Track error patterns
        self._track_error(tool_name, error)
        
        # Attempt recovery
        recovery_result = await self._attempt_recovery(tool_name, error, arguments)
        if recovery_result:
            return recovery_result
        
        # Format user-friendly error response
        return self._format_error_response(error)
    
    def _log_error(self, tool_name: str, error: Exception, arguments: Dict[str, Any]):
        """Log detailed error information."""
        error_context = {
            "tool_name": tool_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "arguments": arguments,
            "traceback": traceback.format_exc()
        }
        
        if isinstance(error, MCPError):
            error_context["severity"] = error.severity.value
            error_context["details"] = error.details
        
        self.logger.error("Tool execution failed", extra=error_context)
    
    def _track_error(self, tool_name: str, error: Exception):
        """Track error patterns for monitoring."""
        error_key = f"{tool_name}:{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Alert if error frequency is high
        if self.error_counts[error_key] > 10:
            self.logger.warning(f"High error frequency detected: {error_key}")
    
    async def _attempt_recovery(self, tool_name: str, error: Exception, 
                               arguments: Dict[str, Any]) -> Optional[List[types.TextContent]]:
        """Attempt to recover from specific error types."""
        
        if isinstance(error, DatabaseError) and "timeout" in str(error).lower():
            # Retry with simpler query
            return await self._retry_with_fallback(tool_name, arguments)
        
        elif isinstance(error, ValidationError):
            # Suggest corrected input
            return self._suggest_correction(error, arguments)
        
        elif isinstance(error, BusinessLogicError):
            # Provide alternative actions
            return self._suggest_alternatives(tool_name, error)
        
        return None
    
    async def _retry_with_fallback(self, tool_name: str, 
                                  arguments: Dict[str, Any]) -> Optional[List[types.TextContent]]:
        """Implement fallback strategies for database timeouts."""
        # Implementation depends on specific tool
        return None
    
    def _suggest_correction(self, error: ValidationError, 
                           arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Suggest input corrections."""
        suggestions = {
            "priority": "Valid priorities are: low, medium, high, urgent",
            "status": "Valid statuses are: pending, in_progress, completed, cancelled",
            "assigned_to": "Please provide a valid username",
            "due_date": "Please use ISO format: YYYY-MM-DDTHH:MM:SS"
        }
        
        suggestion = suggestions.get(error.field, "Please check the input format")
        
        return [types.TextContent(
            type="text",
            text=f"❌ Input Error: {error.message}\n\n💡 Suggestion: {suggestion}"
        )]
    
    def _suggest_alternatives(self, tool_name: str, 
                             error: BusinessLogicError) -> List[types.TextContent]:
        """Suggest alternative actions for business rule violations."""
        alternatives = {
            "task_already_completed": [
                "Update the task description instead",
                "Create a new related task",
                "Add a comment to the existing task"
            ],
            "user_not_authorized": [
                "Request permission from the task owner",
                "Ask an administrator to make the change",
                "Work on tasks assigned to you"
            ]
        }
        
        suggestions = alternatives.get(error.rule, ["Check the system requirements"])
        suggestion_text = "\n".join(f"• {s}" for s in suggestions)
        
        return [types.TextContent(
            type="text",
            text=f"❌ Business Rule Violation: {error.message}\n\n💡 Alternatives:\n{suggestion_text}"
        )]
    
    def _format_error_response(self, error: Exception) -> List[types.TextContent]:
        """Format a user-friendly error response."""
        if isinstance(error, MCPError):
            icon = {
                ErrorSeverity.LOW: "⚠️",
                ErrorSeverity.MEDIUM: "❌",
                ErrorSeverity.HIGH: "🚨",
                ErrorSeverity.CRITICAL: "💥"
            }[error.severity]
            
            return [types.TextContent(
                type="text",
                text=f"{icon} {error.message}"
            )]
        else:
            return [types.TextContent(
                type="text",
                text=f"❌ An unexpected error occurred: {str(error)}"
            )]
```

### Advanced Input Validation and Sanitization

```python
# validation/schemas.py
from typing import Any, Dict, List, Optional, Union
import re
from datetime import datetime
import html

class AdvancedValidator:
    """Comprehensive input validation and sanitization."""
    
    # Common validation patterns
    PATTERNS = {
        'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
        'username': re.compile(r'^[a-zA-Z0-9_-]{3,30}$'),
        'hex_color': re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'),
        'sql_injection': re.compile(r'(\'|(\'\')|(\-\-)|(%27)|(%2D%2D))', re.IGNORECASE)
    }
    
    @classmethod
    def validate_task_input(cls, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive task input validation."""
        validated = {}
        
        # Required fields
        if 'title' not in arguments:
            raise ValidationError('title', 'Title is required')
        
        # Title validation and sanitization
        title = str(arguments['title']).strip()
        if not title:
            raise ValidationError('title', 'Title cannot be empty')
        if len(title) > 255:
            raise ValidationError('title', 'Title must be 255 characters or less')
        
        # Sanitize HTML
        validated['title'] = html.escape(title)
        
        # Description validation
        if 'description' in arguments:
            description = str(arguments['description']).strip()
            if len(description) > 1000:
                raise ValidationError('description', 'Description must be 1000 characters or less')
            validated['description'] = html.escape(description) if description else None
        
        # Priority validation
        priority = arguments.get('priority', 'medium')
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if priority not in valid_priorities:
            raise ValidationError('priority', f'Priority must be one of: {", ".join(valid_priorities)}', priority)
        validated['priority'] = priority
        
        # Assigned to validation
        if 'assigned_to' in arguments:
            assigned_to = str(arguments['assigned_to']).strip()
            if assigned_to and not cls.PATTERNS['username'].match(assigned_to):
                raise ValidationError('assigned_to', 'Invalid username format', assigned_to)
            validated['assigned_to'] = assigned_to if assigned_to else None
        
        # Due date validation
        if 'due_date' in arguments:
            due_date = arguments['due_date']
            if due_date:
                try:
                    # Parse ISO format
                    parsed_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    # Ensure it's in the future
                    if parsed_date <= datetime.now():
                        raise ValidationError('due_date', 'Due date must be in the future')
                    validated['due_date'] = parsed_date
                except ValueError:
                    raise ValidationError('due_date', 'Invalid date format, use ISO format (YYYY-MM-DDTHH:MM:SS)')
        
        # Tags validation
        if 'tags' in arguments:
            tags = arguments['tags']
            if not isinstance(tags, list):
                raise ValidationError('tags', 'Tags must be a list')
            if len(tags) > 10:
                raise ValidationError('tags', 'Maximum 10 tags allowed')
            
            validated_tags = []
            for i, tag in enumerate(tags):
                tag_str = str(tag).strip()
                if not tag_str:
                    raise ValidationError('tags', f'Tag {i+1} cannot be empty')
                if len(tag_str) > 50:
                    raise ValidationError('tags', f'Tag {i+1} must be 50 characters or less')
                validated_tags.append(html.escape(tag_str))
            
            validated['tags'] = validated_tags
        
        return validated
    
    @classmethod
    def validate_query_input(cls, query: str) -> str:
        """Validate and sanitize SQL query input."""
        if not query.strip():
            raise ValidationError('query', 'Query cannot be empty')
        
        # Check for SQL injection patterns
        if cls.PATTERNS['sql_injection'].search(query):
            raise ValidationError('query', 'Query contains potentially dangerous patterns')
        
        # Ensure it's a SELECT query
        query_upper = query.strip().upper()
        if not query_upper.startswith('SELECT'):
            raise ValidationError('query', 'Only SELECT queries are allowed')
        
        # Check for dangerous keywords
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValidationError('query', f'Keyword "{keyword}" is not allowed')
        
        return query.strip()
```

### Performance Optimization and Caching

```python
# performance/caching.py
import asyncio
import json
import time
from typing import Any, Optional, Dict, Callable, Hashable
from functools import wraps
import hashlib

class CacheManager:
    """Advanced caching with TTL and invalidation."""
    
    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments."""
        key_data = json.dumps([args, sorted(kwargs.items())], sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        return time.time() > entry['expires_at']
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            entry = self.cache[key]
            if not self._is_expired(entry):
                return entry['value']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Invalidate all cache entries matching pattern."""
        keys_to_remove = [key for key in self.cache.keys() if pattern in key]
        for key in keys_to_remove:
            del self.cache[key]
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()

def cached_tool(ttl: int = 300, invalidate_on: Optional[List[str]] = None):
    """Decorator for caching tool results."""
    def decorator(func: Callable):
        cache = CacheManager(ttl)
        
        @wraps(func)
        async def wrapper(self, arguments: Dict[str, Any]):
            # Generate cache key
            cache_key = cache._generate_key(func.__name__, **arguments)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                self.logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function
            self.logger.debug(f"Cache miss for {func.__name__}")
            result = await func(self, arguments)
            
            # Cache the result
            cache.set(cache_key, result, ttl)
            
            return result
        
        # Add cache invalidation method
        wrapper.invalidate_cache = lambda pattern=None: cache.invalidate_pattern(pattern or func.__name__)
        wrapper.clear_cache = cache.clear
        
        return wrapper
    return decorator

# Usage in MCP server
class OptimizedMCPServer(MCPTaskServer):
    """MCP server with performance optimizations."""
    
    @cached_tool(ttl=600)  # Cache for 10 minutes
    async def _handle_list_tasks(self, arguments: Dict[str, Any]):
        """Cached task listing."""
        return await super()._handle_list_tasks(arguments)
    
    @cached_tool(ttl=300, invalidate_on=['create_task', 'update_task_status'])
    async def _handle_get_task_statistics(self, arguments: Dict[str, Any]):
        """Get cached task statistics."""
        stats = await self.db.execute_query("""
            SELECT 
                status,
                COUNT(*) as count,
                AVG(EXTRACT(EPOCH FROM (NOW() - created_at))/3600) as avg_age_hours
            FROM tasks 
            GROUP BY status
        """)
        
        return [types.TextContent(
            type="text",
            text=f"📊 Task Statistics:\n\n" + 
                 "\n".join(f"• {stat['status']}: {stat['count']} tasks (avg age: {stat['avg_age_hours']:.1f}h)" 
                          for stat in stats)
        )]
    
    async def _handle_create_task(self, arguments: Dict[str, Any]):
        """Create task and invalidate relevant caches."""
        result = await super()._handle_create_task(arguments)
        
        # Invalidate caches that depend on task data
        self._handle_list_tasks.invalidate_cache()
        self._handle_get_task_statistics.invalidate_cache()
        
        return result
```

### Real-time Features and Streaming

```python
# streaming/realtime.py
import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List
from datetime import datetime

class StreamingMCPServer(MCPTaskServer):
    """MCP server with streaming capabilities."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}
    
    async def _stream_large_dataset(self, query: str, batch_size: int = 100) -> AsyncGenerator[str, None]:
        """Stream large datasets in batches."""
        offset = 0
        
        while True:
            batch_query = f"{query} LIMIT {batch_size} OFFSET {offset}"
            batch = await self.db.execute_query(batch_query)
            
            if not batch:
                break
            
            # Yield batch as JSON
            yield json.dumps({
                'batch': offset // batch_size + 1,
                'data': batch,
                'has_more': len(batch) == batch_size
            }, default=str)
            
            offset += batch_size
            
            # Allow other operations to run
            await asyncio.sleep(0.01)
    
    @cached_tool(ttl=60)
    async def _handle_export_tasks(self, arguments: Dict[str, Any]):
        """Export large datasets with streaming."""
        format_type = arguments.get('format', 'json')
        
        if format_type == 'json':
            return await self._stream_tasks_json(arguments)
        elif format_type == 'csv':
            return await self._stream_tasks_csv(arguments)
        else:
            raise ValidationError('format', 'Supported formats: json, csv')
    
    async def _stream_tasks_json(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """Stream tasks as JSON."""
        status_filter = arguments.get('status')
        
        base_query = """
            SELECT t.*, 
                   COALESCE(ARRAY_AGG(c.name) FILTER (WHERE c.name IS NOT NULL), '{}') as categories
            FROM tasks t
            LEFT JOIN task_categories tc ON t.id = tc.task_id
            LEFT JOIN categories c ON tc.category_id = c.id
        """
        
        if status_filter:
            base_query += f" WHERE t.status = '{status_filter}'"
        
        base_query += " GROUP BY t.id ORDER BY t.created_at DESC"
        
        # Count total records
        count_query = base_query.replace("SELECT t.*, COALESCE(...", "SELECT COUNT(DISTINCT t.id)")
        total_count = await self.db.execute_query(count_query)
        total = total_count[0]['count'] if total_count else 0
        
        result = f"📁 Starting export of {total} tasks...\n\n"
        
        batch_count = 0
        async for batch_json in self._stream_large_dataset(base_query):
            batch_data = json.loads(batch_json)
            batch_count += 1
            
            result += f"📦 Batch {batch_data['batch']}: {len(batch_data['data'])} tasks\n"
            
            # For demo purposes, show first few records of first batch
            if batch_count == 1:
                first_few = batch_data['data'][:3]
                for task in first_few:
                    result += f"  • {task['title']} ({task['status']})\n"
                if len(batch_data['data']) > 3:
                    result += f"  • ... and {len(batch_data['data']) - 3} more tasks\n"
        
        result += f"\n✅ Export completed: {batch_count} batches, {total} total tasks"
        
        return [types.TextContent(type="text", text=result)]
```

This comprehensive section covers advanced MCP patterns including sophisticated error handling, performance optimization, caching strategies, and real-time features that make your MCP server production-ready and user-friendly.

## 🏆 Part 7: Best Practices and Production Considerations

### Security Best Practices Summary

#### **1. Input Security**
- ✅ Always use parameterized queries to prevent SQL injection
- ✅ Validate all inputs with JSON schemas before processing
- ✅ Sanitize HTML content to prevent XSS attacks
- ✅ Implement proper error handling without exposing internal details
- ❌ Never allow arbitrary SQL execution without validation

#### **2. Database Security**
- ✅ Use dedicated database users with minimal required permissions
- ✅ Enable SSL/TLS for database connections in production
- ✅ Implement connection pooling with reasonable limits
- ✅ Monitor database performance and query patterns
- ❌ Don't store sensitive data in plain text

#### **3. Process Security**
- ✅ Run MCP servers with non-root users
- ✅ Use environment variables for sensitive configuration
- ✅ Implement proper logging without logging sensitive data
- ✅ Set up monitoring and alerting for suspicious activity
- ❌ Don't hardcode credentials or secrets in code

### Performance Best Practices Summary

#### **1. Database Performance**
- ✅ Use connection pooling efficiently (2-20 connections typical)
- ✅ Implement proper indexing on commonly queried fields
- ✅ Cache frequently accessed data with appropriate TTL
- ✅ Monitor query performance and optimize slow queries
- ❌ Don't fetch large datasets without pagination

#### **2. MCP Protocol Performance**
- ✅ Implement proper async/await patterns throughout
- ✅ Use streaming for large data exports
- ✅ Implement intelligent caching strategies
- ✅ Monitor tool execution times and response sizes
- ❌ Don't block the event loop with synchronous operations

#### **3. Resource Management**
- ✅ Properly clean up database connections and resources
- ✅ Implement proper error recovery and retry logic
- ✅ Monitor memory usage and prevent memory leaks
- ✅ Use appropriate data structures for different use cases
- ❌ Don't keep connections open longer than necessary

### User Experience Best Practices

#### **1. Error Messages**
- ✅ Provide clear, actionable error messages
- ✅ Suggest alternatives when operations fail
- ✅ Use appropriate error severity levels
- ✅ Include context about what went wrong and how to fix it
- ❌ Don't expose technical details to end users

#### **2. Tool Design**
- ✅ Create tools with clear, descriptive names
- ✅ Provide comprehensive descriptions and examples
- ✅ Use intuitive parameter names and validation
- ✅ Implement consistent response formatting
- ❌ Don't create tools that are too complex or have unclear purposes

#### **3. Resource Management**
- ✅ Provide meaningful resource URIs and descriptions
- ✅ Structure data in a way that's easy for AI to understand
- ✅ Include metadata that helps with context understanding
- ✅ Keep resource responses appropriately sized
- ❌ Don't expose internal system details through resources

### Maintenance Best Practices

#### **1. Code Quality**
- ✅ Write comprehensive tests for all components
- ✅ Use type hints throughout the codebase
- ✅ Document all tools and resources thoroughly
- ✅ Implement proper logging and monitoring
- ❌ Don't skip error handling or edge case testing

#### **2. Monitoring and Observability**
- ✅ Track tool usage patterns and performance metrics
- ✅ Monitor database connection health and query performance
- ✅ Set up alerts for error rates and system health
- ✅ Implement structured logging for easier debugging
- ❌ Don't deploy without proper monitoring in place

#### **3. Deployment and Operations**
- ✅ Use infrastructure as code for reproducible deployments
- ✅ Implement proper backup and recovery procedures
- ✅ Have a rollback strategy for failed deployments
- ✅ Test deployments in staging environments first
- ❌ Don't make changes directly in production without testing

## 📊 Part 8: Complete Monitoring and Debugging Guide

### Advanced Logging and Observability

```python
# monitoring/logging.py
import logging
import structlog
import time
import traceback
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

class MCPLogger:
    """Advanced logging setup for MCP servers."""
    
    @staticmethod
    def setup_production_logging(log_level: str = "INFO"):
        """Configure structured logging for production."""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer() if log_level == "DEBUG" else structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Set root logger level
        logging.basicConfig(level=getattr(logging, log_level.upper()))
    
    @staticmethod
    def get_logger(name: str) -> structlog.BoundLogger:
        """Get a structured logger instance."""
        return structlog.get_logger(name)

class RequestTracker:
    """Track and log MCP requests with timing and context."""
    
    def __init__(self, logger: structlog.BoundLogger):
        self.logger = logger
        self.active_requests: Dict[str, Dict[str, Any]] = {}
    
    @asynccontextmanager
    async def track_request(self, request_type: str, tool_name: str, arguments: Dict[str, Any]):
        """Context manager to track request lifecycle."""
        request_id = f"{request_type}_{tool_name}_{int(time.time() * 1000)}"
        start_time = time.time()
        
        # Log request start
        self.logger.info(
            "Request started",
            request_id=request_id,
            request_type=request_type,
            tool_name=tool_name,
            arguments=arguments
        )
        
        # Track active request
        self.active_requests[request_id] = {
            'start_time': start_time,
            'tool_name': tool_name,
            'request_type': request_type
        }
        
        try:
            yield request_id
            
            # Log successful completion
            duration = time.time() - start_time
            self.logger.info(
                "Request completed",
                request_id=request_id,
                duration=duration,
                success=True
            )
            
        except Exception as e:
            # Log error
            duration = time.time() - start_time
            self.logger.error(
                "Request failed",
                request_id=request_id,
                duration=duration,
                error=str(e),
                error_type=type(e).__name__,
                traceback=traceback.format_exc()
            )
            raise
            
        finally:
            # Clean up tracking
            self.active_requests.pop(request_id, None)
    
    def get_active_requests(self) -> Dict[str, Dict[str, Any]]:
        """Get information about currently active requests."""
        current_time = time.time()
        return {
            req_id: {
                **req_info,
                'running_time': current_time - req_info['start_time']
            }
            for req_id, req_info in self.active_requests.items()
        }

# Usage in MCP server
class MonitoredMCPServer(MCPTaskServer):
    """MCP server with comprehensive monitoring."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = MCPLogger.get_logger(self.__class__.__name__)
        self.request_tracker = RequestTracker(self.logger)
        self.metrics = {
            'tool_calls': {},
            'errors': {},
            'performance': {}
        }
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]):
        """Enhanced tool call handling with monitoring."""
        async with self.request_tracker.track_request("tool_call", name, arguments) as request_id:
            # Update metrics
            self.metrics['tool_calls'][name] = self.metrics['tool_calls'].get(name, 0) + 1
            
            # Execute with performance monitoring
            start_time = time.time()
            try:
                result = await super().handle_call_tool(name, arguments)
                
                # Track performance
                duration = time.time() - start_time
                if name not in self.metrics['performance']:
                    self.metrics['performance'][name] = []
                self.metrics['performance'][name].append(duration)
                
                # Keep only last 100 measurements
                if len(self.metrics['performance'][name]) > 100:
                    self.metrics['performance'][name] = self.metrics['performance'][name][-100:]
                
        return result
                
    except Exception as e:
                # Track errors
                error_key = f"{name}:{type(e).__name__}"
                self.metrics['errors'][error_key] = self.metrics['errors'].get(error_key, 0) + 1
        raise
    
    async def get_health_metrics(self) -> Dict[str, Any]:
        """Get comprehensive health and performance metrics."""
        current_time = time.time()
        
        # Calculate performance statistics
        perf_stats = {}
        for tool_name, durations in self.metrics['performance'].items():
            if durations:
                perf_stats[tool_name] = {
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'call_count': len(durations)
                }
        
        # Database health check
        try:
            await self.db.execute_query("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return {
            'timestamp': current_time,
            'uptime': current_time - getattr(self, '_start_time', current_time),
            'database_status': db_status,
            'active_requests': self.request_tracker.get_active_requests(),
            'tool_call_counts': self.metrics['tool_calls'],
            'error_counts': self.metrics['errors'],
            'performance_stats': perf_stats,
            'memory_usage': self._get_memory_usage()
        }
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage information."""
        try:
            import psutil
            process = psutil.Process()
            return {
                'rss': process.memory_info().rss,
                'vms': process.memory_info().vms,
                'percent': process.memory_percent()
            }
        except ImportError:
            return {'error': 'psutil not available'}
```

### Health Check Implementation

```python
# Add this to your MCP server tools
types.Tool(
    name="health_check",
    description="Check server and database health with detailed metrics",
    inputSchema={
        "type": "object",
        "properties": {
            "include_metrics": {
                "type": "boolean",
                "description": "Include detailed performance metrics",
                "default": False
            }
        }
    }
),

async def _handle_health_check(self, arguments: Dict[str, Any]):
    """Comprehensive health check tool."""
    include_metrics = arguments.get('include_metrics', False)
    
    try:
        # Basic health checks
        health_status = await self.get_health_metrics()
        
        # Format response
        result = "🏥 **MCP Server Health Check**\n\n"
        
        # Database status
        db_icon = "✅" if health_status['database_status'] == "healthy" else "❌"
        result += f"{db_icon} **Database**: {health_status['database_status']}\n"
        
        # Active requests
        active_count = len(health_status['active_requests'])
        result += f"🔄 **Active Requests**: {active_count}\n"
        
        # Tool usage summary
        total_calls = sum(health_status['tool_call_counts'].values())
        result += f"📞 **Total Tool Calls**: {total_calls}\n"
        
        # Error summary
        total_errors = sum(health_status['error_counts'].values())
        error_rate = (total_errors / total_calls * 100) if total_calls > 0 else 0
        result += f"❌ **Error Rate**: {error_rate:.2f}% ({total_errors} errors)\n"
        
        # Uptime
        uptime_hours = health_status['uptime'] / 3600
        result += f"⏰ **Uptime**: {uptime_hours:.1f} hours\n"
        
        if include_metrics:
            result += "\n📊 **Performance Metrics**:\n"
            for tool_name, stats in health_status['performance_stats'].items():
                result += f"• **{tool_name}**: {stats['call_count']} calls, "
                result += f"avg {stats['avg_duration']:.3f}s\n"
        
        return [types.TextContent(type="text", text=result)]
        
        except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Health check failed: {str(e)}"
        )]
```

## 🚀 Part 9: Next Steps and Advanced Projects

### Extending Your MCP Server

Now that you have a solid foundation, here are ways to expand your MCP server:

#### **1. Add More Complex Tools**
```python
# Example: AI-powered task prioritization
types.Tool(
    name="ai_prioritize_tasks",
    description="Use AI to analyze and suggest task priorities based on content",
    inputSchema={
        "type": "object",
        "properties": {
            "criteria": {
                "type": "string",
                "description": "Prioritization criteria (urgency, importance, deadlines, etc.)"
            }
        }
    }
),

# Example: Advanced reporting
types.Tool(
    name="generate_productivity_report",
    description="Generate comprehensive productivity and performance reports",
    inputSchema={
        "type": "object",
        "properties": {
            "period": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
            "include_charts": {"type": "boolean", "default": False},
            "team_member": {"type": "string", "description": "Optional: specific team member"}
        }
    }
),
```

#### **2. Integration with External Services**
```python
# Example: Slack integration
async def _handle_notify_slack(self, arguments: Dict[str, Any]):
    """Send task notifications to Slack."""
    task_id = arguments["task_id"]
    channel = arguments.get("channel", "#general")
    
    task = await self.db.get_task_by_id(task_id)
    if not task:
        raise ValidationError("task_id", "Task not found")
    
    # Send to Slack (implement your Slack integration)
    message = f"📋 Task Update: {task['title']} is now {task['status']}"
    await self.slack_client.send_message(channel, message)
    
    return [types.TextContent(
        type="text", 
        text=f"✅ Notification sent to {channel}"
    )]

# Example: Email integration
async def _handle_send_task_reminder(self, arguments: Dict[str, Any]):
    """Send email reminders for overdue tasks."""
    email = arguments["email"]
    task_id = arguments["task_id"]
    
    task = await self.db.get_task_by_id(task_id)
    if not task:
        raise ValidationError("task_id", "Task not found")
    
    # Send email (implement your email service)
    await self.email_service.send_reminder(email, task)
    
    return [types.TextContent(
        type="text",
        text=f"📧 Reminder sent to {email}"
    )]
```

#### **3. Advanced Data Analytics**
```python
# Example: Predictive analytics
async def _handle_predict_completion_time(self, arguments: Dict[str, Any]):
    """Predict task completion time based on historical data."""
    task_id = arguments["task_id"]
    
    # Analyze historical patterns
    similar_tasks = await self.db.execute_query("""
        SELECT 
            EXTRACT(EPOCH FROM (completed_at - created_at))/3600 as completion_hours,
            priority,
            complexity_score
        FROM tasks 
        WHERE status = 'completed' 
        AND priority = (SELECT priority FROM tasks WHERE id = $1)
        ORDER BY created_at DESC
        LIMIT 50
    """, task_id)
    
    if not similar_tasks:
        return [types.TextContent(
            type="text",
            text="⚠️ Not enough historical data for prediction"
        )]
    
    # Simple prediction based on average
    avg_hours = sum(t['completion_hours'] for t in similar_tasks) / len(similar_tasks)
    
    return [types.TextContent(
        type="text",
        text=f"🔮 Predicted completion time: {avg_hours:.1f} hours\n"
             f"Based on {len(similar_tasks)} similar completed tasks"
    )]
```

### Building Different Types of MCP Servers

#### **1. CRM Server**
- Customer management tools
- Sales pipeline tracking
- Lead scoring and management
- Integration with email and calendar

#### **2. Inventory Management Server**
- Product catalog management
- Stock level monitoring
- Order processing
- Supplier management

#### **3. Analytics Server**
- Data visualization tools
- Report generation
- KPI tracking
- Real-time dashboard data

#### **4. DevOps Server**
- Deployment management
- Infrastructure monitoring
- Log analysis
- Performance metrics

### Advanced Implementation Patterns

#### **1. Plugin Architecture**
```python
# plugins/base.py
from abc import ABC, abstractmethod
from typing import List
import mcp.types as types

class MCPPlugin(ABC):
    """Base class for MCP server plugins."""
    
    @abstractmethod
    def get_tools(self) -> List[types.Tool]:
        """Return tools provided by this plugin."""
        pass
    
    @abstractmethod
    def get_resources(self) -> List[types.Resource]:
        """Return resources provided by this plugin."""
        pass
    
    @abstractmethod
    async def handle_tool_call(self, name: str, arguments: dict) -> List[types.TextContent]:
        """Handle tool calls for this plugin."""
        pass

# plugins/analytics_plugin.py
class AnalyticsPlugin(MCPPlugin):
    """Plugin for analytics and reporting features."""
    
    def get_tools(self) -> List[types.Tool]:
        return [
            types.Tool(
                name="generate_report",
                description="Generate various types of reports",
                inputSchema={
    "type": "object",
    "properties": {
                        "report_type": {
                            "type": "string",
                            "enum": ["productivity", "performance", "summary"]
                        },
                        "date_range": {"type": "string"}
                    }
                }
            )
        ]
    
    async def handle_tool_call(self, name: str, arguments: dict):
        if name == "generate_report":
            return await self._generate_report(arguments)
        
        raise ValueError(f"Unknown tool: {name}")

# Usage in main server
class PluginMCPServer(MCPTaskServer):
    """MCP server with plugin support."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugins = {
            'analytics': AnalyticsPlugin(),
            'notifications': NotificationsPlugin(),
            'integrations': IntegrationsPlugin()
        }
    
    async def handle_list_tools(self):
        """Combine tools from all plugins."""
        tools = await super().handle_list_tools()
        
        for plugin in self.plugins.values():
            tools.extend(plugin.get_tools())
        
        return tools
```

#### **2. Multi-Database Support**
```python
# databases/factory.py
from abc import ABC, abstractmethod

class DatabaseAdapter(ABC):
    """Abstract database adapter."""
    
    @abstractmethod
    async def execute_query(self, query: str, *args):
        pass

class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL implementation."""
    
    async def execute_query(self, query: str, *args):
        # PostgreSQL specific implementation
        pass

class MongoAdapter(DatabaseAdapter):
    """MongoDB implementation."""
    
    async def execute_query(self, query: str, *args):
        # MongoDB specific implementation (translate SQL-like to MongoDB)
        pass

class DatabaseFactory:
    """Factory for creating database adapters."""
    
    @staticmethod
    def create_adapter(database_url: str) -> DatabaseAdapter:
        if database_url.startswith('postgresql://'):
            return PostgreSQLAdapter(database_url)
        elif database_url.startswith('mongodb://'):
            return MongoAdapter(database_url)
        else:
            raise ValueError(f"Unsupported database: {database_url}")
```

### Testing Advanced Features

#### **1. Load Testing**
```python
# tests/test_load.py
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

async def simulate_concurrent_requests(num_requests: int = 100):
    """Simulate high concurrent load."""
    
    async def make_request():
        # Simulate MCP tool call
        start_time = time.time()
        await asyncio.sleep(0.1)  # Simulate processing time
        return time.time() - start_time
    
    # Execute requests concurrently
    tasks = [make_request() for _ in range(num_requests)]
    durations = await asyncio.gather(*tasks)
    
    # Analyze results
    avg_duration = sum(durations) / len(durations)
    max_duration = max(durations)
    
    print(f"Processed {num_requests} requests")
    print(f"Average duration: {avg_duration:.3f}s")
    print(f"Maximum duration: {max_duration:.3f}s")
    
    assert avg_duration < 0.5  # Should complete quickly
    assert max_duration < 2.0  # No request should take too long
```

#### **2. Integration Testing**
```python
# tests/test_integration.py
async def test_full_workflow():
    """Test complete task lifecycle."""
    server = MCPTaskServer(test_db_url)
    await server.start()
    
    try:
        # Create task
        create_result = await server.handle_call_tool("create_task", {
            "title": "Integration Test Task",
            "priority": "high"
        })
        assert "created successfully" in create_result[0].text.lower()
        
        # List tasks to verify creation
        list_result = await server.handle_call_tool("list_tasks", {})
        assert "Integration Test Task" in list_result[0].text
        
        # Update task status
        update_result = await server.handle_call_tool("update_task_status", {
            "task_id": 1,  # Assuming first task
            "status": "completed"
        })
        assert "updated" in update_result[0].text.lower()
        
        # Verify status change
        list_completed = await server.handle_call_tool("list_tasks", {
            "status": "completed"
        })
        assert "Integration Test Task" in list_completed[0].text
        
    finally:
        await server.stop()
```

## 🏆 Part 10: Complete Summary and Best Practices

### What You've Learned

By completing this tutorial, you now understand:

1. **MCP Architecture** - How AI assistants communicate with external systems through standardized protocols
2. **Protocol Implementation** - Building robust servers that handle tools, resources, and error scenarios
3. **Database Integration** - Efficient async database operations with connection pooling and optimization
4. **Production Deployment** - Containerization, monitoring, and scaling strategies
5. **Advanced Patterns** - Error handling, caching, streaming, and performance optimization
6. **Testing Strategies** - From unit tests to load testing and integration validation

### Key Differences: MCP vs Traditional Servers

| **Aspect** | **Traditional API Server** | **MCP Server** |
|------------|------------------------------|----------------|
| **Discovery** | Manual API documentation | Automatic tool/resource discovery |
| **Integration** | Custom client development | Native AI assistant support |
| **Communication** | HTTP requests/responses | JSON-RPC over stdin/stdout |
| **Type Safety** | Optional (OpenAPI) | Built-in JSON schema validation |
| **Error Handling** | HTTP status codes | Rich, contextual error responses |
| **Real-time** | WebSockets/SSE | Protocol-native streaming |

### Production Readiness Checklist

#### **Security** ✅
- [ ] Input validation with JSON schemas
- [ ] Parameterized database queries
- [ ] Error handling without information leakage
- [ ] Environment-based configuration management
- [ ] Non-root process execution

#### **Performance** ✅
- [ ] Database connection pooling (2-20 connections)
- [ ] Intelligent caching with TTL
- [ ] Async/await throughout the codebase
- [ ] Query optimization and indexing
- [ ] Resource cleanup and memory management

#### **Reliability** ✅
- [ ] Comprehensive error recovery
- [ ] Health check endpoints
- [ ] Structured logging and monitoring
- [ ] Graceful shutdown procedures
- [ ] Retry logic for transient failures

#### **Observability** ✅
- [ ] Request/response logging
- [ ] Performance metrics collection
- [ ] Error rate monitoring
- [ ] Database health tracking
- [ ] Memory and CPU usage alerts

#### **Testing** ✅
- [ ] Unit tests for all components
- [ ] Integration tests for workflows
- [ ] Load testing for performance
- [ ] End-to-end testing with Claude
- [ ] Error scenario validation

### Advanced Implementation Checklist

#### **Scalability** 🚀
- [ ] Horizontal scaling support
- [ ] Load balancing configuration
- [ ] Database read replicas
- [ ] Caching layers (Redis/Memcached)
- [ ] Container orchestration (Kubernetes)

#### **Enterprise Features** 🏢
- [ ] Authentication and authorization
- [ ] Multi-tenancy support
- [ ] Audit logging
- [ ] Rate limiting
- [ ] SLA monitoring

#### **Developer Experience** 👨‍💻
- [ ] Interactive testing tools (MCP Inspector)
- [ ] Comprehensive documentation
- [ ] Plugin architecture
- [ ] Configuration management
- [ ] Development environment setup

### Next Steps and Project Ideas

#### **Beginner Projects** 📚
1. **Personal Task Manager** - Extend the tutorial example with priorities, deadlines, and categories
2. **Note-Taking System** - Create, organize, and search personal notes
3. **Simple CRM** - Contact management with basic interaction tracking
4. **Expense Tracker** - Personal finance management with categories and reports

#### **Intermediate Projects** 🛠️
1. **Team Project Manager** - Multi-user task management with collaboration features
2. **Content Management System** - Blog/article management with publishing workflows
3. **Inventory System** - Product catalog with stock management and supplier integration
4. **Customer Support System** - Ticket management with status tracking and escalation

#### **Advanced Projects** 🚀
1. **Analytics Platform** - Real-time data processing with dashboard generation
2. **DevOps Automation** - Deployment pipelines, monitoring, and incident management
3. **E-commerce Backend** - Order processing, payment integration, and fulfillment
4. **Multi-Database Federation** - Unified interface across different data sources

#### **Innovation Projects** 💡
1. **AI-Enhanced MCP** - Integrate GPT/Claude for intelligent task suggestions
2. **Real-time Collaboration** - WebSocket-based live updates and notifications
3. **Multi-Modal Interface** - Handle images, documents, and rich media
4. **Blockchain Integration** - Decentralized data storage and smart contracts

### Architecture Patterns to Explore

#### **Event-Driven Architecture**
```python
# Example: Event sourcing with MCP
class EventSourcedMCPServer(MCPTaskServer):
    """MCP server with event sourcing capabilities."""
    
    async def _handle_create_task(self, arguments):
        # Create event
        event = TaskCreatedEvent(
            task_id=generate_id(),
            title=arguments['title'],
            timestamp=datetime.now()
        )
        
        # Store event
        await self.event_store.append(event)
        
        # Apply event to current state
        task = await self.apply_event(event)
        
        return [types.TextContent(
            type="text",
            text=f"✅ Task created with event sourcing: {task['title']}"
        )]
```

#### **CQRS (Command Query Responsibility Segregation)**
```python
# Separate read and write models
class CQRSMCPServer(MCPTaskServer):
    """MCP server with CQRS pattern."""
    
    def __init__(self, write_db_url: str, read_db_url: str):
        self.write_db = TaskDatabase(write_db_url)
        self.read_db = TaskQueryDatabase(read_db_url)
        super().__init__(write_db_url)
    
    async def _handle_create_task(self, arguments):
        # Command: use write database
        result = await self.write_db.create_task(**arguments)
        
        # Async: update read model
        await self.update_read_model(result)
        
        return [types.TextContent(type="text", text="Task created")]
    
    async def _handle_list_tasks(self, arguments):
        # Query: use optimized read database
        tasks = await self.read_db.get_tasks_optimized(**arguments)
        return self.format_task_list(tasks)
```

### Community and Resources

#### **Official Resources** 📖
- [MCP Specification](https://spec.modelcontextprotocol.io/) - Official protocol specification
- [MCP SDK Documentation](https://docs.modelcontextprotocol.io/) - Implementation guides and APIs
- [Example Servers](https://github.com/modelcontextprotocol/servers) - Community-maintained examples

#### **Development Tools** 🔧
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector) - Interactive testing and debugging
- [MCP CLI](https://github.com/modelcontextprotocol/cli) - Command-line tools for development
- [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk) - Alternative implementation

#### **Community** 🤝
- [GitHub Discussions](https://github.com/modelcontextprotocol/spec/discussions) - Technical discussions and Q&A
- [Discord Server](https://discord.gg/modelcontextprotocol) - Real-time community chat
- [Reddit Community](https://reddit.com/r/ModelContextProtocol) - Share projects and get feedback

#### **Contributing** 🌟
Ways to contribute to the MCP ecosystem:
1. **Build Example Servers** - Share implementations for different domains
2. **Improve Documentation** - Help make MCP more accessible to developers
3. **Report Issues** - Help improve the protocol and implementations
4. **Share Best Practices** - Document patterns and solutions you discover

### Final Thoughts

MCP represents a fundamental shift in how AI assistants interact with external systems. By building robust, well-designed MCP servers, you're not just creating useful tools – you're contributing to the future of AI-human collaboration.

The patterns and practices covered in this tutorial will serve you well as you build increasingly sophisticated MCP servers. Remember:

- **Start simple** and iterate based on real usage
- **Prioritize security and reliability** from day one
- **Monitor and optimize** continuously
- **Share your learnings** with the community

**Happy building, and welcome to the MCP community!** 🎉

---

*This tutorial covered everything from basic MCP concepts to production deployment. As the protocol evolves, make sure to check the [official documentation](https://docs.modelcontextprotocol.io/) for the latest features and best practices.*
