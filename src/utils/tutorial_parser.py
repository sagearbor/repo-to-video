"""
Tutorial parser for extracting structured information from markdown tutorials
"""
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TutorialStep:
    """Represents a single step in a tutorial"""
    step_number: int
    heading: str
    content: str
    code_snippets: List[str]
    file_references: List[str]
    narration_text: str


@dataclass
class TutorialStructure:
    """Structured representation of a tutorial"""
    title: str
    file_path: str
    description: str
    steps: List[TutorialStep]


class TutorialParser:
    """Parser for markdown and Python tutorial files"""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def parse_markdown(self, file_path: Path) -> TutorialStructure:
        """
        Parse a markdown tutorial file into structured steps

        Args:
            file_path: Path to the markdown file

        Returns:
            TutorialStructure with parsed content
        """
        logger.info(f"Parsing markdown tutorial: {file_path.name}")

        content = file_path.read_text()

        # Extract title (first H1 heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem

        # Extract description (content before first H2)
        description_match = re.search(r'^#\s+.+?\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
        description = description_match.group(1).strip() if description_match else ""

        # Split into sections by H2 headings
        sections = re.split(r'^##\s+(.+)$', content, flags=re.MULTILINE)

        steps = []
        step_number = 1

        # Process sections (skip first element which is before first H2)
        for i in range(1, len(sections), 2):
            if i + 1 >= len(sections):
                break

            heading = sections[i].strip()
            section_content = sections[i + 1].strip()

            # Extract code snippets
            code_snippets = re.findall(r'```(?:\w+)?\n(.+?)```', section_content, re.DOTALL)

            # Extract file references (e.g., "create file.py" or "open `file.py`")
            file_refs = re.findall(r'`([a-zA-Z0-9_/\-\.]+\.(py|md|js|ts|json|yaml|yml))`', section_content)
            file_references = [ref[0] for ref in file_refs]

            # Create narration text by removing code blocks and formatting
            narration = self._create_narration(heading, section_content)

            step = TutorialStep(
                step_number=step_number,
                heading=heading,
                content=section_content,
                code_snippets=code_snippets,
                file_references=file_references,
                narration_text=narration
            )

            steps.append(step)
            step_number += 1

        return TutorialStructure(
            title=title,
            file_path=str(file_path.relative_to(self.repo_path)),
            description=description,
            steps=steps
        )

    def parse_python_file(self, file_path: Path) -> TutorialStructure:
        """
        Parse a Python tutorial file (code with comments)

        Args:
            file_path: Path to the Python file

        Returns:
            TutorialStructure with code sections
        """
        logger.info(f"Parsing Python tutorial: {file_path.name}")

        content = file_path.read_text()

        # Extract module docstring as title/description
        docstring_match = re.search(r'^"""(.+?)"""', content, re.DOTALL)
        if docstring_match:
            docstring = docstring_match.group(1).strip()
            lines = docstring.split('\n')
            title = lines[0].strip()
            description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
        else:
            title = file_path.stem.replace('_', ' ').title()
            description = ""

        # Split by section comments (lines starting with # followed by uppercase)
        sections = re.split(r'\n(# [A-Z][^\n]+)\n', content)

        steps = []
        step_number = 1

        for i in range(1, len(sections), 2):
            if i + 1 >= len(sections):
                break

            heading = sections[i].replace('#', '').strip()
            section_content = sections[i + 1].strip()

            # Create a single code snippet for the section
            code_snippets = [section_content] if section_content else []

            narration = f"{heading}. This section demonstrates {heading.lower()}."

            step = TutorialStep(
                step_number=step_number,
                heading=heading,
                content=section_content,
                code_snippets=code_snippets,
                file_references=[str(file_path.relative_to(self.repo_path))],
                narration_text=narration
            )

            steps.append(step)
            step_number += 1

        # If no sections found, treat entire file as one step
        if not steps:
            steps.append(TutorialStep(
                step_number=1,
                heading=title,
                content=content,
                code_snippets=[content],
                file_references=[str(file_path.relative_to(self.repo_path))],
                narration_text=f"This tutorial demonstrates {title}"
            ))

        return TutorialStructure(
            title=title,
            file_path=str(file_path.relative_to(self.repo_path)),
            description=description,
            steps=steps
        )

    def _create_narration(self, heading: str, content: str) -> str:
        """
        Create narration text from heading and content

        Args:
            heading: Section heading
            content: Section content

        Returns:
            Narration text suitable for TTS
        """
        # Remove code blocks
        clean_content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

        # Remove markdown formatting
        clean_content = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_content)  # Bold
        clean_content = re.sub(r'\*(.+?)\*', r'\1', clean_content)  # Italic
        clean_content = re.sub(r'`(.+?)`', r'\1', clean_content)  # Inline code
        clean_content = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', clean_content)  # Links

        # Get first few sentences (up to 200 characters)
        sentences = re.split(r'[.!?]\s+', clean_content)
        narration_parts = [heading]

        char_count = len(heading)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if char_count + len(sentence) > 200:
                break
            narration_parts.append(sentence)
            char_count += len(sentence)

        narration = '. '.join(narration_parts)

        # Clean up extra whitespace
        narration = re.sub(r'\s+', ' ', narration).strip()

        return narration + '.'

    def parse_all_tutorials(self) -> List[TutorialStructure]:
        """
        Parse all tutorial files in the repository

        Returns:
            List of TutorialStructure objects
        """
        tutorials = []

        # Check tutorials directory
        tutorials_dir = self.repo_path / 'tutorials'
        if tutorials_dir.exists():
            # Parse markdown files
            for md_file in sorted(tutorials_dir.glob('*.md')):
                try:
                    tutorial = self.parse_markdown(md_file)
                    tutorials.append(tutorial)
                except Exception as e:
                    logger.warning(f"Failed to parse {md_file.name}: {e}")

            # Parse Python files
            for py_file in sorted(tutorials_dir.glob('*.py')):
                try:
                    tutorial = self.parse_python_file(py_file)
                    tutorials.append(tutorial)
                except Exception as e:
                    logger.warning(f"Failed to parse {py_file.name}: {e}")

        # Check docs directory
        docs_dir = self.repo_path / 'docs'
        if docs_dir.exists():
            for md_file in sorted(docs_dir.glob('*.md')):
                try:
                    tutorial = self.parse_markdown(md_file)
                    tutorials.append(tutorial)
                except Exception as e:
                    logger.warning(f"Failed to parse {md_file.name}: {e}")

        logger.info(f"Parsed {len(tutorials)} tutorial files")
        return tutorials
