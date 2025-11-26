"""Contact/profile information extractor."""

import re
import logging
from typing import Optional

from app.models.extraction import ContactInfo
from app.constants import Patterns

logger = logging.getLogger(__name__)

# US States mapping for validation
US_STATES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"
}


class ContactExtractor:
    """Extract contact information from resume text."""

    def extract(self, text: str) -> ContactInfo:
        """
        Extract contact information from resume text.

        Args:
            text: Raw text content from resume.

        Returns:
            ContactInfo with extracted fields.
        """
        lines = text.strip().split("\n")

        first_name, last_name = self._extract_name(lines)
        email = self._extract_email(text)
        phone = self._extract_phone(text)
        city, state = self._extract_location(text)

        contact = ContactInfo(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            city=city,
            state=state,
        )

        logger.info(f"Extracted contact info: {contact.model_dump(exclude_none=True)}")
        return contact

    def _extract_name(self, lines: list[str]) -> tuple[Optional[str], Optional[str]]:
        """
        Extract first and last name from the first few lines.
        Names typically appear at the very top of a resume.
        """
        for line in lines[:5]:
            line = line.strip()
            if not line:
                continue

            # Skip lines that look like headers or contain common non-name patterns
            if self._is_likely_header(line):
                continue

            # Skip lines with email/phone
            if "@" in line or re.search(Patterns.PHONE_US, line):
                continue

            # Try to extract name - look for 2-4 capitalized words
            words = line.split()
            name_words = []

            for word in words:
                # Clean the word
                clean_word = re.sub(r"[^\w]", "", word)
                if clean_word and clean_word[0].isupper() and clean_word.isalpha():
                    name_words.append(clean_word)
                else:
                    break

            if 2 <= len(name_words) <= 4:
                first_name = name_words[0]
                last_name = name_words[-1]
                logger.debug(f"Found name: {first_name} {last_name}")
                return first_name, last_name

        return None, None

    def _is_likely_header(self, line: str) -> bool:
        """Check if line is likely a section header."""
        header_keywords = [
            "resume", "curriculum vitae", "cv", "contact", "summary",
            "experience", "education", "skills", "objective"
        ]
        lower_line = line.lower()
        return any(kw in lower_line for kw in header_keywords)

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text."""
        match = re.search(Patterns.EMAIL, text, re.IGNORECASE)
        if match:
            email = match.group()
            logger.debug(f"Found email: {email}")
            return email
        return None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text."""
        # Try US format first
        match = re.search(Patterns.PHONE_US, text)
        if match:
            phone = match.group()
            logger.debug(f"Found phone: {phone}")
            return phone

        # Try international format
        match = re.search(Patterns.PHONE_INTL, text)
        if match:
            phone = match.group()
            logger.debug(f"Found phone (intl): {phone}")
            return phone

        return None

    def _extract_location(self, text: str) -> tuple[Optional[str], Optional[str]]:
        """
        Extract city and state from text.
        Common patterns: "City, ST" or "City, ST 12345" or "City, State"
        """
        # Pattern for "City, ST" or "City, ST ZIP"
        location_pattern = r"([A-Z][a-zA-Z\s]+),\s*([A-Z]{2})(?:\s+\d{5})?"
        match = re.search(location_pattern, text)

        if match:
            city = match.group(1).strip()
            state = match.group(2)
            if state in US_STATES:
                logger.debug(f"Found location: {city}, {state}")
                return city, state

        # Try address line pattern
        address_pattern = r"Address:\s*[^,]+,\s*([A-Z][a-zA-Z\s]+),\s*([A-Z]{2})"
        match = re.search(address_pattern, text)
        if match:
            city = match.group(1).strip()
            state = match.group(2)
            if state in US_STATES:
                return city, state

        return None, None

