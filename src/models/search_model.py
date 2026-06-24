from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    state: str = Field(..., description="The State which to search in")
    business_type: Optional[str] = Field(
        None, description="The business type for example Property & Casual"
    )
    type_of_insurance: Optional[List[str]] = Field(
        None , description="The types of insurances to select"
    )
    company_name: Optional[str] = Field(None, description="Name of the company")
    naic_company_code: Optional[str] = Field(None, description="The NAIC company code")
    insurance_product_name: Optional[str] = Field(
        None, description="The Insurance Product name to search"
    )
    serff_tracking_number: Optional[str] = Field(
        None, description="The SERFF tracking number to search for"
    )
    start_submission_date: Optional[str] = Field(
        None, description="The start submission date in format M/D/YY"
    )
    start_disposition_date: Optional[str] = Field(
        None, description="The start disposition date in format M/D/YY"
    )
    end_submission_date: Optional[str] = Field(
        None, description="The end submission date in format M/D/YY"
    )
    end_disposition_date: Optional[str] = Field(
        None, description="The end disposition date in format M/D/YY"
    )
