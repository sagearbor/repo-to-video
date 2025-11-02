"""
Static HTML project analyzer
"""
import os
from typing import Optional, List
from .base import BaseAnalyzer
from ..models import ProjectMetadata, TechStack


class StaticHTMLAnalyzer(BaseAnalyzer):
    """Analyzer for static HTML projects"""

    async def analyze(self) -> Optional[ProjectMetadata]:
        """Analyze static HTML project"""

        # Discover HTML files
        html_files = self._discover_html_files()

        if not html_files:
            return None

        # Extract features from HTML
        readme_summary = self.extract_readme()
        key_features = self.extract_features_from_readme()

        if not key_features:
            key_features = ["Static HTML website", "No backend required"]

        # Entry points are HTML files
        entry_points = [f"/{file}" if file != 'index.html' else '/' for file in html_files[:5]]

        return ProjectMetadata(
            tech_stack=TechStack.STATIC_HTML,
            setup_commands=[],  # No setup needed
            start_command="python -m http.server 8000",
            default_port=8000,
            entry_points=entry_points,
            readme_summary=readme_summary,
            key_features=key_features,
            repo_path=str(self.repo_path)
        )

    def _discover_html_files(self) -> List[str]:
        """Discover HTML files in the repository"""
        html_files = []

        for root, dirs, files in os.walk(self.repo_path):
            # Skip node_modules, .git, etc.
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'node_modules']

            for file in files:
                if file.endswith('.html'):
                    rel_path = os.path.relpath(os.path.join(root, file), self.repo_path)
                    html_files.append(rel_path)

        return html_files
