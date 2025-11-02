"""
Ruby project analyzer
"""
from typing import Optional
from .base import BaseAnalyzer
from ..models import ProjectMetadata, TechStack


class RubyAnalyzer(BaseAnalyzer):
    """Analyzer for Ruby projects"""

    async def analyze(self) -> Optional[ProjectMetadata]:
        """Analyze Ruby project"""
        gemfile = self.read_file('Gemfile')
        if not gemfile:
            return None

        # Check for Rails
        if 'rails' in gemfile.lower():
            return ProjectMetadata(
                tech_stack=TechStack.RAILS,
                setup_commands=[
                    "bundle install",
                    "rails db:migrate"
                ],
                start_command="rails server",
                default_port=3000,
                entry_points=["/", "/admin"],
                readme_summary=self.extract_readme(),
                key_features=self.extract_features_from_readme() or ["Ruby on Rails application"],
                repo_path=str(self.repo_path)
            )

        return None
