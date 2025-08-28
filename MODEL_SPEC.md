# Lease Generator - Complete Model & Architecture Specification

This document provides a comprehensive specification for the Lease Generator application, covering data models, architecture, features, and implementation details. This specification should serve as the authoritative guide for understanding and regenerating the application.

## Application Overview

The Lease Generator is a FastAPI-based web application that generates professional residential lease agreements with the following key capabilities:

- **Interactive Web Form**: Clean, responsive form interface with validation
- **JSON Template System**: Upload/download lease configurations as JSON templates
- **Example Template Loading**: Built-in example template with sample data
- **Payment Schedule Generation**: Auto-generate complex payment schedules with rent increases
- **Multiple Output Formats**: HTML preview, PDF download, and renewal message text files
- **Professional Formatting**: Currency formatting, proper date handling, and clean document layout
- **Configuration Management**: Save and reuse lease configurations
- **Renewal Message Generation**: Automated renewal messages with calculated rent increases

## Core Data Models

### 1. LeaseParties

Represents all parties involved in the lease agreement with support for additional occupants.

```python
class LeaseParties(BaseModel):
    landlord_name: str                      # Full name of the landlord
    landlord_address: str                   # Mailing address of the landlord
    tenant_name: str                        # Full name of the primary tenant
    tenant_address: Optional[str] = None    # Tenant's mailing address
    tenant_email: Optional[str] = None      # Tenant's email address
    has_occupants: bool = False             # Whether additional occupants exist
    occupants: Optional[List[str]] = None   # List of additional occupant names
```

**Field Descriptions:**
- `landlord_name`: Required. Full legal name of the property owner/landlord
- `landlord_address`: Required. Complete mailing address for legal notices
- `tenant_name`: Required. Full legal name of the primary tenant
- `tenant_address`: Optional. Tenant's current mailing address
- `tenant_email`: Optional. Tenant's email for communications
- `has_occupants`: Optional. Boolean indicating if additional occupants will live in the property
- `occupants`: Optional. List of additional occupant names (used when has_occupants is True)

**Validation Rules:**
- All required string fields must be non-empty
- Email addresses are validated for proper format when provided
- If has_occupants is True, occupants list should contain at least one name

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

Contains the financial and temporal terms of the lease with enhanced security deposit handling.

```python
class LeaseTerms(BaseModel):
    start_date: date                                    # Lease start date
    end_date: date                                      # Lease end date  
    monthly_rent: float                                 # Monthly rent amount
    custom_security_deposit: Optional[float] = None     # Custom security deposit override
    security_deposit_details: Optional[str] = None      # Security deposit calculation details
    pet_deposit: Optional[float] = None                 # Pet deposit (if pets allowed)
    late_fee: float = 20.0                            # Late payment fee
    nsf_fee: float = 34.0                             # Non-sufficient funds fee
    payment_instructions: str                           # How rent should be paid
```

**Field Descriptions:**
- `start_date`: Required. Date when lease term begins
- `end_date`: Required. Date when lease term ends
- `monthly_rent`: Required. Monthly rental amount in USD
- `custom_security_deposit`: Optional. Override for security deposit calculation
- `security_deposit_details`: Optional. Text explaining security deposit calculation for renewals
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

### 5. PaymentEntry

Represents a single payment entry in the payment schedule.

```python
class PaymentEntry(BaseModel):
    due_date: Union[date, str]          # Payment due date
    rent_amount: float                  # Rent portion of payment
    security_deposit: float = 0.0       # Security deposit portion
    pet_deposit: float = 0.0            # Pet deposit portion
    total: float                        # Total payment amount
    comment: Optional[str] = None       # Comment/description for payment
    is_manual: bool = False             # Whether entry was manually created
    entry_number: Optional[int] = None  # Entry sequence number
```

**Field Descriptions:**
- `due_date`: Required. Date when payment is due
- `rent_amount`: Required. Monthly rent portion of the payment
- `security_deposit`: Optional. Security deposit portion (default: 0.0)
- `pet_deposit`: Optional. Pet deposit portion (default: 0.0)
- `total`: Required. Total amount due for this payment
- `comment`: Optional. Descriptive text for the payment entry
- `is_manual`: Optional. Flag indicating if entry was manually created vs auto-generated
- `entry_number`: Optional. Sequential number for ordering entries

### 6. PaymentSchedule

Configuration for generating and managing payment schedules.

```python
class PaymentSchedule(BaseModel):
    include_in_lease: bool = False              # Whether to include schedule in lease document
    auto_generate: bool = True                  # Whether to auto-generate monthly payments
    custom_entries: List[PaymentEntry] = []     # Manual payment entries
    rent_increases: List[dict] = []             # Scheduled rent increases
    lease_start_comment: Optional[str] = None   # Comment for first lease payment
```

**Field Descriptions:**
- `include_in_lease`: Optional. Whether to include full payment schedule in lease document
- `auto_generate`: Optional. Whether to automatically generate monthly payment entries
- `custom_entries`: Optional. List of manually created payment entries
- `rent_increases`: Optional. List of rent increase configurations with dates and amounts
- `lease_start_comment`: Optional. Special comment for the first lease payment

**Rent Increase Format:**
```python
{
    "date": "2025-06-01",     # Date when increase takes effect
    "amount": 1250.0         # New monthly rent amount
}
```

### 7. AdditionalTerms

Contains miscellaneous terms, contact information, and payment schedule configuration.

```python
class AdditionalTerms(BaseModel):
    early_termination_notice: int = 30              # Days notice required for early termination
    landlord_contact_phone: Optional[str] = None    # Landlord's phone number
    landlord_contact_email: Optional[str] = None    # Landlord's email address
    special_conditions: List[str] = []              # Custom lease conditions
    payment_schedule: PaymentSchedule = PaymentSchedule()  # Payment schedule configuration
```

**Field Descriptions:**
- `early_termination_notice`: Optional. Days of notice required for early termination (default: 30)
- `landlord_contact_phone`: Optional. Landlord's phone number for maintenance/emergencies
- `landlord_contact_email`: Optional. Landlord's email for communications
- `special_conditions`: Optional. List of custom lease terms and conditions (supports plain text)
- `payment_schedule`: Optional. Payment schedule configuration object

**Special Conditions Format:**
Special conditions are stored as plain text strings in a list. Each string can be:
- A section title (e.g., "Property Maintenance")
- A detailed condition (e.g., "- Tenant is responsible for basic upkeep including lawn care and snow removal")
- A policy statement (e.g., "Quiet hours are from 10:00 PM to 8:00 AM")

**Example Special Conditions:**
```python
[
    "Property Maintenance",
    "- Tenant is responsible for basic upkeep including lawn care and snow removal", 
    "- Any maintenance requests must be submitted in writing",
    "Noise Policy",
    "- Quiet hours are from 10:00 PM to 8:00 AM",
    "- No loud music or parties that disturb neighbors"
]
```

### 8. LeaseConfiguration

Represents a saved lease configuration template that can be downloaded as JSON.

```python
class LeaseConfiguration(BaseModel):
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
- `parties` through `additional_terms`: Template data for all lease components
- `governing_law_state`: Default state law (can be overridden per lease)
- `lead_paint_disclosure`: Default lead paint disclosure setting
- `created_at`: Timestamp when configuration was created
- `updated_at`: Timestamp when configuration was last modified

**Usage Pattern:**
1. User fills out lease form
2. Clicks "Download Configuration JSON" button
3. JSON file is automatically downloaded with filename: `lease_configuration_{tenant_name}_{start_date}.json`
4. User can upload this JSON template later to populate the form
5. Example template is also available via "Load Example Template" button

### 9. LeaseAgreement

The main model that combines all lease components for a specific lease instance.

```python
class LeaseAgreement(BaseModel):
    parties: LeaseParties                   # Landlord and tenant information
    property_details: PropertyDetails       # Property characteristics
    lease_terms: LeaseTerms                # Financial and temporal terms
    property_features: PropertyFeatures     # Amenities and policies
    additional_terms: AdditionalTerms       # Miscellaneous terms and payment schedule
    governing_law_state: str = "Vermont"    # State whose laws govern the lease
    lead_paint_disclosure: bool = False     # Whether to include lead paint disclosure
    created_at: datetime                    # When agreement was generated
    updated_at: datetime                    # When agreement was last modified
```

**Field Descriptions:**
- `parties`: Required. Contains landlord and tenant information
- `property_details`: Required. Physical property information
- `lease_terms`: Required. Financial and time-based lease terms
- `property_features`: Required. Property amenities and policies
- `additional_terms`: Required. Miscellaneous terms, conditions, and payment schedule
- `governing_law_state`: Optional. State law that governs the lease (default: "Vermont")
- `lead_paint_disclosure`: Optional. Whether to include federal lead paint disclosure
- `created_at`: Required. Timestamp when agreement was generated
- `updated_at`: Required. Timestamp when agreement was last modified

## Application Architecture

### Technology Stack
- **FastAPI**: Python web framework for the backend API
- **Uvicorn**: ASGI server for running the FastAPI application
- **Jinja2**: Template engine for HTML generation
- **WeasyPrint**: HTML to PDF conversion library
- **Pydantic**: Data validation and serialization
- **Python-multipart**: Form data handling for file uploads

### File Structure
```
lease-generator/
├── src/
│   └── lease_generator/
│       ├── __init__.py              # Package marker
│       ├── main.py                  # FastAPI application and all endpoints
│       ├── models.py                # Pydantic data models
│       └── templates/               # Jinja2 HTML templates
│           ├── form.html            # Main lease creation form
│           ├── lease_template.html  # Lease document template
│           └── edit_form.html       # Lease editing interface (basic)
├── example_template.json            # Example template with sample data
├── pyproject.toml                   # Project configuration and dependencies
├── .python-version                  # Python version specification for pyenv
├── MODEL_SPEC.md                    # This comprehensive specification
└── README.md                        # User documentation and setup guide
```

### Configuration Management

**JSON Template System:**
- No server-side persistence - all configuration is client-side
- Users download JSON configuration files from the browser
- Users upload JSON files to populate the form
- Built-in example template for getting started

**File Naming Convention:**
- Downloaded configs: `lease_configuration_{tenant_name}_{start_date}.json`
- PDFs: `lease_agreement_{tenant_name}_{start_date}.pdf`
- Renewal messages: `renewal_message_{tenant_name}_{start_date}.txt`

**Template Features:**
- Automatic filename generation based on tenant name and lease start date
- Sanitized filenames for filesystem compatibility
- Timestamp metadata (created_at, updated_at) in JSON files
- Full form state preservation in JSON format

## Data Flow & Processing

### 1. Form Population Flow
**Empty Form Load:**
1. User visits `/` endpoint
2. FastAPI renders `form.html` with empty form
3. Template displays upload section and example template button

**Example Template Load:**
1. User clicks "Load Example Template" button
2. POST request to `/templates/load-example`
3. Server loads `example_template.json` from project root
4. Form re-renders with example data populated
5. Template upload section is hidden

**JSON Template Upload:**
1. User selects JSON file and submits upload form
2. POST request to `/templates/upload` with file
3. Server parses uploaded JSON file
4. Form re-renders with uploaded data populated
5. Success message displayed

### 2. Lease Generation Flow
1. **Form Submission**: User submits completed form to `/generate`
2. **Data Processing**: FastAPI processes form data into Pydantic models
3. **Payment Schedule Generation**: Auto-generate payment entries if enabled
4. **Security Deposit Calculation**: Calculate deposit increases for renewals
5. **Template Rendering**: Jinja2 renders lease document with data
6. **Output Generation**: Based on selected format:
   - **HTML**: Return rendered template for browser display
   - **PDF**: Use WeasyPrint to convert HTML to PDF for download
   - **Renewal Message**: Generate personalized text file

### 3. Payment Schedule Generation Algorithm
```python
def create_payment_schedule(
    start_date: date, 
    end_date: date, 
    monthly_rent: float,
    rent_increases: List[dict],
    custom_entries: List[PaymentEntry],
    security_deposit_increase: float = 0.0,
    lease_start_comment: str = "",
    previous_rent: float = 0.0
) -> List[PaymentEntry]
```

**Algorithm Steps:**
1. **Previous Month Entry**: If previous_rent > 0, add entry for month before lease start
2. **Monthly Entries**: Generate entry for each month from start to end date
3. **First Payment**: Add security deposit increase to first payment
4. **Rent Increases**: Apply scheduled rent increases on specified dates
5. **Custom Entries**: Merge in any manually created payment entries
6. **Sorting**: Sort all entries by due date
7. **Comments**: Apply lease start comment to first payment

### 4. Currency Formatting
Custom Jinja2 filter for professional currency display:
```python
def format_currency(amount):
    if amount is None:
        return "$0"
    if float(amount) == int(amount):
        return f"${int(amount):,}"      # No decimals for whole numbers
    else:
        return f"${amount:,.2f}"        # Two decimals for partial amounts
```

**Examples:**
- `1200.0` → `"$1,200"`
- `1250.50` → `"$1,250.50"`
- `12500.0` → `"$12,500"`

### 5. Renewal Message Generation
```python
def generate_renewal_message(tenant_name: str, previous_rent: float, current_rent: float) -> str
```

**Template:**
```
Dear {first_name},

I hope this message finds you well. As your lease term is approaching its end, I wanted to reach out regarding the renewal of your lease.

I'm pleased to offer you the opportunity to renew your lease for another term. The monthly rent for the upcoming term will be ${current_rent:,}, which represents an increase of ${rent_increase:,} ({increase_percentage}%) from your current rent of ${previous_rent:,}.

If you're interested in renewing your lease under these terms, please let me know by {sign_by_date}. I'll prepare the new lease agreement for your review and signature.

Thank you for being a great tenant, and I look forward to hearing from you soon.

Best regards,
[Your Name]
```

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

## Extensibility & Customization

### Adding New Form Fields
1. **Update Data Model**: Add field to appropriate Pydantic model in `models.py`
2. **Update Form**: Add input field to `form.html` template
3. **Update Lease Template**: Add field display to `lease_template.html`
4. **Update Processing**: Modify form processing in `main.py` if special handling needed
5. **Update Example**: Add field to `example_template.json` if applicable

### Adding New Models
1. **Create Model**: Define new Pydantic model in `models.py`
2. **Integrate Model**: Add as field to `LeaseAgreement` model
3. **Update Templates**: Modify HTML templates to handle new model data
4. **Update Endpoints**: Modify API endpoints to process new model data
5. **Update Documentation**: Add model specification to this document

### Customizing Business Logic
**Pydantic Validators:**
```python
from pydantic import validator

class LeaseTerms(BaseModel):
    start_date: date
    end_date: date
    
    @validator('end_date')
    def end_date_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v
```

**Custom Payment Logic:**
```python
def create_custom_payment_schedule(lease_data: LeaseAgreement) -> List[PaymentEntry]:
    # Implement custom payment generation logic
    pass
```

**Template Customization:**
- Modify `lease_template.html` for document layout changes
- Update CSS styles embedded in templates
- Add new template sections for additional data
- Customize currency formatting and date display

### Configuration Options
**Default Values** (in `models.py`):
```python
class LeaseTerms(BaseModel):
    late_fee: float = 20.0          # Modify default late fee
    nsf_fee: float = 34.0           # Modify default NSF fee
    
class LeaseAgreement(BaseModel):
    governing_law_state: str = "Vermont"  # Change default state
```

**Server Settings** (in `main.py`):
```python
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)  # Modify host/port
```

### Integration Possibilities
- **Database Integration**: Add SQLAlchemy models for server-side storage
- **Email Integration**: Add SMTP functionality for sending renewal messages
- **Digital Signatures**: Integrate with DocuSign or similar services
- **Payment Processing**: Add Stripe/PayPal integration for rent collection
- **Document Storage**: Integrate with cloud storage providers
- **Multi-tenant Support**: Add user authentication and tenant separation

This specification provides a complete reference for understanding, maintaining, and extending the Lease Generator application. All current features and implementation details are documented to enable full regeneration of the application from this specification.

## Development & Deployment

### Local Development Setup
```bash
# Clone repository
git clone <repository-url>
cd lease-generator

# Install dependencies
uv sync

# Run development server
uv run uvicorn src.lease_generator.main:app --reload

# Access application
open http://localhost:8000
```

### Production Deployment
```bash
# Run production server
uv run python -m lease_generator.main

# Or with uvicorn directly
uv run uvicorn src.lease_generator.main:app --host 0.0.0.0 --port 8000
```

### Environment Variables
No environment variables required - application uses sensible defaults:
- **Host**: `0.0.0.0`
- **Port**: `8000` 
- **Default State**: `Vermont`
- **Default Late Fee**: `$20`
- **Default NSF Fee**: `$34`

### Dependencies
All dependencies managed in `pyproject.toml`:
```toml
[project]
requires-python = ">=3.11"
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "jinja2",
    "weasyprint",
    "pydantic",
    "python-multipart"
]
```

### Error Handling Strategy
1. **Form Level**: HTML5 validation for required fields and basic types
2. **Pydantic Level**: Model validation with detailed error messages
3. **Application Level**: Custom business logic validation
4. **Template Level**: Graceful handling of missing optional data
5. **User Experience**: Clear error messages displayed in web interface

### Testing Strategy
- **Manual Testing**: Web interface testing for all user workflows
- **Data Validation**: Pydantic models provide automatic validation testing
- **Template Testing**: HTML rendering verification with sample data
- **PDF Generation**: WeasyPrint output verification
- **File Operations**: Template upload/download functionality verification

## API Endpoints

The FastAPI application provides the following HTTP endpoints:

### Core Endpoints
- **`GET /`** - Main form page for creating new leases
  - Returns: HTML form page
  - Optional query params: None (always shows clean form or template-loaded form)

- **`POST /generate`** - Generate lease from form data
  - Accepts: Form data (application/x-www-form-urlencoded)
  - Returns: HTML preview, PDF download, or renewal message text file
  - Form fields: All lease data fields plus output format selection

### Template Management Endpoints
- **`POST /templates/upload`** - Upload JSON template file
  - Accepts: multipart/form-data with template_file
  - Returns: HTML form page populated with template data
  - File validation: Must be valid JSON with expected structure

- **`POST /templates/load-example`** - Load built-in example template
  - Accepts: POST request (no body required)
  - Returns: HTML form page populated with example data
  - Template source: `example_template.json` in project root

### Utility Endpoints
- **`POST /generate-payment-schedule`** - Generate standalone payment schedule PDF
  - Accepts: JSON data with lease information
  - Returns: PDF file download
  - Use case: Generate payment schedule without full lease document

- **`GET /edit/{lease_id}`** - Lease editing interface (basic implementation)
  - Returns: HTML editing interface
  - Status: Basic placeholder implementation

### Response Formats
**HTML Responses:**
- Form pages with populated data
- Success/error messages
- Template rendering with Jinja2

**File Downloads:**
- PDF files with proper Content-Disposition headers
- Text files for renewal messages
- JSON files for configuration downloads

**Error Handling:**
- 400 Bad Request for invalid form data
- 500 Internal Server Error for processing failures
- User-friendly error messages in HTML responses

## Key Features & Implementation Details

### Payment Schedule Features
- **Auto-generation**: Create monthly payment entries from lease start to end
- **Rent Increases**: Support multiple rent increases with specific effective dates
- **Security Deposit Handling**: Automatic calculation of deposit increases for renewals
- **Previous Month Entry**: Option to show previous rent rate before lease start
- **Custom Comments**: Configurable comments for specific payments (especially first payment)
- **Manual Override**: Support for completely custom payment schedules

### Currency & Number Formatting
- **Professional Display**: Currency amounts formatted with commas, no unnecessary decimals
- **Consistent Formatting**: Same formatting rules applied throughout lease document
- **Input Flexibility**: Accept various input formats, normalize for display

### Template System
- **Example Template**: Built-in generic template with John Smith/Jane Doe
- **Upload/Download**: JSON-based template sharing
- **Form Population**: Automatic form field population from template data
- **Data Preservation**: All form state preserved in template JSON

### Document Generation
- **Multiple Formats**: HTML preview, PDF download, renewal message text
- **Professional Styling**: Print-optimized CSS for PDF generation
- **Filename Generation**: Automatic, descriptive filenames based on tenant and date
- **WeasyPrint Integration**: HTML-to-PDF conversion with proper formatting

### Validation & Error Handling
- **Pydantic Validation**: Type checking and constraint validation on all data models
- **Form Validation**: HTML5 validation for required fields and basic types
- **Business Rules**: Custom validation for logical constraints (end date after start date, etc.)
- **User-Friendly Errors**: Clear error messages displayed in the UI

### Performance Considerations
- **No Database**: Stateless application with no server-side storage
- **Efficient Templates**: Jinja2 templates with minimal processing overhead
- **Memory Management**: Appropriate Python types, optional fields default to None
- **PDF Generation**: On-demand PDF creation, no caching required
- **Client-side Storage**: Configuration management handled in browser downloads