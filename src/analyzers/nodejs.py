"""
Node.js project analyzer
"""
import json
from typing import Optional, List
from .base import BaseAnalyzer
from ..models import ProjectMetadata, TechStack


class NodeJSAnalyzer(BaseAnalyzer):
    """Analyzer for Node.js projects"""

    async def analyze(self) -> Optional[ProjectMetadata]:
        """Analyze Node.js project"""
        package_json = self.read_file('package.json')
        if not package_json:
            return None

        try:
            package_data = json.loads(package_json)
        except json.JSONDecodeError:
            return None

        dependencies = package_data.get('dependencies', {})
        dev_dependencies = package_data.get('devDependencies', {})
        all_deps = {**dependencies, **dev_dependencies}

        # Detect specific framework
        tech_stack = TechStack.UNKNOWN
        start_command = "npm start"
        default_port = 3000

        if 'next' in all_deps:
            tech_stack = TechStack.NEXTJS
            start_command = "npm run dev"
            default_port = 3000
        elif 'react' in all_deps or 'react-scripts' in all_deps:
            tech_stack = TechStack.REACT
            start_command = "npm start"
            default_port = 3000
        elif 'vue' in all_deps or '@vue/cli-service' in all_deps:
            tech_stack = TechStack.VUE
            start_command = "npm run serve"
            default_port = 8080
        elif '@angular/core' in all_deps:
            tech_stack = TechStack.ANGULAR
            start_command = "npm start"
            default_port = 4200

        # Check scripts for custom commands
        scripts = package_data.get('scripts', {})
        if 'dev' in scripts:
            start_command = "npm run dev"
        elif 'serve' in scripts:
            start_command = "npm run serve"
        elif 'start' in scripts:
            start_command = "npm start"

        # Try to detect port from README
        default_port = self.detect_port_from_readme(default_port)

        # Setup commands
        setup_commands = ["npm install"]

        # Extract entry points
        entry_points = self._detect_entry_points(tech_stack)

        # Extract features
        readme_summary = self.extract_readme()
        key_features = self.extract_features_from_readme()

        if not key_features:
            # Fallback: use package description or dependencies as features
            if 'description' in package_data:
                key_features.append(package_data['description'])
            key_features.extend([f"Uses {dep}" for dep in list(dependencies.keys())[:5]])

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

    def _detect_entry_points(self, tech_stack: TechStack) -> List[str]:
        """Detect entry points based on tech stack"""
        entry_points = ["/"]

        if tech_stack == TechStack.NEXTJS:
            # Check pages directory
            if self.file_exists('pages'):
                # Common Next.js pages
                entry_points.extend(['/about', '/contact', '/api/hello'])
            if self.file_exists('app'):
                # Next.js 13+ app directory
                entry_points.extend(['/dashboard'])

        elif tech_stack == TechStack.REACT:
            # React apps typically have a single entry point
            entry_points = ["/"]

        elif tech_stack == TechStack.VUE:
            # Check for Vue router
            if self.file_exists('src/router'):
                entry_points.extend(['/about', '/contact'])

        return entry_points
