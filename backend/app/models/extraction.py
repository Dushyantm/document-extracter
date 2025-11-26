"""Pydantic models for resume extraction results."""

from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    """Extracted contact/profile information."""

    first_name: str = ""
    last_name: str = ""
    email: str = ""
    phone: str = ""
    city: str = ""
    state: str = ""


class Education(BaseModel):
    """Single education entry."""

    degree: str = ""
    field_of_study: str = ""
    institution: str = ""
    graduation_year: str = ""


class WorkExperience(BaseModel):
    """Single work experience entry."""

    job_title: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    description: list[str] = Field(default_factory=list)


class ExtractedResume(BaseModel):
    """Complete extracted resume data."""

    contact: ContactInfo = Field(default_factory=ContactInfo)
    education: list[Education] = Field(default_factory=list)
    work_experience: list[WorkExperience] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    raw_text: str = ""
