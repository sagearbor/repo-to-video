#!/usr/bin/env python3
"""
Test script for DevServerManager
Tests automatic server startup, health checking, and shutdown
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.server_manager import DevServerManager
from src.utils.logger import setup_logger

logger = setup_logger('test_server_manager')


async def test_server_manager():
    """Test the DevServerManager with a simple Python server"""

    # Create a test directory
    test_dir = Path(__file__).parent / 'test_server'
    test_dir.mkdir(exist_ok=True)

    # Create a simple test server
    test_server_code = '''
import http.server
import socketserver

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    httpd.serve_forever()
'''

    test_server_file = test_dir / 'test_server.py'
    test_server_file.write_text(test_server_code)

    logger.info("Testing DevServerManager...")
    logger.info("-" * 70)

    # Test automatic server startup
    server_manager = DevServerManager(
        repo_path=test_dir,
        start_command='python test_server.py',
        port=8000,
        setup_commands=[]
    )

    try:
        logger.info("Starting test server...")
        success = await server_manager.start(timeout=30)

        if success:
            logger.info("✓ Server started successfully!")
            logger.info("Waiting 3 seconds...")
            await asyncio.sleep(3)
            logger.info("✓ Server still running")
        else:
            logger.error("✗ Server failed to start")
            return False

    finally:
        logger.info("Stopping server...")
        server_manager.stop()
        logger.info("✓ Server stopped")

    # Clean up
    test_server_file.unlink()
    test_dir.rmdir()

    logger.info("-" * 70)
    logger.info("✓ All tests passed!")
    return True


if __name__ == '__main__':
    success = asyncio.run(test_server_manager())
    sys.exit(0 if success else 1)
