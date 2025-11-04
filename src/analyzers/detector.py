"""
Technology stack detection
"""
from pathlib import Path
from typing import Optional
from ..models import ProjectMetadata
from ..utils.logger import get_logger
from .nodejs import NodeJSAnalyzer
from .python_analyzer import PythonAnalyzer
from .static_html import StaticHTMLAnalyzer
from .ruby import RubyAnalyzer
from .php import PHPAnalyzer
from .go_analyzer import GoAnalyzer
from .tutorial import TutorialAnalyzer

logger = get_logger(__name__)


async def detect_tech_stack(repo_path: Path) -> Optional[ProjectMetadata]:
    """
    Detect technology stack by analyzing repository files

    Args:
        repo_path: Path to the repository

    Returns:
        ProjectMetadata or None if detection failed
    """
    logger.info(f"Analyzing repository: {repo_path}")

    # Define detectors in priority order
    # Web app indicators are checked FIRST (most common case)
    detectors = [
        # Node.js ecosystems
        ('package.json', NodeJSAnalyzer),

        # Python ecosystems
        ('requirements.txt', PythonAnalyzer),
        ('pyproject.toml', PythonAnalyzer),
        ('Pipfile', PythonAnalyzer),
        ('setup.py', PythonAnalyzer),

        # Ruby
        ('Gemfile', RubyAnalyzer),

        # PHP
        ('composer.json', PHPAnalyzer),
        ('index.php', PHPAnalyzer),

        # Go
        ('go.mod', GoAnalyzer),

        # Static HTML (lowest priority)
        ('index.html', StaticHTMLAnalyzer),
    ]

    for file_indicator, analyzer_class in detectors:
        file_path = repo_path / file_indicator
        if file_path.exists():
            logger.info(f"Detected {file_indicator}, using {analyzer_class.__name__}")
            analyzer = analyzer_class(repo_path)
            try:
                metadata = await analyzer.analyze()
                if metadata:
                    logger.info(f"Successfully analyzed as {metadata.tech_stack.value}")
                    return metadata
            except Exception as e:
                logger.warning(f"Analyzer {analyzer_class.__name__} failed: {e}")
                continue

    # Fallback: Check for tutorial/documentation-only repositories
    # This is LAST RESORT - only if no web app indicators were found
    tutorials_dir = repo_path / 'tutorials'
    docs_dir = repo_path / 'docs'
    if tutorials_dir.exists() or docs_dir.exists():
        logger.info("No web app detected, checking for tutorial/documentation repository")
        analyzer = TutorialAnalyzer(repo_path)
        try:
            metadata = await analyzer.analyze()
            if metadata:
                logger.info(f"Successfully analyzed as {metadata.tech_stack.value}")
                return metadata
        except Exception as e:
            logger.warning(f"Tutorial analyzer failed: {e}")

    logger.error("Unable to detect technology stack")
    raise Exception("Unable to detect technology stack. No supported project files found.")
