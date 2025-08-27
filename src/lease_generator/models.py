from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import date, datetime


class LeaseParties(BaseModel):
    landlord_name: str
    landlord_address: str
    tenant_name: str
    tenant_address: Optional[str] = None
    tenant_email: Optional[str] = None
    has_occupants: bool = False
    occupants: Optional[str] = None


class PropertyDetails(BaseModel):
    mailing_address: str
    residence_type: str
    bedrooms: int
    bathrooms: int
    furnished: bool = False
    appliances: List[str] = []


class SecurityDepositDetails(BaseModel):
    previous_rent: Optional[float] = None
    use_custom_section: bool = False


class LeaseTerms(BaseModel):
    start_date: date
    end_date: date
    monthly_rent: float
    custom_security_deposit: Optional[float] = None
    security_deposit_details: Optional[SecurityDepositDetails] = None
    pet_deposit: Optional[float] = None
    late_fee: float = 20.0
    nsf_fee: float = 34.0
    payment_instructions: str


class PropertyFeatures(BaseModel):
    parking_spaces: Optional[int] = None
    utilities_included: List[str] = []
    smoking_allowed: bool = False
    pets_allowed: bool = False
    waterbed_allowed: bool = False


class SpecialCondition(BaseModel):
    title: str
    items: List[str]

class PaymentEntry(BaseModel):
    due_date: Union[date, str]
    rent_amount: float
    security_deposit: float = 0.0
    pet_deposit: float = 0.0
    other_fees: float = 0.0
    total: float
    comment: Optional[str] = None
    is_manual: bool = False  # Flag for manual entries
    entry_number: Optional[int] = None  # For display ordering

class PaymentSchedule(BaseModel):
    include_in_lease: bool = False
    auto_generate: bool = True
    custom_entries: List[PaymentEntry] = []
    rent_increases: List[dict] = []  # List of {date, new_rent} for rent increases
    lease_start_comment: Optional[str] = None  # Comment for the lease start date payment

class AdditionalTerms(BaseModel):
    early_termination_notice: int = 30
    landlord_contact_phone: Optional[str] = None
    landlord_contact_email: Optional[str] = None
    special_conditions: List[Union[str, SpecialCondition]] = []
    payment_schedule: Optional[PaymentSchedule] = None


class LeaseConfiguration(BaseModel):
    parties: LeaseParties
    property_details: PropertyDetails
    lease_terms: LeaseTerms
    property_features: PropertyFeatures
    additional_terms: AdditionalTerms
    governing_law_state: str = "Vermont"
    lead_paint_disclosure: bool = False
    created_at: datetime
    updated_at: datetime


class LeaseAgreement(BaseModel):
    parties: LeaseParties
    property_details: PropertyDetails
    lease_terms: LeaseTerms
    property_features: PropertyFeatures
    additional_terms: AdditionalTerms
    governing_law_state: str = "Vermont"
    agreement_date: date
    lead_paint_disclosure: bool = False