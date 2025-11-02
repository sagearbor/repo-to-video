"""
Base analyzer class for technology stack detection
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List
from ..models import ProjectMetadata, TechStack
from ..utils.file_utils import read_file, file_exists


class BaseAnalyzer(ABC):
    """Base class for project analyzers"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    @abstractmethod
    async def analyze(self) -> Optional[ProjectMetadata]:
        """
        Analyze the repository and return project metadata

        Returns:
            ProjectMetadata if analysis successful, None otherwise
        """
        pass

    def file_exists(self, relative_path: str) -> bool:
        """Check if a file exists in the repository"""
        return file_exists(self.repo_path / relative_path)

    def read_file(self, relative_path: str) -> Optional[str]:
        """Read a file from the repository"""
        return read_file(self.repo_path / relative_path)

    def extract_readme(self) -> str:
        """Extract README content"""
        for readme_name in ['README.md', 'README.rst', 'README.txt', 'README']:
            content = self.read_file(readme_name)
            if content:
                # Extract first paragraph or first 500 characters
                lines = content.split('\n')
                paragraphs = []
                current_para = []

                for line in lines:
                    line = line.strip()
                    if line.startswith('#'):  # Skip headers
                        continue
                    if line:
                        current_para.append(line)
                    elif current_para:
                        paragraphs.append(' '.join(current_para))
                        if len(paragraphs) >= 2:  # Get first 2 paragraphs
                            break
                        current_para = []

                if paragraphs:
                    summary = ' '.join(paragraphs)
                    return summary[:500] + ('...' if len(summary) > 500 else '')

        return "No description available"

    def extract_features_from_readme(self) -> List[str]:
        """Extract key features from README"""
        readme = self.read_file('README.md')
        if not readme:
            return []

        features = []
        lines = readme.split('\n')

        # Look for features section
        in_features_section = False
        for line in lines:
            line = line.strip()

            # Check if we're entering features section
            if any(keyword in line.lower() for keyword in ['## features', '## key features', '### features']):
                in_features_section = True
                continue

            # Check if we've left features section
            if in_features_section and line.startswith('##'):
                break

            # Extract bullet points
            if in_features_section and (line.startswith('- ') or line.startswith('* ')):
                feature = line[2:].strip()
                if feature and len(feature) > 10:  # Meaningful features
                    features.append(feature)

        return features[:10]  # Limit to 10 features

    def detect_port_from_readme(self, default_port: int) -> int:
        """Try to detect port number from README"""
        readme = self.read_file('README.md')
        if not readme:
            return default_port

        # Look for common port patterns
        import re
        port_patterns = [
            r'localhost:(\d+)',
            r'port\s+(\d+)',
            r':(\d+)/',
        ]

        for pattern in port_patterns:
            matches = re.findall(pattern, readme, re.IGNORECASE)
            if matches:
                try:
                    port = int(matches[0])
                    if 1000 <= port <= 65535:
                        return port
                except ValueError:
                    continue

        return default_port
