# Data Model Specification

This document outlines the data models and structure used in the Lease Generator application. All models are implemented using Pydantic for validation and serialization.

## Overview

The lease generation system uses a hierarchical data model that breaks down a residential lease agreement into logical components. This modular approach allows for easy validation, editing, and extensibility.

## Core Models

### 1. LeaseParties

Represents the parties involved in the lease agreement.

```python
class LeaseParties(BaseModel):
    landlord_name: str              # Full name of the landlord
    landlord_address: str           # Mailing address of the landlord
    tenant_name: str                # Full name of the primary tenant
    tenant_address: Optional[str]   # Tenant's mailing address
    tenant_email: Optional[str]     # Tenant's email address
```

**Field Descriptions:**
- `landlord_name`: Required. Full legal name of the property owner/landlord
- `landlord_address`: Required. Complete mailing address for legal notices
- `tenant_name`: Required. Full legal name of the primary tenant
- `tenant_address`: Optional. Tenant's current mailing address
- `tenant_email`: Optional. Tenant's email for communications

**Validation Rules:**
- All required string fields must be non-empty
- Email addresses are validated for proper format when provided

### 2. PropertyDetails

Describes the physical characteristics and features of the rental property.

```python
class PropertyDetails(BaseModel):
    mailing_address: str            # Physical address of the rental property
    residence_type: str             # Type of residence (House, Apartment, etc.)
    bedrooms: int                   # Number of bedrooms
    bathrooms: int                  # Number of bathrooms
    furnished: bool = False         # Whether property comes furnished
    appliances: List[str] = []      # List of included appliances
```

**Field Descriptions:**
- `mailing_address`: Required. Complete address of the rental property
- `residence_type`: Required. Property type (e.g., "House", "Apartment", "Condo")
- `bedrooms`: Required. Number of bedrooms (must be >= 0)
- `bathrooms`: Required. Number of bathrooms (must be >= 0, allows decimals like 1.5)
- `furnished`: Optional. Defaults to False (unfurnished)
- `appliances`: Optional. List of appliances included with rental

**Common Appliance Values:**
- "Electric Stove"
- "Refrigerator" 
- "Washer"
- "Dryer"
- "Dishwasher"
- "Microwave"

### 3. LeaseTerms

Contains the financial and temporal terms of the lease.

```python
class LeaseTerms(BaseModel):
    start_date: date                # Lease start date
    end_date: date                  # Lease end date  
    monthly_rent: float             # Monthly rent amount
    security_deposit: float         # Security deposit amount
    pet_deposit: Optional[float]    # Pet deposit (if pets allowed)
    late_fee: float = 20.0         # Late payment fee
    nsf_fee: float = 34.0          # Non-sufficient funds fee
    payment_instructions: str       # How rent should be paid
```

**Field Descriptions:**
- `start_date`: Required. Date when lease term begins
- `end_date`: Required. Date when lease term ends
- `monthly_rent`: Required. Monthly rental amount in USD
- `security_deposit`: Required. Refundable security deposit amount
- `pet_deposit`: Optional. Additional deposit required if pets are allowed
- `late_fee`: Optional. Fee charged for late rent payments (default: $20)
- `nsf_fee`: Optional. Fee for bounced checks (default: $34)
- `payment_instructions`: Required. Text describing how to pay rent

**Validation Rules:**
- `end_date` must be after `start_date`
- All monetary amounts must be >= 0
- `payment_instructions` must be non-empty

### 4. PropertyFeatures

Defines property amenities and policies.

```python
class PropertyFeatures(BaseModel):
    parking_spaces: Optional[int]           # Number of parking spaces
    utilities_included: List[str] = []      # List of included utilities
    smoking_allowed: bool = False           # Whether smoking is permitted
    pets_allowed: bool = False             # Whether pets are allowed
    waterbed_allowed: bool = False         # Whether waterbeds are permitted
```

**Field Descriptions:**
- `parking_spaces`: Optional. Number of parking spaces provided
- `utilities_included`: Optional. List of utilities paid by landlord
- `smoking_allowed`: Optional. Smoking policy (default: not allowed)
- `pets_allowed`: Optional. Pet policy (default: not allowed)
- `waterbed_allowed`: Optional. Waterbed policy (default: not allowed)

**Common Utilities:**
- "Water"
- "Sewer" 
- "Electricity"
- "Gas"
- "Internet"
- "Cable TV"
- "Trash Collection"

### 5. AdditionalTerms

Contains miscellaneous terms and contact information.

```python
class AdditionalTerms(BaseModel):
    early_termination_notice: int = 30              # Days notice required for early termination
    landlord_contact_phone: Optional[str]           # Landlord's phone number
    landlord_contact_email: Optional[str]           # Landlord's email address
    special_conditions: List[str] = []              # Custom lease conditions
```

**Field Descriptions:**
- `early_termination_notice`: Optional. Days of notice required for early termination (default: 30)
- `landlord_contact_phone`: Optional. Landlord's phone number for maintenance/emergencies
- `landlord_contact_email`: Optional. Landlord's email for communications
- `special_conditions`: Optional. List of custom lease terms and conditions

**Special Conditions Examples:**
- "No smoking in common areas"
- "Quiet hours: 10 PM - 8 AM"
- "Tenant responsible for lawn maintenance"
- "No food storage on outdoor deck"

### 6. LeaseConfiguration

Represents a saved lease configuration template that can be reused.

```python
class LeaseConfiguration(BaseModel):
    name: str                               # User-friendly name for the configuration
    description: Optional[str]              # Optional description
    parties: LeaseParties                   # Landlord and tenant template data
    property_details: PropertyDetails       # Property template data
    lease_terms: LeaseTerms                # Financial template data
    property_features: PropertyFeatures     # Amenities template data
    additional_terms: AdditionalTerms       # Miscellaneous template data
    governing_law_state: str = "Vermont"    # Default governing state
    lead_paint_disclosure: bool = False     # Default lead paint setting
    created_at: datetime                    # When configuration was created
    updated_at: datetime                    # When configuration was last modified
```

**Field Descriptions:**
- `name`: Required. User-friendly name for the configuration (e.g., "Standard Apartment Lease")
- `description`: Optional. Brief description of when to use this configuration
- `parties` through `additional_terms`: Template data for all lease components
- `governing_law_state`: Default state law (can be overridden per lease)
- `lead_paint_disclosure`: Default lead paint disclosure setting
- `created_at`: Timestamp when configuration was first saved
- `updated_at`: Timestamp when configuration was last modified

**Usage Pattern:**
1. User fills out lease form with common values
2. Checks "Save configuration" option
3. Provides name and description for the configuration
4. Configuration is saved to local JSON files
5. Future lease forms can load this configuration as a starting point

### 7. LeaseAgreement

The main model that combines all lease components for a specific lease instance.

```python
class LeaseAgreement(BaseModel):
    parties: LeaseParties                   # Landlord and tenant information
    property_details: PropertyDetails       # Property characteristics
    lease_terms: LeaseTerms                # Financial and temporal terms
    property_features: PropertyFeatures     # Amenities and policies
    additional_terms: AdditionalTerms       # Miscellaneous terms
    governing_law_state: str = "Vermont"    # State whose laws govern the lease
    agreement_date: date                    # Date the agreement was made
    lead_paint_disclosure: bool = False     # Whether to include lead paint disclosure
```

**Field Descriptions:**
- `parties`: Required. Contains landlord and tenant information
- `property_details`: Required. Physical property information
- `lease_terms`: Required. Financial and time-based lease terms
- `property_features`: Required. Property amenities and policies
- `additional_terms`: Required. Miscellaneous terms and conditions
- `governing_law_state`: Optional. State law that governs the lease (default: "Vermont")
- `agreement_date`: Required. Date when the agreement was executed
- `lead_paint_disclosure`: Optional. Whether to include federal lead paint disclosure

## Configuration Management

### Configuration Storage
Configurations are stored as JSON files in a local `configs/` directory with the following structure:

**File Naming Convention:**
`{sanitized_name}_{timestamp}.json`

**Example:**
`Standard_Apartment_20241026_143022.json`

**Storage Features:**
- Automatic file naming with timestamps
- JSON serialization with proper date handling
- Configuration listing and deletion
- Safe name sanitization for filesystem compatibility

### Configuration Manager Class
The `ConfigurationManager` class handles all configuration persistence:

```python
class ConfigurationManager:
    def save_configuration(config: LeaseConfiguration) -> str
    def load_configuration(config_id: str) -> Optional[LeaseConfiguration]
    def list_configurations() -> List[Dict[str, str]]
    def delete_configuration(config_id: str) -> bool
```

## Data Flow

### 1. Configuration Creation Flow
1. **Form Completion**: User fills out lease form
2. **Save Option**: User checks "Save configuration" checkbox
3. **Configuration Details**: User provides name and description
4. **Form Submission**: Data is sent to `/generate` endpoint
5. **Configuration Creation**: `LeaseConfiguration` model is created
6. **File Persistence**: Configuration saved to JSON file
7. **Lease Generation**: Normal lease generation continues

### 2. Configuration Loading Flow
1. **Configuration Selection**: User clicks on saved configuration
2. **URL Navigation**: Browser navigates to `/?config_id={id}`
3. **Configuration Loading**: Server loads configuration from file
4. **Form Population**: Configuration data is passed to template
5. **JavaScript Execution**: Form fields are populated automatically

### 3. Form Input → Model Creation
When a user submits the web form, the data flows through these steps:

1. **Form Validation**: FastAPI validates form data types
2. **String Processing**: Comma-separated strings are split into lists
3. **Model Creation**: Data is assembled into nested Pydantic models
4. **Model Validation**: Pydantic validates all constraints and types
5. **Configuration Saving** (optional): Save configuration if requested

### 4. Model → Template Rendering
The model is passed to the Jinja2 template engine:

1. **Model Serialization**: Pydantic model converts to dictionary
2. **Template Processing**: Jinja2 renders HTML using model data
3. **Conditional Logic**: Template shows/hides sections based on model values

### 5. Template → PDF Generation
For PDF output:

1. **HTML Generation**: Template renders complete HTML document
2. **CSS Styling**: WeasyPrint applies print-specific CSS
3. **PDF Creation**: HTML is converted to PDF with proper formatting

## Validation Rules

### Global Rules
- All required fields must be present and non-empty (for strings)
- Date fields must be valid ISO dates
- Numeric fields must be non-negative where appropriate

### Model-Specific Rules
- **LeaseTerms**: End date must be after start date
- **PropertyDetails**: Bedroom/bathroom counts must be >= 0
- **AdditionalTerms**: Early termination notice must be >= 1 day

### Business Logic Validation
- If pets are not allowed, pet deposit should be None or 0
- If no parking provided, parking_spaces should be None or 0
- Lead paint disclosure recommended for properties built before 1978

## Extensibility

### Adding New Fields
1. Update the appropriate Pydantic model
2. Add form field to HTML template
3. Update lease template to display new field
4. Modify form processing in main.py

### Adding New Models
1. Create new Pydantic model in models.py
2. Add as field to LeaseAgreement model
3. Update form and templates to handle new data
4. Update API endpoints to process new model

### Customizing Validation
Pydantic validators can be added to enforce custom business rules:

```python
@validator('end_date')
def end_date_after_start_date(cls, v, values):
    if 'start_date' in values and v <= values['start_date']:
        raise ValueError('End date must be after start date')
    return v
```

## Error Handling

The application handles validation errors at multiple levels:

1. **Form Level**: HTML5 validation for required fields and basic types
2. **Pydantic Level**: Model validation with detailed error messages
3. **Application Level**: Custom business logic validation
4. **Template Level**: Graceful handling of missing optional data

## API Endpoints

The application provides the following configuration-related endpoints:

- `GET /?config_id={id}` - Load form with specific configuration
- `GET /configurations` - List all saved configurations (JSON API)
- `DELETE /configurations/{id}` - Delete a specific configuration
- `POST /generate` - Generate lease and optionally save configuration

## Performance Considerations

- Models use appropriate Python types for memory efficiency
- Optional fields default to None or empty containers
- Large text fields (like special_conditions) use lists for better processing
- Date fields use Python's built-in date type for efficient comparison and formatting
- Configuration files are stored as JSON for fast read/write operations
- Configuration loading is on-demand (not cached) to ensure data consistency