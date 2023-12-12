from utils.parsing import NoRaiseBaseModel
from typing import Optional, Sequence

from pydantic import BaseModel, Field, StrictStr


class ResumeLocation(NoRaiseBaseModel):
    formatted_location: Optional[StrictStr]  # Affinda ?
    postal_code: Optional[StrictStr]  # All
    region: Optional[StrictStr]  # All
    country: Optional[StrictStr]  # Affinda
    country_code: Optional[StrictStr]  # All
    raw_input_location: Optional[StrictStr]  # All
    street: Optional[StrictStr]  # Affinda
    street_number: Optional[StrictStr]  # Affinda
    appartment_number: Optional[StrictStr]  # Affinda
    city: Optional[str]  # All


class ResumeSkill(NoRaiseBaseModel):
    name: StrictStr
    type: Optional[StrictStr]


class ResumeLang(NoRaiseBaseModel):
    name: StrictStr
    code: Optional[StrictStr]


class ResumeWorkExpEntry(NoRaiseBaseModel):
    title: Optional[StrictStr]
    start_date: Optional[StrictStr]
    end_date: Optional[StrictStr]
    company: Optional[StrictStr]
    location: Optional[ResumeLocation]
    description: Optional[StrictStr]
    industry: Optional[StrictStr]  # Hireability


class ResumeWorkExp(NoRaiseBaseModel):
    total_years_experience: Optional[StrictStr]  # Affinda
    entries: Sequence[ResumeWorkExpEntry] = Field(default_factory=list)


class ResumeEducationEntry(NoRaiseBaseModel):
    title: Optional[StrictStr]
    start_date: Optional[StrictStr]
    end_date: Optional[StrictStr]
    location: Optional[ResumeLocation]
    establishment: Optional[StrictStr]  # All
    description: Optional[StrictStr]
    gpa: Optional[StrictStr]  # Hireability
    accreditation: Optional[StrictStr]  # Affinda


class ResumeEducation(NoRaiseBaseModel):
    total_years_education: Optional[int]
    entries: Sequence[ResumeEducationEntry] = Field(default_factory=list)


class ResumePersonalName(NoRaiseBaseModel):
    first_name: Optional[StrictStr]  # all
    last_name: Optional[StrictStr]  # all
    raw_name: Optional[StrictStr]  # all
    middle: Optional[StrictStr]  # all
    title: Optional[StrictStr]  # Affinda
    prefix: Optional[StrictStr]  # Affinda
    sufix: Optional[StrictStr]  # Affinda


class ResumePersonalInfo(NoRaiseBaseModel):
    name: ResumePersonalName
    address: ResumeLocation
    self_summary: Optional[StrictStr]  # all
    objective: Optional[StrictStr]  # Hireability
    date_of_birth: Optional[StrictStr]  # Affinda
    place_of_birth: Optional[StrictStr]  # Hireability
    phones: Sequence[str] = Field(default_factory=list)
    mails: Sequence[str] = Field(default_factory=list)
    urls: Sequence[str] = Field(default_factory=list)
    fax: Sequence[str] = Field(default_factory=list)
    current_profession: Optional[StrictStr]  # ??
    gender: Optional[StrictStr]  # Hireability
    nationality: Optional[StrictStr]  # Hireability
    martial_status: Optional[StrictStr]  # Hireability
    current_salary: Optional[StrictStr]  # Hireability


class ResumeExtractedData(NoRaiseBaseModel):
    personal_infos: ResumePersonalInfo
    education: ResumeEducation
    work_experience: ResumeWorkExp
    languages: Sequence[ResumeLang] = Field(default_factory=list)
    skills: Sequence[ResumeSkill] = Field(default_factory=list)
    certifications: Sequence[ResumeSkill] = Field(default_factory=list)
    courses: Sequence[ResumeSkill] = Field(default_factory=list)
    publications: Sequence[ResumeSkill] = Field(default_factory=list)
    interests: Sequence[ResumeSkill] = Field(default_factory=list)


class ResumeParserDataClass(NoRaiseBaseModel):
    extracted_data: ResumeExtractedData
