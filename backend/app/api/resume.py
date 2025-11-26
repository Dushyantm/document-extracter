"""Resume parsing API endpoints."""

import tempfile
import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Query

from app.config import get_settings
from app.models.extraction import ExtractedResume
from app.services.pdf_parser import PDFParserService
from app.services.extraction_pipeline import ExtractionPipeline
from app.services.llm_extractor import LLMExtractor
from app.services.resume_validator import ResumeValidator
from app.utils.exceptions import PDFExtractionError

logger = logging.getLogger(__name__)
router = APIRouter()

settings = get_settings()
pdf_parser = PDFParserService()
extraction_pipeline = ExtractionPipeline()
llm_extractor = LLMExtractor()
resume_validator = ResumeValidator()


@router.post("/parse", response_model=ExtractedResume, response_model_exclude={"raw_text"})
async def parse_resume(
    file: UploadFile = File(..., description="PDF file to parse"),
    use_ocr: bool = Query(False, description="Use OCR for scanned documents"),
) -> ExtractedResume:
    """
    Parse a PDF resume and extract structured data.

    Accepts a PDF file and returns extracted contact information,
    education, work experience, and skills.
    """
    settings = get_settings()

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB",
        )

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            logger.info(f"Parsing PDF: {file.filename} ({file_size_mb:.2f}MB)")
            parsed = await pdf_parser.parse_document(
                tmp_path,
                use_ocr=use_ocr,
                ocr_backend=settings.DEFAULT_OCR_BACKEND.value,
            )

            # Check if we got any text from the PDF
            if not parsed.content or len(parsed.content.strip()) < 10:
                logger.warning(f"PDF has minimal or no extractable text: {len(parsed.content)} chars")
                raise HTTPException(
                    status_code=422,
                    detail="PDF has no extractable text. Please ensure the file is not corrupted or is a text-based PDF (not a scanned image)."
                )

            # Validate that the document is actually a resume
            is_valid, reason = resume_validator.validate(parsed.content)
            if not is_valid:
                logger.warning(f"Resume validation failed: {reason}")
                raise HTTPException(
                    status_code=422,
                    detail=reason
                )

            # Extract data
            result = extraction_pipeline.extract(parsed.content)

            # Check if we have section headers but extraction failed
            has_failed, failure_reason = resume_validator.has_sections_but_no_data(
                parsed.content, result
            )

            if has_failed:
                logger.error(f"Extraction validation failed: {failure_reason}")
                raise HTTPException(
                    status_code=422,
                    detail=failure_reason
                )

            logger.info(
                f"Extraction complete: contact={bool(result.contact.first_name)}, "
                f"education={len(result.education)}, "
                f"experience={len(result.work_experience)}, "
                f"skills={len(result.skills)}"
            )

            return result

        finally:
            tmp_path.unlink(missing_ok=True)

    except PDFExtractionError as e:
        logger.error(f"PDF extraction error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error parsing resume: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse resume")


@router.post("/parse-llm", response_model=ExtractedResume, response_model_exclude={"raw_text"})
async def parse_resume_llm(
    file: UploadFile = File(..., description="PDF file to parse"),
    use_ocr: bool = Query(False, description="Use OCR for scanned documents"),
) -> ExtractedResume:
    """
    Parse a PDF resume and extract structured data using LLM (Ollama).

    Alternative extraction method using Large Language Model instead of regex patterns.
    Accepts a PDF file and returns extracted contact information,
    education, work experience, and skills.
    """
    settings = get_settings()

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {settings.ALLOWED_EXTENSIONS}",
        )

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB",
        )

    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        try:
            logger.info(f"Parsing PDF with LLM: {file.filename} ({file_size_mb:.2f}MB)")
            parsed = await pdf_parser.parse_document(
                tmp_path,
                use_ocr=use_ocr,
                ocr_backend=settings.DEFAULT_OCR_BACKEND.value,
            )

            if not parsed.content or len(parsed.content.strip()) < 10:
                logger.warning(f"PDF has minimal or no extractable text: {len(parsed.content)} chars")
                raise HTTPException(
                    status_code=422,
                    detail="PDF has no extractable text. Please ensure the file is not corrupted or is a text-based PDF (not a scanned image)."
                )

            is_valid, reason = resume_validator.validate(parsed.content)
            if not is_valid:
                logger.warning(f"Resume validation failed: {reason}")
                raise HTTPException(
                    status_code=422,
                    detail=reason
                )

            result = llm_extractor.extract(parsed.content)

            logger.info(
                f"LLM extraction complete: contact={bool(result.contact.first_name)}, "
                f"education={len(result.education)}, "
                f"experience={len(result.work_experience)}, "
                f"skills={len(result.skills)}"
            )

            return result

        finally:
            tmp_path.unlink(missing_ok=True)

    except PDFExtractionError as e:
        logger.error(f"PDF extraction error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error parsing resume with LLM: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse resume with LLM")
