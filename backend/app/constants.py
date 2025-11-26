"""Application constants - no magic strings in business logic."""

from enum import Enum


class ParserType(Enum):
    """Available PDF parser types."""

    TEXT = "text"
    OCR = "ocr"


class OCRBackend(Enum):
    """Available OCR backends."""

    TESSERACT = "Tesseract"
    PADDLE = "Paddle"


class ExtractionMethod(Enum):
    """Available extraction methods."""

    REGEX = "regex"
    LLM = "llm"
    HYBRID = "hybrid"


class Patterns:
    """Regex patterns for extraction."""

    EMAIL = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    PHONE_US = r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    PHONE_INTL = r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}"
    LINKEDIN = r"linkedin\.com/in/[\w-]+"
    GITHUB = r"github\.com/[\w-]+"
    DATE_RANGE = r"(\w+\.?\s*\d{4})\s*(?:-|to)\s*(\w+\.?\s*\d{4}|present|current)"
    YEAR = r"\b(19|20)\d{2}\b"
    GPA = r"\b([0-3]\.\d{1,2}|4\.0{1,2})\s*(?:/\s*4\.0?)?\s*GPA\b"
    STATE_ABBREV = r"\b[A-Z]{2}\b"
    ZIP_CODE = r"\b\d{5}(?:-\d{4})?\b"


class SectionHeaders:
    """Section header keywords."""

    EDUCATION = ["education", "academic background", "academic", "qualifications"]
    EXPERIENCE = [
        "work experience", "professional experience", "employment history",
        "employment", "work history", "career history", "experience"
    ]
    SKILLS = [
        "technical skills", "skills","technologies"
    ]
    CONTACT = ["contact", "personal information", "personal details"]
    SUMMARY = [
        "professional summary", "summary", "objective", "career objective",
        "profile", "about me", "overview", "executive summary"
    ]
    PROJECTS = ["projects", "portfolio", "personal projects", "key projects"]
    CERTIFICATIONS = ["certifications", "certificates", "licenses", "credentials"]

    # Headers to exclude when finding sections (these appear within other sections)
    EXCLUDE_FROM_EXPERIENCE = ["professional summary", "summary", "objective", "profile"]


class Confidence:
    """Confidence score thresholds."""

    HIGH = 0.90
    MEDIUM = 0.70
    LOW = 0.50
    VERY_LOW = 0.30


class Degrees:
    """Degree keyword patterns."""

    BACHELORS = ["bachelor", "b.s.", "b.a.", "bs", "ba", "b.sc", "bsc", "b.e.", "be"]
    MASTERS = ["master", "m.s.", "m.a.", "ms", "ma", "m.sc", "msc", "mba", "m.e.", "me"]
    DOCTORATE = ["ph.d", "phd", "doctorate", "doctor of", "d.phil"]
    ASSOCIATE = ["associate", "a.s.", "a.a.", "as", "aa"]


class JobTitleKeywords:
    """Common job title keywords."""

    ENGINEERING = ["engineer", "developer", "architect", "programmer", "swe"]
    MANAGEMENT = ["manager", "director", "lead", "head", "chief", "vp", "president"]
    DESIGN = ["designer", "ux", "ui", "creative", "graphic"]
    DATA = ["analyst", "scientist", "data engineer", "ml", "machine learning"]
    PRODUCT = ["product manager", "product owner", "pm", "po"]
