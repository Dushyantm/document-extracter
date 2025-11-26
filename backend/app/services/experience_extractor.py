"""Work experience extractor."""

import re
import logging
from typing import Optional

from app.models.extraction import WorkExperience
from app.constants import Patterns, SectionHeaders

logger = logging.getLogger(__name__)


class ExperienceExtractor:
    """Extract work experience from resume text."""

    # Date range patterns
    DATE_RANGE_PATTERN = r"(\w+\.?\s*\d{4})\s*(?:-|–|to)\s*(\w+\.?\s*\d{4}|present|current)"

    # Job title keywords that strongly indicate a job title line
    JOB_TITLE_KEYWORDS = [
        "engineer", "developer", "manager", "director", "analyst",
        "designer", "architect", "lead", "senior", "junior", "intern",
        "specialist", "coordinator", "administrator", "consultant",
        "executive", "officer", "associate", "assistant", "supervisor",
        "technician", "representative", "strategist"
    ]

    # Company indicators
    COMPANY_INDICATORS = [
        "inc", "llc", "ltd", "corp", "corporation", "company", "co.",
        "solutions", "technologies", "services", "group", "partners"
    ]

    def extract(self, text: str) -> list[WorkExperience]:
        """
        Extract work experience entries from resume text.

        Args:
            text: Raw text content from resume.

        Returns:
            List of WorkExperience entries.
        """
        experience_section = self._find_experience_section(text)
        if not experience_section:
            logger.warning("No experience section found")
            return []

        entries = self._parse_experience_entries(experience_section)
        logger.info(f"Extracted {len(entries)} work experience entries")
        return entries

    def _find_experience_section(self, text: str) -> Optional[str]:
        """Find and extract the experience section from text."""
        lines = text.split("\n")
        section_start = None
        section_end = None

        # Try to find the most specific match first (longer headers first)
        sorted_headers = sorted(SectionHeaders.EXPERIENCE, key=len, reverse=True)
        exclude_headers = getattr(SectionHeaders, 'EXCLUDE_FROM_EXPERIENCE', [])

        # Find section start - prefer more specific matches
        for i, line in enumerate(lines):
            lower_line = line.lower().strip()

            # Skip lines that match exclusion patterns (like "professional summary")
            if any(excl in lower_line for excl in exclude_headers):
                continue

            for header in sorted_headers:
                if header in lower_line:
                    section_start = i
                    break
            if section_start is not None:
                break

        if section_start is None:
            return None

        # Find section end (next major section)
        other_headers = (
            SectionHeaders.EDUCATION + SectionHeaders.SKILLS +
            SectionHeaders.PROJECTS + SectionHeaders.CERTIFICATIONS
        )

        for i in range(section_start + 1, len(lines)):
            lower_line = lines[i].lower().strip()
            # Check if this line is a section header (but not part of content)
            if self._is_section_header(lower_line, other_headers):
                section_end = i
                break

        if section_end is None:
            section_end = len(lines)

        return "\n".join(lines[section_start:section_end])

    def _is_section_header(self, line: str, headers: list) -> bool:
        """Check if a line is a section header (short line with header keyword)."""
        # Section headers are typically short and standalone
        words = line.split()
        if len(words) > 5:
            return False
        return any(header in line for header in headers)

    def _parse_experience_entries(self, section_text: str) -> list[WorkExperience]:
        """Parse individual work experience entries."""
        entries = []
        lines = section_text.split("\n")

        current_entry = {}
        current_descriptions = []
        awaiting_company_date = False  # True when we just saw a job title, waiting for company/date

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Skip section header
            if any(h in line.lower() for h in SectionHeaders.EXPERIENCE):
                continue

            # Skip bullet points and add to descriptions
            if self._is_bullet_point(line):
                if current_entry:
                    desc = line.lstrip("•-*·–►▪ ").strip()
                    if desc:
                        current_descriptions.append(desc)
                continue

            # Check if this line has a date range (strong indicator of job entry)
            has_date = re.search(self.DATE_RANGE_PATTERN, line, re.IGNORECASE)

            # Check if this looks like a standalone job title
            is_job_title_line = self._is_job_title_line(line)

            # Check if this looks like a company line
            is_company_line = self._looks_like_company_line(line)

            if has_date:
                dates = self._extract_dates_from_line(line)

                # If we're waiting for company/date after seeing a job title
                if awaiting_company_date and current_entry.get("job_title"):
                    # This line has dates - extract company from it
                    company = self._extract_company_from_date_line(line)
                    if company:
                        current_entry["company"] = company
                    current_entry.update(dates)
                    awaiting_company_date = False
                elif is_job_title_line:
                    # Save previous complete entry
                    if current_entry and current_entry.get("job_title") and current_entry.get("company"):
                        current_entry["description"] = current_descriptions
                        entries.append(self._create_experience(current_entry))
                        current_descriptions = []
                    # Job title on the same line as date
                    current_entry = self._parse_job_header(line)
                    current_entry.update(dates)
                    awaiting_company_date = False
                else:
                    # This is likely a company line with date
                    company = self._extract_company_from_date_line(line)
                    if current_entry.get("job_title") and not current_entry.get("company") and company:
                        # Attach to current entry
                        current_entry["company"] = company
                        current_entry.update(dates)
                        awaiting_company_date = False

            elif is_job_title_line:
                # Standalone job title line (no date)
                # Save previous complete entry first
                if current_entry and current_entry.get("job_title") and current_entry.get("company"):
                    current_entry["description"] = current_descriptions
                    entries.append(self._create_experience(current_entry))
                    current_descriptions = []

                # Start new entry with job title, await company/date on next line
                current_entry = {"job_title": self._clean_job_title(line)}
                awaiting_company_date = True

            elif is_company_line and current_entry and awaiting_company_date:
                # Company line without date (rare but possible)
                if "company" not in current_entry:
                    company = self._extract_company_name(line)
                    if company:
                        current_entry["company"] = company

            elif current_entry and current_entry.get("job_title") and len(line) > 20:
                # Long line without clear pattern - might be description
                if not awaiting_company_date:
                    current_descriptions.append(line)

        # Don't forget last entry
        if current_entry and current_entry.get("job_title") and current_entry.get("company"):
            current_entry["description"] = current_descriptions
            entries.append(self._create_experience(current_entry))

        return entries

    def _is_bullet_point(self, line: str) -> bool:
        """Check if line is a bullet point."""
        return line.startswith(("•", "-", "*", "·", "–", "►", "▪"))

    def _is_job_title_line(self, line: str) -> bool:
        """Check if line looks like a job title (not a bullet, not too long, has title keywords)."""
        # Not a bullet point
        if self._is_bullet_point(line):
            return False

        # Not too long (job titles are typically short)
        if len(line) > 80:
            return False

        # Should contain job title keywords
        lower_line = line.lower()
        has_title_keyword = any(kw in lower_line for kw in self.JOB_TITLE_KEYWORDS)

        if not has_title_keyword:
            return False

        # Should NOT look like a full sentence (description)
        # Descriptions often start with verbs and are longer
        description_starters = [
            "led ", "managed ", "developed ", "created ", "built ", "designed ",
            "implemented ", "responsible for", "worked with", "collaborated"
        ]
        if any(lower_line.startswith(s) for s in description_starters):
            return False

        return True

    def _looks_like_company_line(self, line: str) -> bool:
        """Check if line looks like a company/location line."""
        lower_line = line.lower()

        # Has company indicators
        if any(ind in lower_line for ind in self.COMPANY_INDICATORS):
            return True

        # Has location pattern (City, ST)
        if re.search(r",\s*[A-Z]{2}\b", line):
            return True

        return False

    def _parse_job_header(self, line: str) -> dict:
        """Parse job title and dates from header line."""
        result = {}

        # Extract date range
        date_pattern = r"(\w+\.?\s*\d{4})\s*(?:-|–|to)\s*(\w+\.?\s*\d{4}|present|current)"
        date_match = re.search(date_pattern, line, re.IGNORECASE)
        if date_match:
            result["start_date"] = date_match.group(1)
            result["end_date"] = date_match.group(2)
            # Remove dates from line to get title
            title_part = line[:date_match.start()].strip()
        else:
            title_part = line

        # Clean up title
        title_part = re.sub(r"\|.*$", "", title_part).strip()
        title_part = title_part.rstrip(",").strip()

        if title_part:
            result["job_title"] = title_part

        return result

    def _clean_job_title(self, line: str) -> str:
        """Clean job title by removing dates and extra info."""
        # Remove date patterns
        clean = re.sub(self.DATE_RANGE_PATTERN, "", line, flags=re.IGNORECASE)
        # Remove pipe and content after
        clean = re.sub(r"\|.*$", "", clean)
        return clean.strip().rstrip(",").strip()

    def _extract_company_from_date_line(self, line: str) -> Optional[str]:
        """Extract company name from a line that contains dates."""
        # Remove the date pattern
        clean = re.sub(self.DATE_RANGE_PATTERN, "", line, flags=re.IGNORECASE)
        # Remove pipe
        clean = re.sub(r"\|", " ", clean).strip()
        # Remove location pattern at end (City, ST)
        location_match = re.search(r",\s*([^,]+),\s*([A-Z]{2})\s*$", clean)
        if location_match:
            clean = clean[:location_match.start()].strip()

        # Clean up
        clean = clean.strip().rstrip(",").strip()

        # Don't return if it looks like a job title
        if clean and not self._looks_like_job_title(clean):
            return clean
        return None

    def _extract_company_name(self, line: str) -> Optional[str]:
        """Extract company name from a company line."""
        clean = line.strip()
        # Remove location at end
        clean = re.sub(r",\s*[^,]+,\s*[A-Z]{2}\s*$", "", clean).strip()
        # Remove pipe and everything after
        if "|" in clean:
            clean = clean.split("|")[0].strip()
        return clean if clean else None

    def _extract_dates_from_line(self, line: str) -> Optional[dict]:
        """Extract start and end dates from a line."""
        date_pattern = r"(\w+\.?\s*\d{4})\s*(?:-|–|to)\s*(\w+\.?\s*\d{4}|present|current)"
        match = re.search(date_pattern, line, re.IGNORECASE)
        if match:
            return {
                "start_date": match.group(1),
                "end_date": match.group(2),
            }
        return None

    def _parse_company_line(self, line: str) -> Optional[dict]:
        """Parse company name from line."""
        # Remove date patterns first
        clean_line = re.sub(
            r"\|\s*\w+\.?\s*\d{4}\s*(?:-|–|to)\s*(?:\w+\.?\s*\d{4}|present|current)",
            "",
            line,
            flags=re.IGNORECASE
        ).strip()

        if "|" in clean_line:
            clean_line = clean_line.split("|")[0].strip()

        # Remove location part (City, ST)
        clean_line = re.sub(r",\s*[^,]+,\s*[A-Z]{2}\s*$", "", clean_line).strip()

        if clean_line and not self._looks_like_job_title(clean_line):
            return {"company": clean_line}

        return None

    def _looks_like_job_title(self, text: str) -> bool:
        """Check if text looks like a job title."""
        job_keywords = [
            "engineer", "developer", "manager", "director", "analyst",
            "designer", "architect", "lead", "senior", "junior"
        ]
        return any(kw in text.lower() for kw in job_keywords)

    def _looks_like_header(self, line: str) -> bool:
        """Check if line looks like a section header."""
        all_headers = (
            SectionHeaders.EDUCATION + SectionHeaders.EXPERIENCE +
            SectionHeaders.SKILLS + SectionHeaders.CERTIFICATIONS
        )
        return any(h in line.lower() for h in all_headers)

    def _create_experience(self, data: dict) -> WorkExperience:
        """Create WorkExperience object from parsed data."""
        return WorkExperience(
            job_title=data.get("job_title"),
            company=data.get("company"),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            description=data.get("description", []),
        )
