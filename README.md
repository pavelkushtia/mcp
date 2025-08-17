# MCP Task Management Server

A comprehensive example of building a custom **Model Context Protocol (MCP)** server with PostgreSQL backend. This project demonstrates how to create an MCP server from scratch that provides task management capabilities to AI assistants.

## 🚀 What is MCP?

The **Model Context Protocol (MCP)** is an open standard that enables AI assistants to securely connect to external data sources and tools. Think of it as a bridge between AI models and your applications, databases, or services.

### Key Concepts:
- **MCP Server** - Your custom server that exposes data/tools (this project)
- **MCP Client** - The AI assistant that connects to your server
- **Resources** - Data that can be read (like database records)
- **Tools** - Actions that can be performed (like database queries)
- **Protocol** - JSON-RPC based communication

## 🏗️ Architecture

```
AI Assistant (Claude, etc.)  ←→  MCP Client  ←→  MCP Server  ←→  PostgreSQL
                                    ↑                ↑              ↑
                               JSON-RPC        Your Custom       Database
                               Protocol           Server
```

## 📋 Features

This MCP server provides comprehensive task management capabilities:

### 🛠️ Tools Available:
- **list_tasks** - List all tasks, optionally filtered by status
- **get_task** - Get details of a specific task by ID
- **create_task** - Create a new task
- **update_task_status** - Update the status of a task
- **delete_task** - Delete a task
- **add_task_comment** - Add a comment to a task
- **get_task_comments** - Get all comments for a task
- **list_categories** - List all available task categories
- **execute_query** - Execute read-only SQL queries
- **get_schema** - Get database schema information

### 📊 Resources Available:
- **task://all** - Complete list of all tasks
- **task://pending** - Pending tasks
- **task://in_progress** - Tasks in progress
- **task://completed** - Completed tasks
- **schema://database** - Database schema information

### 🗄️ Database Schema:
- **tasks** - Main tasks table with status, priority, assignments
- **categories** - Task categories for organization
- **task_categories** - Many-to-many relationship between tasks and categories
- **task_comments** - Comments system for tasks

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- Node.js 18+ (for MCP Inspector)

### 1. Clone and Setup
```bash
git clone <your-repo>
cd mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start PostgreSQL Database
```bash
# Start the database
sudo docker-compose up -d

# Check if it's running
sudo docker-compose ps
```

### 3. Test Database Connection
```bash
source venv/bin/activate
PYTHONPATH=/home/sanzad/git/mcp python tests/test_database.py
```

### 4. Test MCP Server with Inspector
```bash
# Install MCP Inspector
sudo npm install -g @modelcontextprotocol/inspector

# Test the server
npx @modelcontextprotocol/inspector python main.py
```

This will open a web interface where you can:
- View available tools and resources
- Test tool calls interactively
- Inspect server responses
- Debug your MCP implementation

## 🔧 Configuration

### Environment Variables
Create a `.env` file (copy from `.env.example`):
```bash
# Database Configuration
DATABASE_URL=postgresql://mcp_user:mcp_password@localhost:5432/mcp_tasks
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mcp_tasks
DB_USER=mcp_user
DB_PASSWORD=mcp_password

# Server Configuration
LOG_LEVEL=INFO
```

### Claude Desktop Integration
To use with Claude Desktop, add to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mcp-task-server": {
      "command": "python",
      "args": ["/path/to/your/mcp/main.py"],
      "env": {
        "DATABASE_URL": "postgresql://mcp_user:mcp_password@localhost:5432/mcp_tasks"
      }
    }
  }
}
```

## 💡 How It Works

### 1. Server Architecture
```python
# Main components:
src/
├── database.py      # PostgreSQL connection and queries
├── mcp_server.py    # MCP protocol implementation
└── __init__.py

main.py              # Entry point
```

### 2. MCP Protocol Flow
1. **Client connects** to server via stdio/transport
2. **Server advertises** available tools and resources
3. **Client calls tools** with JSON-RPC messages
4. **Server executes** database operations
5. **Server returns** formatted results

### 3. Database Operations
```python
# Example: Creating a task
async def create_task(self, title: str, description: str = None, 
                     priority: str = 'medium', assigned_to: str = None,
                     due_date: datetime = None, tags: List[str] = None):
    query = """
    INSERT INTO tasks (title, description, priority, assigned_to, due_date, tags)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING *
    """
    results = await self.execute_query(query, title, description, priority, assigned_to, due_date, tags)
    return results[0] if results else None
```

## 🧪 Testing

### Database Tests
```bash
source venv/bin/activate
PYTHONPATH=/home/sanzad/git/mcp python tests/test_database.py
```

### MCP Server Tests
```bash
# Interactive testing with MCP Inspector
npx @modelcontextprotocol/inspector python main.py

# Manual testing with curl (if server runs on HTTP)
curl -X POST http://localhost:8000/mcp \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}'
```

## 📚 Sample Usage

Once connected to an AI assistant, you can:

### Task Management
- "Show me all pending tasks"
- "Create a new task called 'Review documentation' with high priority"
- "Update task 5 status to completed"
- "Add a comment to task 3: 'Made good progress today'"

### Data Analysis
- "Show me tasks grouped by status"
- "Which tasks are overdue?"
- "Run a query to find all high-priority tasks assigned to 'developer'"

### Schema Exploration
- "What tables are in the database?"
- "Show me the structure of the tasks table"
- "What categories are available?"

## 🔒 Security Features

- **Read-only queries** - Only SELECT statements allowed in execute_query
- **Parameterized queries** - Protection against SQL injection
- **Connection pooling** - Efficient database connections
- **Input validation** - JSON schema validation for all inputs

## 🚀 Extending the Server

### Adding New Tools
```python
# In mcp_server.py, add to list_tools():
types.Tool(
    name="my_custom_tool",
    description="Description of what it does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    }
)

# Add handler in handle_call_tool():
elif name == "my_custom_tool":
    return await self._handle_my_custom_tool(arguments)
```

### Adding New Resources
```python
# Add to list_resources():
types.Resource(
    uri="my_resource://data",
    name="My Data",
    description="Custom data resource",
    mimeType="application/json"
)

# Handle in read_resource():
elif uri == "my_resource://data":
    data = await self.db.get_my_data()
    return json.dumps(data, default=str, indent=2)
```

## 🏆 Best Practices

1. **Error Handling** - Always handle database errors gracefully
2. **Logging** - Use structured logging for debugging
3. **Validation** - Validate all inputs with JSON schemas
4. **Documentation** - Document all tools and resources clearly
5. **Testing** - Write comprehensive tests for all functionality
6. **Security** - Never allow arbitrary SQL execution
7. **Performance** - Use connection pooling and efficient queries

## 🤝 Contributing

This is a learning project! Feel free to:
- Add new features
- Improve error handling
- Add more comprehensive tests
- Enhance documentation
- Create additional MCP servers

## 📖 Resources

- [MCP Official Documentation](https://modelcontextprotocol.io)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)

## 📄 License

Apache License 2.0 - See LICENSE file for details.

---

Built with ❤️ as a learning project to understand MCP server development.