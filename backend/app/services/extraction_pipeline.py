"""Extraction pipeline to orchestrate all resume extractors."""

import logging

from app.models.extraction import ExtractedResume
from app.services.contact_extractor import ContactExtractor
from app.services.education_extractor import EducationExtractor
from app.services.experience_extractor import ExperienceExtractor
from app.services.skills_extractor import SkillsExtractor

logger = logging.getLogger(__name__)


class ExtractionPipeline:
    """Orchestrate extraction of all resume sections."""

    def __init__(self):
        """Initialize all extractors."""
        self.contact_extractor = ContactExtractor()
        self.education_extractor = EducationExtractor()
        self.experience_extractor = ExperienceExtractor()
        self.skills_extractor = SkillsExtractor()
        logger.info("Extraction pipeline initialized")

    def extract(self, text: str) -> ExtractedResume:
        """
        Extract all information from resume text.

        Args:
            text: Raw text content from PDF parser.

        Returns:
            ExtractedResume with all extracted fields.
        """
        logger.info("Starting extraction pipeline")

        # Extract each section
        contact = self.contact_extractor.extract(text)
        education = self.education_extractor.extract(text)
        work_experience = self.experience_extractor.extract(text)
        skills = self.skills_extractor.extract(text)

        # Build result
        result = ExtractedResume(
            contact=contact,
            education=education,
            work_experience=work_experience,
            skills=skills,
            raw_text=text,
        )

        logger.info(
            f"Extraction complete: "
            f"contact={bool(contact.first_name)}, "
            f"education={len(education)}, "
            f"experience={len(work_experience)}, "
            f"skills={len(skills)}"
        )

        return result

    def extract_to_dict(self, text: str) -> dict:
        """
        Extract and return as dictionary (for JSON serialization).

        Args:
            text: Raw text content from PDF parser.

        Returns:
            Dictionary with all extracted fields.
        """
        result = self.extract(text)
        return result.model_dump(exclude_none=True, exclude={"raw_text"})
