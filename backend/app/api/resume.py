"""Resume parsing API endpoints."""

import tempfile
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel, Field

from app.config import get_settings
from app.services.pdf_parser import PDFParserService
from app.services.extraction_pipeline import ExtractionPipeline
from app.utils.exceptions import PDFExtractionError

logger = logging.getLogger(__name__)
router = APIRouter()


class ContactResponse(BaseModel):
    """Contact information response."""

    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    city: str = ""
    state: str = ""


class EducationResponse(BaseModel):
    """Education entry response."""

    degree: str = ""
    field_of_study: str = ""
    institution: str = ""
    graduation_year: str = ""


class WorkExperienceResponse(BaseModel):
    """Work experience entry response."""

    job_title: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    description: list[str] = Field(default_factory=list)


class ResumeParseResponse(BaseModel):
    """Complete parsed resume response."""

    contact: ContactResponse = Field(default_factory=ContactResponse)
    education: list[EducationResponse] = Field(default_factory=list)
    work_experience: list[WorkExperienceResponse] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)


# Initialize services
pdf_parser = PDFParserService()
extraction_pipeline = ExtractionPipeline()


@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume(
    file: UploadFile = File(..., description="PDF file to parse"),
    use_ocr: bool = Query(False, description="Use OCR for scanned documents"),
) -> ResumeParseResponse:
    """
    Parse a PDF resume and extract structured data.

    Accepts a PDF file and returns extracted contact information,
    education, work experience, and skills.
    """
    settings = get_settings()

    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    # Read and validate file size
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB",
        )

    # Create temp file and process
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            # Parse PDF
            logger.info(f"Parsing PDF: {file.filename} ({file_size_mb:.2f}MB)")
            parsed = await pdf_parser.parse_document(
                tmp_path,
                use_ocr=use_ocr,
                ocr_backend=settings.DEFAULT_OCR_BACKEND.value,
            )

            # Extract resume data
            extracted = extraction_pipeline.extract(parsed.content)

            # Build response with empty string defaults
            contact = ContactResponse(
                first_name=extracted.contact.first_name or "",
                last_name=extracted.contact.last_name or "",
                email=extracted.contact.email or "",
                phone=extracted.contact.phone or "",
                city=extracted.contact.city or "",
                state=extracted.contact.state or "",
            )

            education = [
                EducationResponse(
                    degree=edu.degree or "",
                    field_of_study=edu.field_of_study or "",
                    institution=edu.institution or "",
                    graduation_year=edu.graduation_year or "",
                )
                for edu in extracted.education
            ]

            work_experience = [
                WorkExperienceResponse(
                    job_title=exp.job_title or "",
                    company=exp.company or "",
                    start_date=exp.start_date or "",
                    end_date=exp.end_date or "",
                    description=exp.description or [],
                )
                for exp in extracted.work_experience
            ]

            skills = extracted.skills or []

            logger.info(
                f"Extraction complete: contact={bool(contact.first_name)}, "
                f"education={len(education)}, experience={len(work_experience)}, "
                f"skills={len(skills)}"
            )

            return ResumeParseResponse(
                contact=contact,
                education=education,
                work_experience=work_experience,
                skills=skills,
            )

        finally:
            # Clean up temp file
            tmp_path.unlink(missing_ok=True)

    except PDFExtractionError as e:
        logger.error(f"PDF extraction error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error parsing resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse resume")
