"""PDF parsing service with text extraction and OCR support."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import asyncio
from kreuzberg import extract_file, extract_file_sync, ExtractionConfig, TesseractConfig, PaddleOCRConfig
from tenacity import retry, stop_after_attempt, wait_exponential

from app.constants import ParserType, OCRBackend
from app.utils.exceptions import PDFExtractionError

logger = logging.getLogger(__name__)


@dataclass
class ParsedPDF:
    """Result of PDF parsing."""

    content: str
    page_count: int
    method: str


class BaseParser(ABC):
    """Base class for PDF parsers."""

    @abstractmethod
    async def parse(self, file_path: Path | str) -> ParsedPDF:
        """
        Parse a PDF file and extract content.

        Args:
            file_path: Path to the PDF file.

        Returns:
            ParsedPDF with extracted content.
        """
        pass


class TextParser(BaseParser):
    """Parser using standard text extraction."""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def parse(self, file_path: Path | str) -> ParsedPDF:
        """
        Extract text from PDF using standard text extraction.

        Args:
            file_path: Path to the PDF file.

        Returns:
            ParsedPDF with extracted content.
        """
        try:
            result = await extract_file(str(file_path))

            return ParsedPDF(
                content=result.content,
                page_count=getattr(result, "page_count", 1),
                method=ParserType.TEXT.value,
            )
        except Exception as e:
            logger.exception(f"Text extraction failed: {str(e)}")
            raise PDFExtractionError(f"Text extraction failed: {str(e)}")


class OCRParser(BaseParser):
    """Parser using OCR for scanned documents."""

    def __init__(self, backend: str = OCRBackend.TESSERACT.value):
        """Initialize OCR parser with specified backend."""
        self.backend = backend
        if backend == OCRBackend.TESSERACT.value:
            self.config = ExtractionConfig(ocr_config=TesseractConfig())
        else:
            self.config = ExtractionConfig(ocr_config=PaddleOCRConfig())
        logger.info(f"OCR parser initialized with {backend}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def parse(self, file_path: Path | str) -> ParsedPDF:
        """
        Extract text from PDF using OCR.

        Args:
            file_path: Path to the PDF file.

        Returns:
            ParsedPDF with extracted content.
        """
        try:
            # Use extract_file_sync for OCR (required for OCR to work properly)
            result = await asyncio.to_thread(
                lambda: extract_file_sync(str(file_path), config=self.config)
            )

            return ParsedPDF(
                content=result.content,
                page_count=getattr(result, "page_count", 1),
                method=self.backend,
            )
        except Exception as e:
            logger.exception(f"{self.backend} OCR extraction failed: {str(e)}")
            raise PDFExtractionError(f"{self.backend} OCR extraction failed: {str(e)}")


class PDFParserService:
    """Service for parsing PDF documents."""

    def __init__(self):
        """Initialize the parser service."""
        self.text_parser = TextParser()
        logger.info("PDF parser service initialized")

    async def parse_document(
        self,
        file_path: Path | str,
        use_ocr: bool = False,
        ocr_backend: str = OCRBackend.TESSERACT.value,
    ) -> ParsedPDF:
        """
        Parse a PDF document.

        Args:
            file_path: Path to the PDF file.
            use_ocr: If True, use OCR for extraction. If False, use text extraction.
            ocr_backend: OCR backend to use when use_ocr is True ("Tesseract" or "Paddle").

        Returns:
            ParsedPDF with extracted content.
        """
        try:
            if use_ocr:
                parser = OCRParser(backend=ocr_backend)
            else:
                parser = self.text_parser
            logger.info(f"Parsing document with {ocr_backend if use_ocr else 'text'} parser")

            parsed_content = await parser.parse(file_path)

            logger.info(
                f"Document parsed successfully, "
                f"extracted {len(parsed_content.content)} characters"
            )
            return parsed_content

        except PDFExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error parsing document: {str(e)}")
            raise PDFExtractionError(f"Failed to parse document: {str(e)}")
