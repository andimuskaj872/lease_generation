from datetime import datetime, date
from .models import (
    LeaseConfiguration, LeaseParties, PropertyDetails, 
    LeaseTerms, PropertyFeatures, AdditionalTerms, SecurityDepositDetails
)

def get_default_templates():
    """Return a list of default configuration templates"""
    
    templates = []
    
    # Standard Apartment Template
    apartment_template = LeaseConfiguration(
        name="Standard Apartment Lease",
        description="Basic apartment lease template with common terms",
        parties=LeaseParties(
            landlord_name="[Landlord Name]",
            landlord_address="[Landlord Address]",
            tenant_name="[Tenant Name]",
            tenant_address="",
            tenant_email="",
            has_occupants=False,
            occupants=None
        ),
        property_details=PropertyDetails(
            mailing_address="[Property Address]",
            residence_type="Apartment",
            bedrooms=2,
            bathrooms=1,
            furnished=False,
            appliances=["Refrigerator", "Electric Stove", "Dishwasher"]
        ),
        lease_terms=LeaseTerms(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            monthly_rent=1200.00,
            pet_deposit=None,
            late_fee=25.00,
            nsf_fee=35.00,
            payment_instructions="Mail check to landlord address or pay via online portal"
        ),
        property_features=PropertyFeatures(
            parking_spaces=1,
            utilities_included=["Water", "Sewer", "Trash Collection"],
            smoking_allowed=False,
            pets_allowed=False,
            waterbed_allowed=False
        ),
        additional_terms=AdditionalTerms(
            early_termination_notice=30,
            landlord_contact_phone="[Phone Number]",
            landlord_contact_email="[Email Address]",
            special_conditions=[
                "Quiet hours: 10 PM - 8 AM",
                "No smoking in common areas"
            ]
        ),
        governing_law_state="Vermont",
        lead_paint_disclosure=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    templates.append(apartment_template)
    
    # House Rental Template
    house_template = LeaseConfiguration(
        name="Single Family House Lease",
        description="Template for single family house rentals with yard maintenance",
        parties=LeaseParties(
            landlord_name="[Landlord Name]",
            landlord_address="[Landlord Address]",
            tenant_name="[Tenant Name]",
            tenant_address="",
            tenant_email="",
            has_occupants=False,
            occupants=None
        ),
        property_details=PropertyDetails(
            mailing_address="[Property Address]",
            residence_type="House",
            bedrooms=3,
            bathrooms=2,
            furnished=False,
            appliances=["Refrigerator", "Electric Stove", "Washer", "Dryer", "Dishwasher"]
        ),
        lease_terms=LeaseTerms(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            monthly_rent=1800.00,
            pet_deposit=None,
            late_fee=50.00,
            nsf_fee=35.00,
            payment_instructions="Mail check to landlord address or pay via online portal"
        ),
        property_features=PropertyFeatures(
            parking_spaces=2,
            utilities_included=["Water", "Sewer"],
            smoking_allowed=False,
            pets_allowed=True,
            waterbed_allowed=False
        ),
        additional_terms=AdditionalTerms(
            early_termination_notice=60,
            landlord_contact_phone="[Phone Number]",
            landlord_contact_email="[Email Address]",
            special_conditions=[
                "Tenant responsible for lawn maintenance",
                "Snow removal required for walkways and driveway",
                "Pet deposit of $300 required if pets are approved"
            ]
        ),
        governing_law_state="Vermont",
        lead_paint_disclosure=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    templates.append(house_template)
    
    # Pet-Friendly Apartment Template
    pet_friendly_template = LeaseConfiguration(
        name="Pet-Friendly Apartment Lease",
        description="Apartment lease template that allows pets with appropriate policies",
        parties=LeaseParties(
            landlord_name="[Landlord Name]",
            landlord_address="[Landlord Address]",
            tenant_name="[Tenant Name]",
            tenant_address="",
            tenant_email="",
            has_occupants=False,
            occupants=None
        ),
        property_details=PropertyDetails(
            mailing_address="[Property Address]",
            residence_type="Apartment",
            bedrooms=2,
            bathrooms=1,
            furnished=False,
            appliances=["Refrigerator", "Electric Stove"]
        ),
        lease_terms=LeaseTerms(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            monthly_rent=1350.00,
            pet_deposit=250.00,
            late_fee=25.00,
            nsf_fee=35.00,
            payment_instructions="Mail check to landlord address or pay via online portal"
        ),
        property_features=PropertyFeatures(
            parking_spaces=1,
            utilities_included=["Water", "Sewer"],
            smoking_allowed=False,
            pets_allowed=True,
            waterbed_allowed=False
        ),
        additional_terms=AdditionalTerms(
            early_termination_notice=30,
            landlord_contact_phone="[Phone Number]",
            landlord_contact_email="[Email Address]",
            special_conditions=[
                "Maximum 2 pets allowed with written approval",
                "Pets must be registered with landlord",
                "Pet waste must be cleaned immediately",
                "Aggressive breed restrictions apply"
            ]
        ),
        governing_law_state="Vermont",
        lead_paint_disclosure=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    templates.append(pet_friendly_template)
    
    # Furnished Studio Template
    furnished_template = LeaseConfiguration(
        name="Furnished Studio Apartment",
        description="Short-term furnished studio with utilities included",
        parties=LeaseParties(
            landlord_name="[Landlord Name]",
            landlord_address="[Landlord Address]",
            tenant_name="[Tenant Name]",
            tenant_address="",
            tenant_email="",
            has_occupants=False,
            occupants=None
        ),
        property_details=PropertyDetails(
            mailing_address="[Property Address]",
            residence_type="Apartment",
            bedrooms=0,  # Studio
            bathrooms=1,
            furnished=True,
            appliances=["Refrigerator", "Electric Stove", "Microwave", "Washer", "Dryer"]
        ),
        lease_terms=LeaseTerms(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 30),  # 6-month lease
            monthly_rent=1500.00,
            custom_security_deposit=1000.00,
            pet_deposit=None,
            late_fee=50.00,
            nsf_fee=35.00,
            payment_instructions="Mail check to landlord address or pay via online portal"
        ),
        property_features=PropertyFeatures(
            parking_spaces=0,
            utilities_included=["Water", "Sewer", "Electricity", "Internet", "Cable TV"],
            smoking_allowed=False,
            pets_allowed=False,
            waterbed_allowed=False
        ),
        additional_terms=AdditionalTerms(
            early_termination_notice=30,
            landlord_contact_phone="[Phone Number]",
            landlord_contact_email="[Email Address]",
            special_conditions=[
                "Furnished unit - inventory list attached",
                "No alterations to furnishings allowed",
                "Professional cleaning required at move-out"
            ]
        ),
        governing_law_state="Vermont",
        lead_paint_disclosure=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    templates.append(furnished_template)
    
    # Vermont Property Template (based on your original lease)
    vermont_template = LeaseConfiguration(
        name="Vermont Property - Andi Muskaj",
        description="Template based on your original 177 Tunnel Street lease agreement",
        parties=LeaseParties(
            landlord_name="Andi Muskaj",
            landlord_address="41-42 24th Street, Unit 405, Long Island City, NY 11101",
            tenant_name="[Tenant Name]",
            tenant_address="[Tenant Address]",
            tenant_email="[Tenant Email]",
            has_occupants=False,
            occupants=None
        ),
        property_details=PropertyDetails(
            mailing_address="177 Tunnel Street, Unit 1, Readsboro, VT 05350",
            residence_type="Apartment",
            bedrooms=3,
            bathrooms=1,
            furnished=False,
            appliances=["Electric Stove", "Refrigerator", "Washer", "Dryer"]
        ),
        lease_terms=LeaseTerms(
            start_date=date(2024, 1, 8),
            end_date=date(2025, 1, 31),
            monthly_rent=975.00,
            pet_deposit=250.00,
            late_fee=20.00,
            nsf_fee=34.00,
            payment_instructions="Mail check to Andi Muskaj at 41-42 24th Street, Unit 405, Long Island City, NY 11101 OR Friends & Family Paypal to 177tunnelstreet@gmail.com"
        ),
        property_features=PropertyFeatures(
            parking_spaces=2,  # 2 parking spaces, vertical (back to back)
            utilities_included=["Water", "Sewer", "Electricity"],
            smoking_allowed=False,
            pets_allowed=True,
            waterbed_allowed=False
        ),
        additional_terms=AdditionalTerms(
            early_termination_notice=30,
            landlord_contact_phone="646-421-4517",
            landlord_contact_email="177tunnelstreet@gmail.com",
            special_conditions=[
                "Outdoor deck - No food or trash should be stored on the porch to avoid attracting animals",
                "Outdoor deck - Should not be used as storage", 
                "No storage allowed anywhere in the common areas (hallways, stairs, outdoor areas, basement)",
                "Attic shall not be accessible to the Tenant",
                "Basement shall only be accessible to Tenants for access to the circuit breakers",
                "A security camera system monitoring the outside of the building and common areas will be installed and maintained by the Landlord",
                "Yearly inspection of the home will be conducted with proper notice",
                "Garbage and rubbish shall be removed from dwellings as often as necessary to maintain sanitary structure, not less than once every week"
            ]
        ),
        governing_law_state="Vermont",
        lead_paint_disclosure=True,  # Property built prior to 1978
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    templates.append(vermont_template)
    
    return templates