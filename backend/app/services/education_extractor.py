"""Education information extractor."""

import re
import logging
from typing import Optional

from app.models.extraction import Education
from app.constants import Patterns, SectionHeaders, Degrees

logger = logging.getLogger(__name__)


class EducationExtractor:
    """Extract education information from resume text."""

    # Institution keywords
    INSTITUTION_KEYWORDS = [
        "university", "college", "institute", "school", "academy",
        "polytechnic", "conservatory"
    ]

    # Field of study patterns
    FIELD_PATTERNS = [
        r"(?:of|in)\s+([A-Z][a-zA-Z\s&]+?)(?:\s*\||,|\s+from|\s+at|$)",
        r"(?:B\.?S\.?|B\.?A\.?|M\.?S\.?|M\.?A\.?|MBA|Ph\.?D\.?)\s+(?:in\s+)?([A-Z][a-zA-Z\s&]+?)(?:\s*\||,|$)",
    ]

    def __init__(self):
        """Initialize with degree patterns."""
        self.degree_patterns = {
            "Bachelor": Degrees.BACHELORS,
            "Master": Degrees.MASTERS,
            "Doctorate": Degrees.DOCTORATE,
            "Associate": Degrees.ASSOCIATE,
        }

    def extract(self, text: str) -> list[Education]:
        """
        Extract education entries from resume text.

        Args:
            text: Raw text content from resume.

        Returns:
            List of Education entries.
        """
        education_section = self._find_education_section(text)
        if not education_section:
            logger.warning("No education section found")
            return []

        entries = self._parse_education_entries(education_section)
        logger.info(f"Extracted {len(entries)} education entries")
        return entries

    def _find_education_section(self, text: str) -> Optional[str]:
        """Find and extract the education section from text."""
        lines = text.split("\n")
        section_start = None
        section_end = None

        # Find section start
        for i, line in enumerate(lines):
            lower_line = line.lower().strip()
            if any(header in lower_line for header in SectionHeaders.EDUCATION):
                section_start = i
                break

        if section_start is None:
            return None

        # Find section end (next major section)
        # Be careful: section headers might appear in the middle of content lines
        other_headers = (
            SectionHeaders.EXPERIENCE + SectionHeaders.SKILLS +
            SectionHeaders.PROJECTS + SectionHeaders.CERTIFICATIONS
        )

        for i in range(section_start + 1, len(lines)):
            line = lines[i].strip()
            lower_line = line.lower()

            # Check if this is a standalone section header (short line, starts with header)
            for header in other_headers:
                if lower_line.startswith(header):
                    section_end = i
                    break
                # Also check if the header appears after a delimiter (like | or newline merged)
                # But only if it's at the END of the line and looks like a section header
                if header in lower_line:
                    # Check if line ends with the header (possibly uppercase)
                    words = line.split()
                    last_words = " ".join(words[-3:]).lower() if len(words) >= 3 else lower_line
                    if header in last_words and len(words) <= 6:
                        # This looks like a section header at the end of a merged line
                        # Keep the content before the header
                        section_end = i
                        break

            if section_end is not None:
                break

        if section_end is None:
            section_end = len(lines)

        # Handle case where section header appears mid-line
        section_text = "\n".join(lines[section_start:section_end])

        # If the last line of section contains a different section header at the end,
        # try to extract just the content before it
        if section_end > section_start:
            last_line = lines[section_end - 1] if section_end <= len(lines) else ""
            for header in other_headers:
                if header in last_line.lower():
                    # Find where the header starts and truncate
                    idx = last_line.lower().rfind(header)
                    if idx > 0:
                        lines[section_end - 1] = last_line[:idx].strip()
                        section_text = "\n".join(lines[section_start:section_end])
                    break

        return section_text

    def _parse_education_entries(self, section_text: str) -> list[Education]:
        """Parse individual education entries from section text."""
        entries = []
        lines = section_text.split("\n")

        current_entry = {}
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Skip section header
            if any(h in line.lower() for h in SectionHeaders.EDUCATION):
                continue

            # Check for degree
            degree_found = self._extract_degree(line)
            is_institution_line = self._looks_like_institution(line)

            # Special case: line has BOTH institution AND degree (merged PDF text)
            # e.g., "University of Texas... | May 2017 | ... Bachelor of Science in..."
            if degree_found and is_institution_line:
                # Check if we have a previous entry missing institution
                if current_entry and current_entry.get("degree") and not current_entry.get("institution"):
                    # Extract institution and year from THIS line for the PREVIOUS entry
                    institution = self._extract_institution(line)
                    if institution:
                        current_entry["institution"] = institution
                    year = self._extract_year(line)
                    if year:
                        current_entry["year"] = year
                    # Save the previous entry
                    entries.append(self._create_education(current_entry))
                elif current_entry and current_entry.get("degree"):
                    entries.append(self._create_education(current_entry))

                # Start new entry with the degree found
                current_entry = {"degree": degree_found}
                # Extract field from the degree portion only
                field = self._extract_field_of_study(line)
                if field:
                    current_entry["field"] = field
                continue

            if degree_found:
                # If we have a current entry with a degree, save it
                if current_entry and current_entry.get("degree"):
                    entries.append(self._create_education(current_entry))

                # Start new entry
                current_entry = {"degree": degree_found, "degree_line": line}

                # Try to extract field of study from the degree line
                field = self._extract_field_of_study(line)
                if field:
                    current_entry["field"] = field

                # Check for year on same line
                year = self._extract_year(line)
                if year:
                    current_entry["year"] = year

                continue

            # If this is an institution line and we have a current entry
            if is_institution_line and current_entry:
                if "institution" not in current_entry:
                    institution = self._extract_institution(line)
                    if institution:
                        current_entry["institution"] = institution

                # Also check for year on institution line
                year = self._extract_year(line)
                if year and "year" not in current_entry:
                    current_entry["year"] = year
                continue

            # If we have a current entry, try to extract missing info from this line
            if current_entry:
                # Check for year if we don't have one yet
                if "year" not in current_entry:
                    year = self._extract_year(line)
                    if year:
                        current_entry["year"] = year

                # Check for institution if we don't have one yet
                if "institution" not in current_entry and is_institution_line:
                    institution = self._extract_institution(line)
                    if institution:
                        current_entry["institution"] = institution

        # Don't forget last entry
        if current_entry and current_entry.get("degree"):
            entries.append(self._create_education(current_entry))

        return entries

    def _extract_degree(self, line: str) -> Optional[str]:
        """Extract degree type from line."""
        lower_line = line.lower()

        for degree_type, keywords in self.degree_patterns.items():
            for keyword in keywords:
                # Use word boundary matching to avoid false positives
                # e.g., "be" should not match "Berkeley"
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, lower_line, re.IGNORECASE):
                    return degree_type

        return None

    def _extract_institution(self, line: str) -> Optional[str]:
        """Extract institution name from line."""
        institution_keywords = ["university", "college", "institute", "school"]
        lower_line = line.lower()

        if any(kw in lower_line for kw in institution_keywords):
            return self._clean_institution_name(line)
        return None

    def _looks_like_institution(self, line: str) -> bool:
        """Check if line looks like an institution name."""
        institution_keywords = ["university", "college", "institute", "school", "academy"]
        return any(kw in line.lower() for kw in institution_keywords)

    def _clean_institution_name(self, line: str) -> str:
        """Clean institution name by removing dates and extra info."""
        # Remove date patterns
        clean = re.sub(r"\|\s*\w+\.?\s*\d{4}", "", line)
        clean = re.sub(r"\|\s*\d{4}", "", clean)
        # Remove GPA
        clean = re.sub(r"\|\s*GPA.*$", "", clean, flags=re.IGNORECASE)
        # Remove pipe and anything after
        if "|" in clean:
            clean = clean.split("|")[0]
        return clean.strip()

    def _extract_year(self, line: str) -> Optional[str]:
        """Extract graduation year from line."""
        match = re.search(Patterns.YEAR, line)
        if match:
            return match.group()
        return None

    def _extract_field_of_study(self, line: str) -> Optional[str]:
        """Extract field of study from degree line."""
        # Common patterns: "Bachelor of Science in Computer Science"
        # "B.S. in Computer Science", "MBA in Finance"

        # Special case for MBA - "Master of Business Administration"
        if "business administration" in line.lower():
            return "Business Administration"

        # Pattern 1: "Bachelor/Master of [Subject] in [Field]"
        # e.g., "Bachelor of Science in Computer Science", "Master of Arts in Psychology"
        pattern1 = r"(?:bachelor|master)(?:'?s?)?\s+of\s+(?:science|arts)\s+in\s+([A-Z][a-zA-Z\s&]+?)(?:\s*\(|\s*\||,|\s+from|\s+at|$)"
        match = re.search(pattern1, line, re.IGNORECASE)
        if match:
            field = match.group(1).strip()
            field = re.sub(r"\s*(?:degree|program|studies)$", "", field, flags=re.IGNORECASE)
            if len(field) > 2:
                return field

        # Pattern 2: "of [Field]" after degree type
        # e.g., "Bachelor of Computer Science", "Master of Engineering"
        pattern2 = r"(?:bachelor|master|doctor)(?:'?s?)?\s+of\s+([A-Z][a-zA-Z\s&]+?)(?:\s*\(|\s*\||,|\s+from|\s+at|$)"
        match = re.search(pattern2, line, re.IGNORECASE)
        if match:
            field = match.group(1).strip()
            field = re.sub(r"\s*(?:degree|program|studies)$", "", field, flags=re.IGNORECASE)
            # Don't return generic degree types
            if field.lower() not in ["science", "arts"] and len(field) > 2:
                return field

        # Pattern 3: Direct field after degree abbreviation: "B.S. Computer Science"
        pattern3 = r"(?:B\.?S\.?|B\.?A\.?|M\.?S\.?|M\.?A\.?|MBA|Ph\.?D\.?)\s+(?:in\s+)?([A-Z][a-zA-Z\s&]+?)(?:\s*\||,|$)"
        match = re.search(pattern3, line)
        if match:
            field = match.group(1).strip()
            if len(field) > 2:
                return field

        # Pattern 4: "in [Field]" standalone
        pattern4 = r"\bin\s+([A-Z][a-zA-Z\s&]+?)(?:\s*\||,|\s+from|\s+at|\s+University|\s+College|$)"
        match = re.search(pattern4, line)
        if match:
            field = match.group(1).strip()
            if field.lower() not in ["science", "arts", "business", "engineering"] and len(field) > 2:
                return field

        return None

    def _create_education(self, data: dict) -> Education:
        """Create Education object from parsed data."""
        return Education(
            degree=data.get("degree"),
            field_of_study=data.get("field"),
            institution=data.get("institution"),
            graduation_year=data.get("year"),
        )
