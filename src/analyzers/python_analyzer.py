"""
Python project analyzer
"""
import re
from typing import Optional, List
from .base import BaseAnalyzer
from ..models import ProjectMetadata, TechStack


class PythonAnalyzer(BaseAnalyzer):
    """Analyzer for Python projects"""

    async def analyze(self) -> Optional[ProjectMetadata]:
        """Analyze Python project"""

        # Read requirements to determine framework
        requirements = self._read_requirements()

        if not requirements:
            return None

        requirements_lower = [req.lower() for req in requirements]

        # Detect specific framework
        tech_stack = TechStack.UNKNOWN
        start_command = "python main.py"
        default_port = 8000
        setup_commands = []

        if any('fastapi' in req for req in requirements_lower):
            tech_stack = TechStack.FASTAPI
            start_command = self._detect_fastapi_command()
            default_port = 8000
            setup_commands = [
                "python -m venv venv",
                "source venv/bin/activate",
                "pip install -r requirements.txt"
            ]

        elif any('flask' in req for req in requirements_lower):
            tech_stack = TechStack.FLASK
            start_command = self._detect_flask_command()
            default_port = 5000
            setup_commands = [
                "python -m venv venv",
                "source venv/bin/activate",
                "pip install -r requirements.txt"
            ]

        elif any('django' in req for req in requirements_lower):
            tech_stack = TechStack.DJANGO
            start_command = "python manage.py runserver"
            default_port = 8000
            setup_commands = [
                "python -m venv venv",
                "source venv/bin/activate",
                "pip install -r requirements.txt",
                "python manage.py migrate"
            ]

        # Try to detect port from README
        default_port = self.detect_port_from_readme(default_port)

        # Extract entry points
        entry_points = self._detect_entry_points(tech_stack)

        # Extract features
        readme_summary = self.extract_readme()
        key_features = self.extract_features_from_readme()

        if not key_features:
            # Fallback: use requirements as features
            key_features = [f"Uses {req.split('==')[0]}" for req in requirements[:5]]

        return ProjectMetadata(
            tech_stack=tech_stack,
            setup_commands=setup_commands,
            start_command=start_command,
            default_port=default_port,
            entry_points=entry_points,
            readme_summary=readme_summary,
            key_features=key_features,
            repo_path=str(self.repo_path)
        )

    def _read_requirements(self) -> List[str]:
        """Read Python requirements from various sources"""
        requirements = []

        # Try requirements.txt
        if self.file_exists('requirements.txt'):
            content = self.read_file('requirements.txt')
            if content:
                requirements = [line.strip() for line in content.split('\n')
                              if line.strip() and not line.startswith('#')]

        # Try pyproject.toml
        elif self.file_exists('pyproject.toml'):
            content = self.read_file('pyproject.toml')
            if content:
                # Simple parsing for dependencies
                import re
                deps = re.findall(r'[\'"]([\w\-]+).*[\'"]', content)
                requirements = deps

        # Try Pipfile
        elif self.file_exists('Pipfile'):
            content = self.read_file('Pipfile')
            if content:
                # Simple parsing for packages
                in_packages = False
                for line in content.split('\n'):
                    if '[packages]' in line:
                        in_packages = True
                        continue
                    if in_packages and line.startswith('['):
                        break
                    if in_packages and '=' in line:
                        pkg = line.split('=')[0].strip()
                        if pkg:
                            requirements.append(pkg)

        return requirements

    def _detect_fastapi_command(self) -> str:
        """Detect FastAPI start command"""
        # Look for main.py or app.py
        for main_file in ['main.py', 'app.py', 'api.py']:
            if self.file_exists(main_file):
                content = self.read_file(main_file)
                if content:
                    # Look for FastAPI app instance
                    match = re.search(r'(\w+)\s*=\s*FastAPI\(', content)
                    if match:
                        app_name = match.group(1)
                        module_name = main_file.replace('.py', '')
                        return f"uvicorn {module_name}:{app_name} --reload --host 0.0.0.0"

        return "uvicorn main:app --reload --host 0.0.0.0"

    def _detect_flask_command(self) -> str:
        """Detect Flask start command"""
        # Look for main.py or app.py
        for main_file in ['main.py', 'app.py', 'run.py']:
            if self.file_exists(main_file):
                content = self.read_file(main_file)
                if content:
                    # Look for Flask app instance
                    if 'Flask(__name__)' in content:
                        module_name = main_file.replace('.py', '')
                        return f"flask --app {module_name} run --host 0.0.0.0"

        return "flask run --host 0.0.0.0"

    def _detect_entry_points(self, tech_stack: TechStack) -> List[str]:
        """Detect entry points based on tech stack"""
        entry_points = ["/"]

        if tech_stack == TechStack.FASTAPI:
            entry_points.extend(['/docs', '/redoc'])
            # Try to detect routes
            # This is a simple implementation; could be enhanced
            entry_points.extend(['/api/items', '/api/users'])

        elif tech_stack == TechStack.DJANGO:
            entry_points.extend(['/admin'])

        elif tech_stack == TechStack.FLASK:
            # Look for common routes
            entry_points.extend(['/api', '/hello'])

        return entry_points
