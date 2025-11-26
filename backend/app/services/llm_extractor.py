"""LLM-based resume extractor using Ollama."""

import logging
import json
import re
from ollama import chat

from app.models.extraction import ExtractedResume, ContactInfo
from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Extract resume information using Ollama LLM."""

    def __init__(self):
        """Initialize LLM extractor with settings from config."""
        self.settings = get_settings()
        self.client = None
        logger.info("LLM extractor initialized")

    def extract(self, text: str) -> ExtractedResume:
        """
        Extract all resume information using LLM.

        Args:
            text: Raw text content from PDF parser.

        Returns:
            ExtractedResume with all extracted and validated fields.
        """
        logger.info("Starting LLM extraction")

        try:
            system_prompt = """You are an expert resume parser. Extract ALL information from the resume and return ONLY valid JSON. Do not include any explanatory text."""

            user_prompt = f"""Extract the following information from this resume and return as JSON:

{{
  "contact": {{
    "first_name": "",
    "last_name": "",
    "email": "",
    "phone": "",
    "city": "",
    "state": ""
  }},
  "education": [
    {{
      "degree": "",
      "field_of_study": "",
      "institution": "",
      "graduation_year": ""
    }}
  ],
  "work_experience": [
    {{
      "job_title": "",
      "company": "",
      "start_date": "",
      "end_date": "",
      "description": []
    }}
  ],
  "skills": []
}}

Rules:
- Extract ALL education entries (multiple if present)
- Extract ALL work experience entries (multiple if present)
- For work experience descriptions, include each bullet point as an array item
- For skills, extract all technical skills, programming languages, frameworks, and tools
- If a field is not found, use empty string or empty array
- Return ONLY the JSON object, no other text

Resume text:
{text}

JSON:"""

            response = self._generate(user_prompt, system_prompt)
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            result = ExtractedResume(**data, raw_text=text)

            logger.info(
                f"LLM extraction complete: "
                f"contact={bool(result.contact.first_name)}, "
                f"education={len(result.education)}, "
                f"experience={len(result.work_experience)}, "
                f"skills={len(result.skills)}"
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return self._empty_result(text)

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._empty_result(text)

    def _generate(self, prompt: str, system_prompt: str) -> str:
        """
        Generate completion from Ollama model.

        Args:
            prompt: The user prompt to send to the model.
            system_prompt: System prompt for context.

        Returns:
            Generated text response from the model.
        """
        logger.debug(
            f"Calling Ollama with model={self.settings.LLM_MODEL_NAME}, "
            f"temp={self.settings.LLM_TEMPERATURE}"
        )

        response = chat(
            model=self.settings.LLM_MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            stream=False,
            options={
                'temperature': self.settings.LLM_TEMPERATURE,
                'num_predict': 2048,
            }
        )

        return response.message.content

    def _extract_json(self, text: str) -> str:
        """
        Extract JSON from text that might be wrapped in markdown code blocks.

        Args:
            text: Raw text potentially containing JSON.

        Returns:
            Cleaned JSON string.
        """
        text = text.strip()

        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = text

        # Clean invalid control characters from JSON string
        # Replace control characters except for newline, tab, and carriage return
        json_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', json_str)

        return json_str

    def _empty_result(self, text: str) -> ExtractedResume:
        """
        Return empty extraction result.

        Args:
            text: Raw text to include.

        Returns:
            Empty ExtractedResume.
        """
        return ExtractedResume(
            contact=ContactInfo(),
            education=[],
            work_experience=[],
            skills=[],
            raw_text=text,
        )
