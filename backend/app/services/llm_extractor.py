"""LLM-based resume extractor using Ollama."""

import logging
import json
import re
from ollama import Client

from app.models.extraction import ExtractedResume, ContactInfo
from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Extract resume information using Ollama LLM."""

    def __init__(self):
        """Initialize LLM extractor with settings from config."""
        self.settings = get_settings()
        self.client = Client(host=self.settings.LLM_BASE_URL)
        logger.info(f"LLM extractor initialized with host: {self.settings.LLM_BASE_URL}")

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

            user_prompt = f"""Extract ALL possible resume information from the text below and return ONLY a JSON object in the exact format shown.

You MUST follow ALL of these rules:

1. WORK EXPERIENCE (CRITICAL)
   - You MUST extract EVERY job under the WORK EXPERIENCE (or equivalent) section.
   - This includes ALL roles, even earlier or junior roles.
   - For example, if the text contains:
       "Senior Software Engineer"
       "Software Engineer"
       "Junior Developer"
     then the JSON MUST contain THREE separate work_experience objects.
   - For each role, extract:
       - job_title
       - company
       - start_date in the format of YYYY-MM
       - end_date in the format of YYYY-MM
       - description (array of bullet points)
   - description MUST be an array of strings. Each bullet point in the resume is one array item.
   - If dates or bullets are missing, still create the work_experience entry and use "" or [] for missing fields.
   - Continue collecting work experience until the next major section (e.g., EDUCATION, SKILLS, PROJECTS).

2. EDUCATION
   - Extract ALL education entries.
   - For each entry, extract:
       - degree
       - field_of_study
       - institution
       - graduation_year
   - If multiple degrees or schools exist, include ALL of them as separate objects.
   - If any field is missing, use "".

3. CONTACT INFORMATION
   - Parse and fill:
       - first_name
       - last_name
       - email
       - phone
       - city
       - state
   - If the address line has full address, extract city and state from it if possible.
   - If any field is not present, use "".

4. SKILLS
   - Extract ALL technical skills, including:
       - Programming languages
       - Frameworks and libraries
       - Databases
       - Tools and platforms (e.g., Docker, Git, AWS)
       - Cloud & DevOps technologies
       - Certifications (these SHOULD also be included in the skills array)
   - Flatten the list so that each skill is a separate string.
   - Remove duplicates.
   - If no skills are found, return an empty array [].

5. OUTPUT FORMAT (STRICT)
   - You MUST return ONLY valid JSON.
   - Do NOT include any explanation, comments, or extra text.
   - The JSON MUST match exactly this structure:

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

Resume text:
{text}

JSON:"""
            print(user_prompt)  # print the user prompt to the console
            response = self._generate(user_prompt, system_prompt)
            print(response)  # print the response to the console
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

        response = self.client.chat(
            model=self.settings.LLM_MODEL_NAME,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ],
            stream=False,
            options={
                'temperature': self.settings.LLM_TEMPERATURE,
            }
        )

        return response['message']['content']

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
