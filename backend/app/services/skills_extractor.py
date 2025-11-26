"""Skills extractor."""

import re
import logging
from typing import Optional

from app.constants import SectionHeaders

logger = logging.getLogger(__name__)


class SkillsExtractor:
    """Extract skills from resume text."""

    def extract(self, text: str) -> list[str]:
        """
        Extract skills from resume text.

        Args:
            text: Raw text content from resume.

        Returns:
            List of extracted skills.
        """
        skills_section = self._find_skills_section(text)
        if not skills_section:
            logger.warning("No skills section found")
            return []

        skills = self._parse_skills(skills_section)
        logger.info(f"Extracted {len(skills)} skills")
        return skills

    def _find_skills_section(self, text: str) -> Optional[str]:
        """Find and extract the skills section from text."""
        lines = text.split("\n")
        section_start = None
        section_end = None
        header_at_end_of_line = None  # Track if header appears mid-line

        # Sort headers by length (prefer more specific matches)
        sorted_headers = sorted(SectionHeaders.SKILLS, key=len, reverse=True)

        # Find section start
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            lower_line = stripped_line.lower()

            for header in sorted_headers:
                # Header should start the line or be the entire line
                if lower_line.startswith(header) or lower_line == header:
                    section_start = i
                    break
                # Also check for header at end of line (merged PDF text)
                # e.g., "Deans List TECHNICAL SKILLS" or "...GPA: 3.7 SKILLS"
                if header in lower_line:
                    # Find where the header starts
                    idx = lower_line.find(header)
                    if idx > 0:
                        # Header is not at start - it's at end of content line
                        # Check if what follows the header is likely skill content
                        section_start = i
                        header_at_end_of_line = header
                        break

            if section_start is not None:
                break

        if section_start is None:
            return None

        # Find section end (next major section)
        # Only consider actual section headers, not content lines
        other_headers = (
            SectionHeaders.EDUCATION + SectionHeaders.EXPERIENCE +
            SectionHeaders.PROJECTS + SectionHeaders.SUMMARY
        )

        for i in range(section_start + 1, len(lines)):
            line = lines[i].strip()
            lower_line = line.lower()

            # Skip if it looks like content (has colon followed by content, or is long)
            if ":" in line and len(line.split(":", 1)[1].strip()) > 10:
                continue

            # Section headers are typically short (< 5 words) and uppercase or title case
            words = line.split()
            if len(words) > 5:
                continue

            if any(header in lower_line for header in other_headers):
                section_end = i
                break

        if section_end is None:
            section_end = len(lines)

        # Extract section text
        section_lines = lines[section_start:section_end]

        # If header was at end of a line, truncate content before it
        if header_at_end_of_line and section_lines:
            first_line = section_lines[0]
            lower_first = first_line.lower()
            idx = lower_first.find(header_at_end_of_line)
            if idx > 0:
                # Keep only the header and after
                section_lines[0] = first_line[idx:]

        return "\n".join(section_lines)

    def _parse_skills(self, section_text: str) -> list[str]:
        """Parse individual skills from section text."""
        skills = []
        lines = section_text.split("\n")

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Skip section headers
            if any(h in line.lower() for h in SectionHeaders.SKILLS):
                continue

            # Handle "Category: skill1, skill2, skill3" format
            if ":" in line:
                # Split on colon and take the skills part
                parts = line.split(":", 1)
                if len(parts) == 2:
                    skills_part = parts[1].strip()
                    if skills_part:
                        extracted = self._extract_skills_from_text(skills_part)
                        skills.extend(extracted)
                continue

            # Skip category headers (short lines followed by skills on next line)
            if self._is_category_header(line, lines, i):
                continue

            # Handle bullet points
            if line.startswith(("•", "-", "*", "·")):
                line = line.lstrip("•-*· ").strip()

            # Extract skills from line
            extracted = self._extract_skills_from_text(line)
            skills.extend(extracted)

        # Remove duplicates while preserving order
        seen = set()
        unique_skills = []
        for skill in skills:
            skill_lower = skill.lower()
            if skill_lower not in seen:
                seen.add(skill_lower)
                unique_skills.append(skill)

        return unique_skills

    def _extract_skills_from_text(self, text: str) -> list[str]:
        """Extract individual skills from a text string."""
        skills = []

        # Split by common delimiters
        # Handle comma, pipe, semicolon, bullet points
        delimiters = r"[,;|•·]|\s{2,}"
        parts = re.split(delimiters, text)

        for part in parts:
            skill = part.strip()
            # Skip empty or very short items
            if len(skill) < 2:
                continue

            # Skip if it's just a category name
            if self._is_category_name(skill):
                continue

            # Clean up the skill
            skill = self._clean_skill(skill)
            if skill:
                skills.append(skill)

        return skills

    def _is_category_header(self, line: str, lines: list[str], index: int) -> bool:
        """Check if line is a category header (short line followed by skills)."""
        # Category headers are typically short (1-4 words) and don't contain commas
        words = line.split()
        if len(words) > 4 or "," in line:
            return False

        # Check if it matches known category patterns
        category_patterns = [
            "languages", "frameworks", "databases", "tools", "technologies",
            "cloud", "devops", "frontend", "backend", "analytics", "marketing",
            "digital", "soft skills", "programming", "technical", "professional"
        ]
        lower_line = line.lower()
        if any(cat in lower_line for cat in category_patterns):
            # Verify next line has comma-separated items (actual skills)
            if index + 1 < len(lines):
                next_line = lines[index + 1].strip()
                if "," in next_line and len(next_line.split(",")) >= 2:
                    return True
        return False

    def _is_category_name(self, text: str) -> bool:
        """Check if text is a category name rather than a skill."""
        categories = [
            "languages", "frameworks", "databases", "tools", "technologies",
            "cloud", "devops", "frontend", "backend", "other", "soft skills",
            "programming", "technical", "professional", "analytics", "marketing",
            "digital marketing", "analytics & tools"
        ]
        return text.lower().strip() in categories

    def _clean_skill(self, skill: str) -> str:
        """Clean and normalize a skill string."""
        # Remove leading/trailing punctuation
        skill = skill.strip(".,;:-•·")

        # Remove parenthetical notes like "(2 years)"
        skill = re.sub(r"\s*\([^)]*\)\s*", "", skill)

        # Remove trailing numbers
        skill = re.sub(r"\s+\d+$", "", skill)

        return skill.strip()
