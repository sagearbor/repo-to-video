"""
PHP project analyzer
"""
from typing import Optional
from .base import BaseAnalyzer
from ..models import ProjectMetadata, TechStack


class PHPAnalyzer(BaseAnalyzer):
    """Analyzer for PHP projects"""

    async def analyze(self) -> Optional[ProjectMetadata]:
        """Analyze PHP project"""

        setup_commands = []
        if self.file_exists('composer.json'):
            setup_commands = ["composer install"]

        return ProjectMetadata(
            tech_stack=TechStack.PHP,
            setup_commands=setup_commands,
            start_command="php -S localhost:8000",
            default_port=8000,
            entry_points=["/", "/index.php"],
            readme_summary=self.extract_readme(),
            key_features=self.extract_features_from_readme() or ["PHP web application"],
            repo_path=str(self.repo_path)
        )
