"""
File system utilities
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


def read_file(file_path: str | Path) -> Optional[str]:
    """
    Read a text file

    Args:
        file_path: Path to the file

    Returns:
        File contents or None if file doesn't exist
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def write_file(file_path: str | Path, content: str):
    """
    Write content to a text file

    Args:
        file_path: Path to the file
        content: Content to write
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def read_json(file_path: str | Path) -> Optional[Dict[str, Any]]:
    """
    Read a JSON file

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data or None if file doesn't exist
    """
    content = read_file(file_path)
    if content:
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from {file_path}: {e}")
    return None


def write_json(file_path: str | Path, data: Dict[str, Any], indent: int = 2):
    """
    Write data to a JSON file

    Args:
        file_path: Path to the JSON file
        data: Data to write
        indent: JSON indentation
    """
    content = json.dumps(data, indent=indent)
    write_file(file_path, content)


def ensure_dir(dir_path: str | Path) -> Path:
    """
    Ensure a directory exists

    Args:
        dir_path: Path to the directory

    Returns:
        Path object
    """
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def file_exists(file_path: str | Path) -> bool:
    """
    Check if a file exists

    Args:
        file_path: Path to the file

    Returns:
        True if file exists
    """
    return Path(file_path).exists()


def get_file_extension(file_path: str | Path) -> str:
    """
    Get file extension

    Args:
        file_path: Path to the file

    Returns:
        File extension (without dot)
    """
    return Path(file_path).suffix.lstrip('.')
