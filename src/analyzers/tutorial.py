"""
Tutorial/Documentation analyzer
Detects repositories that are primarily tutorials or documentation
"""
from pathlib import Path
from typing import Optional
from .base import BaseAnalyzer
from ..models import ProjectMetadata, TechStack
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TutorialAnalyzer(BaseAnalyzer):
    """Analyzer for tutorial and documentation repositories"""

    async def analyze(self) -> Optional[ProjectMetadata]:
        """
        Detect if repository is a tutorial/documentation repository

        Returns:
            ProjectMetadata with TUTORIAL tech stack
        """
        logger.info("Analyzing as tutorial repository")

        # Check for tutorial indicators
        has_tutorials_dir = (self.repo_path / 'tutorials').exists()
        has_docs_dir = (self.repo_path / 'docs').exists()

        # Count markdown files
        md_files = list(self.repo_path.glob('*.md'))
        md_files.extend(self.repo_path.glob('tutorials/*.md'))
        md_files.extend(self.repo_path.glob('docs/*.md'))

        # Check for web app indicators (disqualifiers)
        has_package_json_with_scripts = False
        package_json = self.repo_path / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json) as f:
                    data = json.load(f)
                    # Only disqualify if there are web server scripts
                    scripts = data.get('scripts', {})
                    has_package_json_with_scripts = any(
                        keyword in str(scripts).lower()
                        for keyword in ['start', 'serve', 'dev']
                    )
            except:
                pass

        has_server_file = (
            (self.repo_path / 'server.py').exists() or
            (self.repo_path / 'app.py').exists() or
            (self.repo_path / 'main.py').exists() and self._has_server_code()
        )

        # Tutorial criteria: has tutorial/docs content AND no web app
        is_tutorial = (
            (has_tutorials_dir or (has_docs_dir and len(md_files) >= 3)) and
            not has_package_json_with_scripts and
            not has_server_file
        )

        if not is_tutorial:
            logger.info("Not a tutorial repository (has web app indicators or insufficient tutorial content)")
            return None

        # Extract metadata from README
        readme_summary = self.extract_readme()
        key_features = self.extract_features_from_readme()

        # Create metadata
        metadata = ProjectMetadata(
            tech_stack=TechStack.TUTORIAL,
            setup_commands=[],  # No setup needed for tutorials
            start_command="",  # No server to start
            default_port=0,  # No port needed
            entry_points=self._find_tutorial_files(),
            readme_summary=readme_summary,
            key_features=key_features,
            repo_path=str(self.repo_path)
        )

        logger.info(f"Detected tutorial repository with {len(metadata.entry_points)} tutorial files")
        return metadata

    def _has_server_code(self) -> bool:
        """Check if main.py contains server code"""
        main_py = self.repo_path / 'main.py'
        if not main_py.exists():
            return False

        try:
            content = main_py.read_text().lower()
            server_keywords = ['flask', 'fastapi', 'django', 'uvicorn', 'app.run', '@app.route']
            return any(keyword in content for keyword in server_keywords)
        except:
            return False

    def _find_tutorial_files(self) -> list:
        """Find all tutorial markdown and Python files"""
        tutorial_files = []

        # Check tutorials directory
        tutorials_dir = self.repo_path / 'tutorials'
        if tutorials_dir.exists():
            # Get all .md and .py files in tutorials/
            for ext in ['*.md', '*.py']:
                for file in sorted(tutorials_dir.glob(ext)):
                    tutorial_files.append(f"tutorials/{file.name}")

        # Check docs directory
        docs_dir = self.repo_path / 'docs'
        if docs_dir.exists():
            for file in sorted(docs_dir.glob('*.md')):
                tutorial_files.append(f"docs/{file.name}")

        # Limit to reasonable number
        return tutorial_files[:20]
