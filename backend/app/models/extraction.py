"""Pydantic models for resume extraction results."""

from pydantic import BaseModel, Field
from typing import Optional


class ContactInfo(BaseModel):
    """Extracted contact/profile information."""

    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State")


class Education(BaseModel):
    """Single education entry."""

    degree: Optional[str] = Field(None, description="Degree obtained")
    field_of_study: Optional[str] = Field(None, description="Field of study/major")
    institution: Optional[str] = Field(None, description="Institution name")
    graduation_year: Optional[str] = Field(None, description="Graduation year")


class WorkExperience(BaseModel):
    """Single work experience entry."""

    job_title: Optional[str] = Field(None, description="Job title")
    company: Optional[str] = Field(None, description="Company name")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date")
    description: Optional[list[str]] = Field(
        default_factory=list, description="Description of responsibilities"
    )


class ExtractedResume(BaseModel):
    """Complete extracted resume data."""

    contact: ContactInfo = Field(default_factory=ContactInfo)
    education: list[Education] = Field(default_factory=list)
    work_experience: list[WorkExperience] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    raw_text: Optional[str] = Field(None, description="Original extracted text")
