"""
Database connection and query management for the MCP Task Server.
"""

import asyncio
import asyncpg
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TaskDatabase:
    """PostgreSQL database interface for task management."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Establish connection pool to PostgreSQL."""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Disconnected from PostgreSQL database")
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dictionaries."""
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            try:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                logger.error(f"Query: {query}")
                logger.error(f"Args: {args}")
                raise
    
    async def execute_command(self, command: str, *args) -> str:
        """Execute an INSERT/UPDATE/DELETE command and return status."""
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as conn:
            try:
                result = await conn.execute(command, *args)
                logger.info(f"Command executed successfully: {result}")
                return result
            except Exception as e:
                logger.error(f"Command execution failed: {e}")
                logger.error(f"Command: {command}")
                logger.error(f"Args: {args}")
                raise
    
    # Task Management Methods
    
    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Retrieve all tasks with their categories."""
        query = """
        SELECT 
            t.*,
            COALESCE(
                ARRAY_AGG(c.name) FILTER (WHERE c.name IS NOT NULL), 
                '{}'
            ) as categories
        FROM tasks t
        LEFT JOIN task_categories tc ON t.id = tc.task_id
        LEFT JOIN categories c ON tc.category_id = c.id
        GROUP BY t.id
        ORDER BY t.created_at DESC
        """
        return await self.execute_query(query)
    
    async def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific task by ID."""
        query = """
        SELECT 
            t.*,
            COALESCE(
                ARRAY_AGG(c.name) FILTER (WHERE c.name IS NOT NULL), 
                '{}'
            ) as categories
        FROM tasks t
        LEFT JOIN task_categories tc ON t.id = tc.task_id
        LEFT JOIN categories c ON tc.category_id = c.id
        WHERE t.id = $1
        GROUP BY t.id
        """
        results = await self.execute_query(query, task_id)
        return results[0] if results else None
    
    async def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Retrieve tasks filtered by status."""
        query = """
        SELECT 
            t.*,
            COALESCE(
                ARRAY_AGG(c.name) FILTER (WHERE c.name IS NOT NULL), 
                '{}'
            ) as categories
        FROM tasks t
        LEFT JOIN task_categories tc ON t.id = tc.task_id
        LEFT JOIN categories c ON tc.category_id = c.id
        WHERE t.status = $1
        GROUP BY t.id
        ORDER BY t.priority DESC, t.created_at DESC
        """
        return await self.execute_query(query, status)
    
    async def create_task(self, title: str, description: str = None, 
                         priority: str = 'medium', assigned_to: str = None,
                         due_date: datetime = None, tags: List[str] = None) -> Dict[str, Any]:
        """Create a new task."""
        query = """
        INSERT INTO tasks (title, description, priority, assigned_to, due_date, tags)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING *
        """
        tags = tags or []
        results = await self.execute_query(
            query, title, description, priority, assigned_to, due_date, tags
        )
        return results[0] if results else None
    
    async def update_task_status(self, task_id: int, status: str) -> bool:
        """Update the status of a task."""
        command = "UPDATE tasks SET status = $2 WHERE id = $1"
        result = await self.execute_command(command, task_id, status)
        return "UPDATE 1" in result
    
    async def delete_task(self, task_id: int) -> bool:
        """Delete a task."""
        command = "DELETE FROM tasks WHERE id = $1"
        result = await self.execute_command(command, task_id)
        return "DELETE 1" in result
    
    async def get_task_comments(self, task_id: int) -> List[Dict[str, Any]]:
        """Get all comments for a specific task."""
        query = """
        SELECT * FROM task_comments 
        WHERE task_id = $1 
        ORDER BY created_at ASC
        """
        return await self.execute_query(query, task_id)
    
    async def add_task_comment(self, task_id: int, comment: str, author: str = None) -> Dict[str, Any]:
        """Add a comment to a task."""
        query = """
        INSERT INTO task_comments (task_id, comment, author)
        VALUES ($1, $2, $3)
        RETURNING *
        """
        results = await self.execute_query(query, task_id, comment, author)
        return results[0] if results else None
    
    async def get_all_categories(self) -> List[Dict[str, Any]]:
        """Retrieve all categories."""
        query = "SELECT * FROM categories ORDER BY name"
        return await self.execute_query(query)
    
    async def get_database_schema(self) -> Dict[str, Any]:
        """Get database schema information for the MCP client."""
        schema_query = """
        SELECT 
            table_name,
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        ORDER BY table_name, ordinal_position
        """
        
        columns = await self.execute_query(schema_query)
        
        # Group columns by table
        schema = {}
        for col in columns:
            table = col['table_name']
            if table not in schema:
                schema[table] = []
            schema[table].append({
                'name': col['column_name'],
                'type': col['data_type'],
                'nullable': col['is_nullable'] == 'YES',
                'default': col['column_default']
            })
        
        return schema
