"""
Server management utilities for automatic dev server startup and health checking
"""
import subprocess
import asyncio
import time
import socket
from pathlib import Path
from typing import Optional, Tuple
import requests
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DevServerManager:
    """Manages development server lifecycle with health checking"""

    def __init__(self, repo_path: Path, start_command: str, port: int, setup_commands: list = None):
        """
        Initialize server manager

        Args:
            repo_path: Path to repository
            start_command: Command to start the server
            port: Port the server listens on
            setup_commands: Optional list of setup commands to run first
        """
        self.repo_path = repo_path
        self.start_command = start_command
        self.port = port
        self.setup_commands = setup_commands or []
        self.process: Optional[subprocess.Popen] = None

    async def start(self, timeout: int = 120) -> bool:
        """
        Start the dev server and wait for it to be ready

        Args:
            timeout: Maximum time to wait for server to be ready (seconds)

        Returns:
            True if server started successfully, False otherwise
        """
        try:
            # Run setup commands if provided
            if self.setup_commands:
                logger.info("Running setup commands...")
                for cmd in self.setup_commands:
                    logger.info(f"  Executing: {cmd}")
                    result = await asyncio.to_thread(
                        subprocess.run,
                        cmd,
                        shell=True,
                        cwd=str(self.repo_path),
                        capture_output=True,
                        text=True
                    )
                    if result.returncode != 0:
                        logger.warning(f"Setup command failed (continuing anyway): {cmd}")
                        logger.warning(f"  Error: {result.stderr}")

            # Start the dev server
            logger.info(f"Starting dev server: {self.start_command}")
            logger.info(f"  Working directory: {self.repo_path}")
            logger.info(f"  Expected port: {self.port}")

            self.process = subprocess.Popen(
                self.start_command,
                shell=True,
                cwd=str(self.repo_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line buffered
                preexec_fn=None  # Don't change process group on Windows
            )

            # Wait for server to be ready
            logger.info("Waiting for server to be ready...")
            start_time = time.time()

            while time.time() - start_time < timeout:
                if self.process.poll() is not None:
                    # Process exited
                    stdout, stderr = self.process.communicate()
                    logger.error(f"Server process exited unexpectedly")
                    logger.error(f"  stdout: {stdout}")
                    logger.error(f"  stderr: {stderr}")
                    return False

                if await self._check_health():
                    elapsed = time.time() - start_time
                    logger.info(f"✓ Server is ready! (took {elapsed:.1f}s)")
                    return True

                await asyncio.sleep(1)

            logger.error(f"Server did not become ready within {timeout}s")
            return False

        except Exception as e:
            logger.error(f"Failed to start server: {e}", exc_info=True)
            return False

    async def _check_health(self) -> bool:
        """
        Check if server is responding to HTTP requests

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            # First check if port is open
            if not self._is_port_open():
                return False

            # Then try HTTP request
            url = f"http://localhost:{self.port}"
            response = await asyncio.to_thread(
                requests.get,
                url,
                timeout=2,
                allow_redirects=True
            )
            # Accept any response (200, 404, etc.) - server is running
            return True

        except requests.exceptions.ConnectionError:
            # Port open but server not ready
            return False
        except requests.exceptions.Timeout:
            # Server slow to respond
            return False
        except Exception:
            # Other errors - server not ready
            return False

    def _is_port_open(self) -> bool:
        """
        Check if port is open using socket

        Returns:
            True if port is open, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('localhost', self.port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def stop(self):
        """Stop the dev server"""
        if self.process:
            logger.info("Stopping dev server...")
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                    logger.info("✓ Server stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning("Server didn't stop gracefully, killing...")
                    self.process.kill()
                    self.process.wait()
                    logger.info("✓ Server killed")
            except Exception as e:
                logger.error(f"Error stopping server: {e}")
            finally:
                self.process = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - always stop server"""
        self.stop()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - always stop server"""
        self.stop()
