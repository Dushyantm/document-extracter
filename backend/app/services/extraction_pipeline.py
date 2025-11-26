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
        logger.info("Regex extraction pipeline initialized")

    def extract(self, text: str) -> ExtractedResume:
        """
        Extract all information from resume text using regex patterns.

        Args:
            text: Raw text content from PDF parser.

        Returns:
            ExtractedResume with all extracted fields.
        """
        logger.info("Starting regex extraction pipeline")
        warnings = []

        try:
            contact = self.contact_extractor.extract(text)
        except Exception as e:
            logger.warning(f"Contact extraction failed: {e}")
            warnings.append(f"Contact extraction failed: {str(e)}")
            from app.models.extraction import ContactInfo
            contact = ContactInfo()

        try:
            education = self.education_extractor.extract(text)
        except Exception as e:
            logger.warning(f"Education extraction failed: {e}")
            warnings.append(f"Education extraction failed: {str(e)}")
            education = []

        try:
            work_experience = self.experience_extractor.extract(text)
        except Exception as e:
            logger.warning(f"Work experience extraction failed: {e}")
            warnings.append(f"Work experience extraction failed: {str(e)}")
            work_experience = []

        try:
            skills = self.skills_extractor.extract(text)
        except Exception as e:
            logger.warning(f"Skills extraction failed: {e}")
            warnings.append(f"Skills extraction failed: {str(e)}")
            skills = []

        result = ExtractedResume(
            contact=contact,
            education=education,
            work_experience=work_experience,
            skills=skills,
            raw_text=text,
        )

        logger.info(
            f"Regex extraction complete: "
            f"contact={bool(contact.first_name)}, "
            f"education={len(education)}, "
            f"experience={len(work_experience)}, "
            f"skills={len(skills)}, "
            f"warnings={len(warnings)}"
        )

        if warnings:
            logger.warning(f"Extraction warnings: {warnings}")

        return result

    def extract_to_dict(self, text: str) -> dict:
        """
        Extract and return as dictionary for API response.

        Args:
            text: Raw text content from PDF parser.

        Returns:
            Dictionary with all extracted fields.
        """
        return self.extract(text).model_dump(exclude={"raw_text"})
