"""
Git repository utilities
"""
import os
import re
from pathlib import Path
from typing import Optional
import git
from git import Repo
from .logger import get_logger

logger = get_logger(__name__)


def get_repo_name(github_url: str) -> str:
    """
    Extract repository name from GitHub URL

    Args:
        github_url: GitHub repository URL

    Returns:
        Repository name

    Examples:
        >>> get_repo_name("https://github.com/user/repo-name")
        'repo-name'
        >>> get_repo_name("https://github.com/user/repo-name.git")
        'repo-name'
    """
    # Remove .git suffix if present
    url = github_url.rstrip('/')
    if url.endswith('.git'):
        url = url[:-4]

    # Extract repo name
    match = re.search(r'/([^/]+)$', url)
    if match:
        return match.group(1)

    raise ValueError(f"Could not extract repository name from URL: {github_url}")


def clone_repository(github_url: str, target_dir: Optional[Path] = None) -> Path:
    """
    Clone a GitHub repository

    Args:
        github_url: GitHub repository URL
        target_dir: Target directory (if None, uses temp_repos/<repo_name>)

    Returns:
        Path to cloned repository
    """
    from ..config import config

    repo_name = get_repo_name(github_url)

    if target_dir is None:
        target_dir = config.paths.temp_repos_dir / repo_name

    # If directory already exists, assume it's already cloned
    if target_dir.exists():
        logger.info(f"Repository already exists at {target_dir}")
        return target_dir

    logger.info(f"Cloning {github_url} to {target_dir}...")

    try:
        Repo.clone_from(github_url, target_dir)
        logger.info(f"Successfully cloned repository to {target_dir}")
        return target_dir
    except git.GitCommandError as e:
        logger.error(f"Failed to clone repository: {e}")
        raise


def is_git_repo(path: Path) -> bool:
    """
    Check if a directory is a git repository

    Args:
        path: Directory path

    Returns:
        True if directory is a git repository
    """
    try:
        Repo(path)
        return True
    except git.InvalidGitRepositoryError:
        return False


def get_repo_info(repo_path: Path) -> dict:
    """
    Get information about a git repository

    Args:
        repo_path: Path to repository

    Returns:
        Dictionary with repository information
    """
    if not is_git_repo(repo_path):
        return {}

    try:
        repo = Repo(repo_path)
        return {
            'remote_url': repo.remotes.origin.url if repo.remotes else None,
            'branch': repo.active_branch.name,
            'last_commit': {
                'hash': repo.head.commit.hexsha[:8],
                'message': repo.head.commit.message.strip(),
                'author': str(repo.head.commit.author),
                'date': repo.head.commit.committed_datetime.isoformat()
            }
        }
    except Exception as e:
        logger.warning(f"Could not get repository info: {e}")
        return {}
