"""Resume validation service to ensure uploaded PDFs are actually resumes."""

import re
import logging
from typing import Tuple, Optional

from app.constants import SectionHeaders, Patterns
from app.models.extraction import ExtractedResume

logger = logging.getLogger(__name__)


class ResumeValidator:
    """Validates that a document is a resume based on content analysis."""

    # Required patterns that indicate contact information
    CONTACT_PATTERNS = {
        "email": Patterns.EMAIL,
        "phone": Patterns.PHONE_US,
        "linkedin": Patterns.LINKEDIN,
    }

    def __init__(self):
        """Initialize validator."""
        self.min_text_length = 100  # Minimum characters for a valid resume
        self.min_keywords = 2  # Minimum resume-related keywords required

        # Combine all section headers for keyword matching
        self.all_section_keywords = (
            SectionHeaders.EDUCATION +
            SectionHeaders.EXPERIENCE +
            SectionHeaders.SKILLS +
            SectionHeaders.SUMMARY +
            SectionHeaders.PROJECTS +
            SectionHeaders.CERTIFICATIONS
        )

        logger.info("Resume validator initialized")

    def validate(self, text: str) -> Tuple[bool, str]:
        """
        Validate if the text content appears to be from a resume.

        Args:
            text: Extracted text from PDF.

        Returns:
            Tuple of (is_valid, reason) where is_valid is True if it's a resume,
            and reason provides explanation if invalid.
        """
        if not text or len(text.strip()) < self.min_text_length:
            return False, f"Document too short ({len(text)} chars). Resumes typically have at least {self.min_text_length} characters."

        text_lower = text.lower()

        # Check 1: Look for resume section keywords using constants
        keyword_matches = sum(1 for keyword in self.all_section_keywords if keyword in text_lower)

        if keyword_matches < self.min_keywords:
            logger.warning(f"Only {keyword_matches} resume keywords found, minimum is {self.min_keywords}")
            return False, f"Document doesn't appear to be a resume. Found only {keyword_matches} resume-related sections (education, experience, skills, etc.). Please upload a valid resume."

        # Check 2: Look for contact information patterns
        has_contact = False
        contact_types = []

        if re.search(self.CONTACT_PATTERNS["email"], text, re.IGNORECASE):
            has_contact = True
            contact_types.append("email")

        if re.search(self.CONTACT_PATTERNS["phone"], text):
            has_contact = True
            contact_types.append("phone")

        if re.search(self.CONTACT_PATTERNS["linkedin"], text, re.IGNORECASE):
            contact_types.append("linkedin")

        if not has_contact:
            logger.warning("No contact information (email/phone) found")
            return False, "Document doesn't appear to be a resume. No contact information (email or phone) found. Please upload a valid resume."

        # Check 3: Look for name patterns (capitalized words at the start)
        lines = text.strip().split("\n")[:10]  # Check first 10 lines
        has_potential_name = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Look for 2-4 capitalized words (potential name)
            words = re.findall(r'\b[A-Z][a-z]+\b', line)
            if 2 <= len(words) <= 4:
                has_potential_name = True
                break

        # Passed all checks
        logger.info(
            f"Resume validation passed: "
            f"keywords={keyword_matches}, "
            f"contact={contact_types}, "
            f"has_name={has_potential_name}"
        )
        return True, "Valid resume detected"

    def has_sections_but_no_data(self, text: str, extracted_data: ExtractedResume) -> Tuple[bool, str]:
        """
        Check if the resume has section headers but extraction failed to get data.
        This indicates a parsing problem rather than an invalid document.

        Args:
            text: Raw text from PDF.
            extracted_data: Result from extraction pipeline.

        Returns:
            Tuple of (has_headers_but_failed, reason)
        """
        text_lower = text.lower()

        # Check which section headers are present
        has_education_header = any(header in text_lower for header in SectionHeaders.EDUCATION)
        has_experience_header = any(header in text_lower for header in SectionHeaders.EXPERIENCE)
        has_skills_header = any(header in text_lower for header in SectionHeaders.SKILLS)

        # Check if data was actually extracted
        has_education_data = len(extracted_data.education) > 0
        has_experience_data = len(extracted_data.work_experience) > 0
        has_skills_data = len(extracted_data.skills) > 0

        # Count sections with headers but no data
        failed_sections = []

        if has_education_header and not has_education_data:
            failed_sections.append("Education")

        if has_experience_header and not has_experience_data:
            failed_sections.append("Work Experience")

        if has_skills_header and not has_skills_data:
            failed_sections.append("Skills")

        # If we have 2+ section headers but failed to extract from them
        if len(failed_sections) >= 2:
            logger.warning(f"Headers found but extraction failed for: {failed_sections}")
            return True, f"Failed to parse PDF. Found resume sections ({', '.join(failed_sections)}) but couldn't extract data. The PDF format may be incompatible or the content is not structured properly."

        return False, "OK"

    def get_validation_summary(self, text: str) -> dict:
        """
        Get detailed validation summary for debugging.

        Args:
            text: Extracted text from PDF.

        Returns:
            Dictionary with validation details.
        """
        text_lower = text.lower()

        keyword_matches = [kw for kw in self.RESUME_KEYWORDS if kw in text_lower]

        contact_info = {
            "has_email": bool(re.search(self.CONTACT_PATTERNS["email"], text, re.IGNORECASE)),
            "has_phone": bool(re.search(self.CONTACT_PATTERNS["phone"], text)),
            "has_linkedin": bool(re.search(self.CONTACT_PATTERNS["linkedin"], text, re.IGNORECASE)),
        }

        return {
            "text_length": len(text),
            "keyword_count": len(keyword_matches),
            "keywords_found": keyword_matches,
            "contact_info": contact_info,
            "has_minimum_keywords": len(keyword_matches) >= self.min_keywords,
            "has_contact": contact_info["has_email"] or contact_info["has_phone"],
        }
