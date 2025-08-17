#!/usr/bin/env python3
"""
MCP Task Server - Main Entry Point

This is the main entry point for the MCP Task Management Server.
It sets up the database connection and starts the MCP server.

Usage:
    python main.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
    DB_HOST: Database host (default: localhost)
    DB_PORT: Database port (default: 5432)
    DB_NAME: Database name (default: mcp_tasks)
    DB_USER: Database user (default: mcp_user)
    DB_PASSWORD: Database password
"""

import asyncio
import os
import sys
import logging
from dotenv import load_dotenv

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.mcp_server import MCPTaskServer

# Load environment variables
load_dotenv()

def get_database_url() -> str:
    """Get database URL from environment variables."""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        return database_url
    
    # Build URL from individual components
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    name = os.getenv('DB_NAME', 'mcp_tasks')
    user = os.getenv('DB_USER', 'mcp_user')
    password = os.getenv('DB_PASSWORD', 'mcp_password')
    
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"

async def main():
    """Main entry point for the MCP server."""
    # Set up logging
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get database configuration
        database_url = get_database_url()
        logger.info(f"Starting MCP Task Server with database: {database_url.split('@')[1] if '@' in database_url else 'unknown'}")
        
        # Create and run server
        server = MCPTaskServer(database_url)
        await server.run()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
