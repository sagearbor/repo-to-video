"""
Go project analyzer
"""
from typing import Optional
from .base import BaseAnalyzer
from ..models import ProjectMetadata, TechStack


class GoAnalyzer(BaseAnalyzer):
    """Analyzer for Go projects"""

    async def analyze(self) -> Optional[ProjectMetadata]:
        """Analyze Go project"""
        if not self.file_exists('go.mod'):
            return None

        # Look for main.go
        start_command = "go run main.go"
        if self.file_exists('cmd/server/main.go'):
            start_command = "go run cmd/server/main.go"
        elif self.file_exists('cmd/main.go'):
            start_command = "go run cmd/main.go"

        return ProjectMetadata(
            tech_stack=TechStack.GO,
            setup_commands=["go mod download"],
            start_command=start_command,
            default_port=8080,
            entry_points=["/", "/api", "/health"],
            readme_summary=self.extract_readme(),
            key_features=self.extract_features_from_readme() or ["Go web service"],
            repo_path=str(self.repo_path)
        )
