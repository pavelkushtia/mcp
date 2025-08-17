"""
Test script for the MCP Task Server database functionality.

This script tests the database connection and basic operations
without requiring the full MCP protocol setup.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from src.database import TaskDatabase

async def test_database():
    """Test database functionality."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Database connection
    database_url = "postgresql://mcp_user:mcp_password@localhost:5432/mcp_tasks"
    db = TaskDatabase(database_url)
    
    try:
        # Connect to database
        logger.info("Connecting to database...")
        await db.connect()
        logger.info("Connected successfully!")
        
        # Test schema retrieval
        logger.info("Testing schema retrieval...")
        schema = await db.get_database_schema()
        logger.info(f"Found {len(schema)} tables: {list(schema.keys())}")
        
        # Test task operations
        logger.info("Testing task operations...")
        
        # List all tasks
        tasks = await db.get_all_tasks()
        logger.info(f"Found {len(tasks)} existing tasks")
        
        # Create a test task
        new_task = await db.create_task(
            title="Test Task from Python",
            description="This is a test task created by the test script",
            priority="high",
            assigned_to="test_user",
            tags=["test", "python", "mcp"]
        )
        
        if new_task:
            task_id = new_task['id']
            logger.info(f"Created test task with ID: {task_id}")
            
            # Get the task details
            task_details = await db.get_task_by_id(task_id)
            logger.info(f"Retrieved task: {task_details['title']}")
            
            # Add a comment
            comment = await db.add_task_comment(
                task_id, 
                "This is a test comment", 
                "test_user"
            )
            logger.info(f"Added comment: {comment['comment']}")
            
            # Get comments
            comments = await db.get_task_comments(task_id)
            logger.info(f"Task has {len(comments)} comments")
            
            # Update task status
            success = await db.update_task_status(task_id, "completed")
            logger.info(f"Updated task status: {'success' if success else 'failed'}")
            
            # Test status filtering
            completed_tasks = await db.get_tasks_by_status("completed")
            logger.info(f"Found {len(completed_tasks)} completed tasks")
            
            # Clean up - delete the test task
            deleted = await db.delete_task(task_id)
            logger.info(f"Deleted test task: {'success' if deleted else 'failed'}")
        
        # Test categories
        categories = await db.get_all_categories()
        logger.info(f"Found {len(categories)} categories")
        
        logger.info("All database tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        raise
    finally:
        await db.disconnect()
        logger.info("Disconnected from database")

if __name__ == "__main__":
    asyncio.run(test_database())
