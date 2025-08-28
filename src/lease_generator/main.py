from fastapi import FastAPI, Form, Request, File, UploadFile
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import weasyprint
from datetime import date, datetime, timedelta
from typing import List, Optional
import json
from pathlib import Path

from .models import (
    LeaseAgreement, LeaseParties, PropertyDetails, 
    LeaseTerms, PropertyFeatures, AdditionalTerms, LeaseConfiguration,
    SecurityDepositDetails, PaymentEntry, PaymentSchedule
)
from .config_manager import ConfigurationManager

app = FastAPI(title="Lease Generator", description="Generate residential lease agreements")

# Setup configuration manager
config_manager = ConfigurationManager()

# Setup templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Add custom currency filter
def format_currency(amount):
    """Format currency with commas and no .00 for whole numbers"""
    if amount is None:
        return "$0"
    
    # Check if it's a whole number
    if float(amount) == int(amount):
        return f"${int(amount):,}"
    else:
        return f"${amount:,.2f}"

# Add the filter to Jinja2 environment
templates.env.filters['currency'] = format_currency


def generate_renewal_message(tenant_name: str, previous_rent: float, current_rent: float) -> str:
    """Generate a dynamic renewal message text"""
    # Extract first name (first word of full name)
    first_name = tenant_name.split()[0]
    
    # Calculate rent increase amount and percentage
    rent_increase = current_rent - previous_rent
    if previous_rent > 0:
        increase_percentage = (rent_increase / previous_rent) * 100
        increase_percentage = round(increase_percentage)  # Round to whole number
    else:
        increase_percentage = 0
    
    # Calculate sign by date (2 weeks from today)
    sign_by_date = (datetime.now() + timedelta(days=14)).strftime('%B %d, %Y')
    
    # Format the message
    message = f"""Hi {first_name}! I hope you're doing well. I wanted to thank you for being such a great tenant over the past year—I really appreciate how well you've taken care of the place. Attached is the lease renewal for the upcoming year. The rent will increase by {increase_percentage}% ({format_currency(rent_increase)}), bringing the monthly total to {format_currency(current_rent)}, and you'll see the updated payment schedule included in the lease. Please review and sign within the next two weeks, by {sign_by_date}, and let me know if you have any questions or concerns. Thanks again!"""
    
    return message


def create_payment_schedule(start_date: date, end_date: date, monthly_rent: float, rent_increases: List[dict], custom_entries: List[PaymentEntry], security_deposit_increase: float = 0.0, lease_start_comment: str = "", previous_rent: float = 0.0) -> List[PaymentEntry]:
    """Generate a complete payment schedule with auto-generated monthly payments and custom entries"""
    if custom_entries is None:
        custom_entries = []
        
    schedule = []
    entry_number = 1
    
    # Add custom entries first (they take priority)
    custom_by_date = {}
    for entry in custom_entries:
        if isinstance(entry.due_date, date):
            custom_by_date[entry.due_date] = entry
        # Non-date entries (like "Lease signing") are added separately
        else:
            entry.entry_number = entry_number if not entry.entry_number else entry.entry_number
            schedule.append(entry)
            entry_number += 1
    
    # Create rent increase lookup
    rent_by_date = {monthly_rent: start_date}  # Start with initial rent
    for increase in rent_increases:
        increase_date = date.fromisoformat(increase['date']) if isinstance(increase['date'], str) else increase['date']
        rent_by_date[increase['new_rent']] = increase_date
    
    # Sort rent increases by date
    sorted_increases = sorted([(d, r) for r, d in rent_by_date.items()])
    
    # Add previous month rent entry if there's a rent increase (previous_rent > 0)
    if previous_rent > 0 and previous_rent != monthly_rent:
        # Calculate the previous month date (month before lease start)
        if start_date.month == 1:
            prev_month_date = date(start_date.year - 1, 12, 1)
        else:
            prev_month_date = date(start_date.year, start_date.month - 1, 1)
        
        # Add entry for previous month at old rate
        prev_month_entry = PaymentEntry(
            due_date=prev_month_date,
            rent_amount=previous_rent,
            security_deposit=0.0,
            pet_deposit=0.0,
            other_fees=0.0,
            total=previous_rent,
            comment="Last month at current rate",
            is_manual=False,
            entry_number=entry_number
        )
        schedule.append(prev_month_entry)
        entry_number += 1
    
    # Generate monthly payments - start with first of the month
    current_date = date(start_date.year, start_date.month, 1)
    current_rent = monthly_rent
    
    while current_date <= end_date:
        # Check if there's a rent increase for this month
        for increase_date, rent_amount in sorted_increases:
            if current_date >= increase_date and rent_amount != current_rent:
                current_rent = rent_amount
                break
        
        # Skip if there's already a custom entry for this date
        if current_date not in custom_by_date:
            # Check if this is a rent increase month
            is_rent_increase = any(
                current_date.year == date.fromisoformat(inc['date']).year and 
                current_date.month == date.fromisoformat(inc['date']).month 
                for inc in rent_increases
            )
            
            # Check if this is the lease start date (first payment)
            is_lease_start = current_date.year == start_date.year and current_date.month == start_date.month
            
            comment = ""
            additional_deposit = 0.0
            
            if is_lease_start:
                if security_deposit_increase > 0:
                    # Apply the calculated security deposit increase for lease start
                    additional_deposit = security_deposit_increase
                    if lease_start_comment:
                        comment = lease_start_comment
                    else:
                        # Generate default comment with actual dollar amount
                        comment = f"New lease first month rent plus ${int(security_deposit_increase):,} security deposit increase."
                else:
                    # No security deposit increase, just first month
                    if lease_start_comment:
                        comment = lease_start_comment
                    else:
                        comment = "First month rent"
            elif is_rent_increase:
                matching_increase = next(inc for inc in rent_increases if 
                    current_date.year == date.fromisoformat(inc['date']).year and 
                    current_date.month == date.fromisoformat(inc['date']).month)
                comment = matching_increase.get('comment', '')
                # Add security deposit difference if rent increased
                if current_rent > monthly_rent:
                    additional_deposit = current_rent - monthly_rent
            
            entry = PaymentEntry(
                due_date=current_date,
                rent_amount=current_rent,
                security_deposit=additional_deposit,
                pet_deposit=0.0,
                other_fees=0.0,
                total=current_rent + additional_deposit,
                comment=comment,
                is_manual=False,
                entry_number=entry_number
            )
            schedule.append(entry)
            entry_number += 1
        else:
            # Add the custom entry
            custom_entry = custom_by_date[current_date]
            custom_entry.entry_number = entry_number if not custom_entry.entry_number else custom_entry.entry_number
            schedule.append(custom_entry)
            entry_number += 1
        
        # Move to next month
        if current_date.month == 12:
            current_date = date(current_date.year + 1, 1, 1)
        else:
            current_date = date(current_date.year, current_date.month + 1, 1)
    
    return sorted(schedule, key=lambda x: (isinstance(x.due_date, str), x.due_date if isinstance(x.due_date, date) else date.min))

# Serve static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, config_id: Optional[str] = None):
    # Load configuration if provided
    config_data = None
    if config_id:
        config = config_manager.load_configuration(config_id)
        if config:
            config_data = config.model_dump(mode='json')
    
    # Get list of saved configurations
    configurations = config_manager.list_configurations()
    
    return templates.TemplateResponse("form.html", {
        "request": request,
        "config_data": config_data,
        "configurations": configurations
    })


@app.post("/generate")
async def generate_lease(
    request: Request,
    # Parties
    landlord_name: str = Form(...),
    landlord_address: str = Form(...),
    tenant_name: str = Form(...),
    tenant_address: str = Form(""),
    tenant_email: str = Form(""),
    has_occupants: bool = Form(False),
    occupants: str = Form(""),
    
    # Property Details
    mailing_address: str = Form(...),
    residence_type: str = Form(...),
    bedrooms: int = Form(...),
    bathrooms: int = Form(...),
    furnished: bool = Form(False),
    appliances: str = Form(""),
    
    # Lease Terms
    start_date: str = Form(...),
    end_date: str = Form(...),
    monthly_rent: float = Form(...),
    custom_security_deposit: float = Form(0),
    
    # Security Deposit Details
    use_custom_security_deposit: bool = Form(False),
    security_deposit_amount_paid: float = Form(0),
    previous_rent: float = Form(0),
    
    pet_deposit: float = Form(0),
    late_fee: float = Form(20),
    nsf_fee: float = Form(34),
    payment_instructions: str = Form(...),
    
    # Property Features
    parking_spaces: int = Form(0),
    utilities_included: str = Form(""),
    smoking_allowed: bool = Form(False),
    pets_allowed: bool = Form(False),
    waterbed_allowed: bool = Form(False),
    
    # Additional Terms
    early_termination_notice: int = Form(30),
    landlord_contact_phone: str = Form(""),
    landlord_contact_email: str = Form(""),
    special_conditions: str = Form(""),
    
    # Payment Schedule
    include_payment_schedule: bool = Form(False),
    auto_generate_schedule: bool = Form(True),
    rent_increases: str = Form(""),
    lease_start_comment: str = Form(""),
    custom_payments: str = Form(""),
    
    # Other
    governing_law_state: str = Form("Vermont"),
    agreement_date: str = Form(str(date.today())),
    lead_paint_disclosure: bool = Form(False),
    
    # Format selection
    output_format: str = Form("html"),
    
    # Configuration saving
    save_config: bool = Form(False)
):
    # Parse arrays from comma-separated strings
    appliances_list = [a.strip() for a in appliances.split(",") if a.strip()] if appliances else []
    utilities_list = [u.strip() for u in utilities_included.split(",") if u.strip()] if utilities_included else []
    
    # Parse special conditions as simple list
    special_conditions_list = [c.strip() for c in special_conditions.split("\n") if c.strip()] if special_conditions else []
    
    # Parse payment schedule data
    payment_schedule = None
    if include_payment_schedule or rent_increases or custom_payments:
        # Parse rent increases
        rent_increases_list = []
        if rent_increases.strip():
            try:
                rent_increases_list = json.loads(rent_increases)
            except json.JSONDecodeError:
                rent_increases_list = []
        
        # Parse custom payment entries
        custom_entries_list = []
        if custom_payments.strip():
            try:
                custom_entries_data = json.loads(custom_payments)
                for entry_data in custom_entries_data:
                    # Parse due_date - handle both date strings and text like "Lease signing"
                    due_date_str = entry_data.get('due_date', '')
                    if due_date_str:
                        try:
                            # Try to parse as date
                            parsed_date = date.fromisoformat(due_date_str)
                        except:
                            # If not a date, use as string (like "Lease signing")
                            parsed_date = due_date_str
                    else:
                        parsed_date = due_date_str
                    
                    entry = PaymentEntry(
                        due_date=parsed_date,
                        rent_amount=entry_data.get('rent_amount', 0.0),
                        security_deposit=entry_data.get('security_deposit', 0.0),
                        pet_deposit=entry_data.get('pet_deposit', 0.0),
                        other_fees=entry_data.get('other_fees', 0.0),
                        total=entry_data.get('total', 0.0),
                        comment=entry_data.get('comment'),
                        is_manual=True
                    )
                    custom_entries_list.append(entry)
            except json.JSONDecodeError:
                custom_entries_list = []
        
        # Generate the complete schedule if auto_generate is enabled
        final_entries = custom_entries_list
        if auto_generate_schedule:
            start_date_obj = date.fromisoformat(start_date)
            end_date_obj = date.fromisoformat(end_date)
            
            # Calculate security deposit increase from existing logic
            security_increase = 0.0
            if use_custom_security_deposit and previous_rent > 0:
                security_increase = monthly_rent - previous_rent
            
            final_entries = create_payment_schedule(
                start_date_obj, 
                end_date_obj, 
                monthly_rent, 
                rent_increases_list, 
                custom_entries_list,
                security_increase,
                lease_start_comment,
                previous_rent
            )
        
        payment_schedule = PaymentSchedule(
            include_in_lease=include_payment_schedule,
            auto_generate=auto_generate_schedule,
            custom_entries=final_entries,
            rent_increases=rent_increases_list,
            lease_start_comment=lease_start_comment if lease_start_comment else None
        )
    
    # Create lease agreement object
    lease = LeaseAgreement(
        parties=LeaseParties(
            landlord_name=landlord_name,
            landlord_address=landlord_address,
            tenant_name=tenant_name,
            tenant_address=tenant_address if tenant_address else None,
            tenant_email=tenant_email if tenant_email else None,
            has_occupants=has_occupants,
            occupants=occupants.strip() if occupants.strip() else None
        ),
        property_details=PropertyDetails(
            mailing_address=mailing_address,
            residence_type=residence_type,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            furnished=furnished,
            appliances=appliances_list
        ),
        lease_terms=LeaseTerms(
            start_date=date.fromisoformat(start_date),
            end_date=date.fromisoformat(end_date),
            monthly_rent=monthly_rent,
            custom_security_deposit=custom_security_deposit if custom_security_deposit > 0 else None,
            security_deposit_details=SecurityDepositDetails(
                previous_rent=previous_rent if use_custom_security_deposit and previous_rent > 0 else None,
                use_custom_section=use_custom_security_deposit
            ) if use_custom_security_deposit else None,
            pet_deposit=pet_deposit if pet_deposit > 0 else None,
            late_fee=late_fee,
            nsf_fee=nsf_fee,
            payment_instructions=payment_instructions
        ),
        property_features=PropertyFeatures(
            parking_spaces=parking_spaces if parking_spaces > 0 else None,
            utilities_included=utilities_list,
            smoking_allowed=smoking_allowed,
            pets_allowed=pets_allowed,
            waterbed_allowed=waterbed_allowed
        ),
        additional_terms=AdditionalTerms(
            early_termination_notice=early_termination_notice,
            landlord_contact_phone=landlord_contact_phone if landlord_contact_phone else None,
            landlord_contact_email=landlord_contact_email if landlord_contact_email else None,
            special_conditions=special_conditions_list,
            payment_schedule=payment_schedule
        ),
        governing_law_state=governing_law_state,
        agreement_date=date.fromisoformat(agreement_date),
        lead_paint_disclosure=lead_paint_disclosure
    )
    
    # Handle configuration download if requested
    if save_config:
        # Create a clean payment schedule for configuration (preserve original settings)
        config_payment_schedule = None
        if include_payment_schedule or rent_increases or custom_payments:
            # Only save the original manual entries, not auto-generated ones
            config_custom_entries = []
            if custom_payments.strip():
                try:
                    custom_entries_data = json.loads(custom_payments)
                    for entry_data in custom_entries_data:
                        # Parse due_date - handle both date strings and text like "Lease signing"
                        due_date_str = entry_data.get('due_date', '')
                        if due_date_str:
                            try:
                                # Try to parse as date
                                parsed_date = date.fromisoformat(due_date_str)
                            except:
                                # If not a date, use as string (like "Lease signing")
                                parsed_date = due_date_str
                        else:
                            parsed_date = due_date_str
                        
                        entry = PaymentEntry(
                            due_date=parsed_date,
                            rent_amount=entry_data.get('rent_amount', 0.0),
                            security_deposit=entry_data.get('security_deposit', 0.0),
                            pet_deposit=entry_data.get('pet_deposit', 0.0),
                            other_fees=entry_data.get('other_fees', 0.0),
                            total=entry_data.get('total', 0.0),
                            comment=entry_data.get('comment'),
                            is_manual=True
                        )
                        config_custom_entries.append(entry)
                except json.JSONDecodeError:
                    config_custom_entries = []
            
            config_payment_schedule = PaymentSchedule(
                include_in_lease=include_payment_schedule,
                auto_generate=auto_generate_schedule,
                custom_entries=config_custom_entries,  # Only manual entries
                rent_increases=rent_increases_list,
                lease_start_comment=lease_start_comment if lease_start_comment else None
            )
        
        # Create additional terms with clean payment schedule
        config_additional_terms = AdditionalTerms(
            early_termination_notice=lease.additional_terms.early_termination_notice,
            landlord_contact_phone=lease.additional_terms.landlord_contact_phone,
            landlord_contact_email=lease.additional_terms.landlord_contact_email,
            special_conditions=lease.additional_terms.special_conditions,
            payment_schedule=config_payment_schedule
        )
        
        config = LeaseConfiguration(
            parties=lease.parties,
            property_details=lease.property_details,
            lease_terms=lease.lease_terms,
            property_features=lease.property_features,
            additional_terms=config_additional_terms,
            governing_law_state=lease.governing_law_state,
            lead_paint_disclosure=lease.lead_paint_disclosure,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Return configuration as downloadable JSON instead of generating lease
        config_json = json.dumps(config.model_dump(mode='json'), indent=2)
        
        # Auto-generate filename: lease_configuration_tenant_name_lease_start_date
        tenant_name_clean = tenant_name.replace(' ', '_').replace('/', '_').lower()
        start_date_clean = start_date.replace('-', '_')
        filename = f"lease_configuration_{tenant_name_clean}_{start_date_clean}.json"
        
        return Response(
            content=config_json,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    # Generate HTML - serialize with mode='json' and format dates
    lease_data = lease.model_dump(mode='json')
    
    # Debug: Print special conditions to see what we're working with
    if 'additional_terms' in lease_data and 'special_conditions' in lease_data['additional_terms']:
        print("DEBUG: special_conditions type and content:")
        for i, condition in enumerate(lease_data['additional_terms']['special_conditions']):
            print(f"  {i}: {type(condition)} - {condition}")
    
    # Format dates for template display
    if 'agreement_date' in lease_data:
        lease_data['agreement_date'] = lease.agreement_date.strftime('%m/%d/%Y')
    if 'lease_terms' in lease_data:
        if 'start_date' in lease_data['lease_terms']:
            lease_data['lease_terms']['start_date'] = lease.lease_terms.start_date.strftime('%m/%d/%Y')
        if 'end_date' in lease_data['lease_terms']:
            lease_data['lease_terms']['end_date'] = lease.lease_terms.end_date.strftime('%m/%d/%Y')
    
    html_content = templates.get_template("lease_template.html").render(lease_data)
    
    if output_format == "pdf":
        # Generate PDF
        pdf = weasyprint.HTML(string=html_content).write_pdf()
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=lease_agreement_{tenant_name.replace(' ', '_').replace('/', '_').lower()}_{start_date.replace('-', '_')}.pdf"
            }
        )
    elif output_format == "renewal_message":
        # Generate renewal message text file
        # Only generate if there's a previous rent (indicating a renewal)
        if use_custom_security_deposit and previous_rent > 0:
            message_text = generate_renewal_message(tenant_name, previous_rent, monthly_rent)
            
            # Generate filename
            tenant_name_clean = tenant_name.replace(' ', '_').replace('/', '_').lower()
            start_date_clean = start_date.replace('-', '_')
            filename = f"renewal_message_{tenant_name_clean}_{start_date_clean}.txt"
            
            return Response(
                content=message_text,
                media_type="text/plain",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}"
                }
            )
        else:
            # Return error message if no previous rent specified
            return HTMLResponse(
                content="<h1>Error</h1><p>Renewal message can only be generated when previous rent is specified (for rent increase calculation). Please enable 'Customize security deposit' and enter the previous rent amount.</p>", 
                status_code=400
            )
    else:
        # Return HTML preview
        return HTMLResponse(content=html_content)




@app.post("/templates/upload")
async def upload_template(request: Request, template_file: UploadFile = File(...)):
    """Upload and use a template file"""
    try:
        # Read the uploaded file
        content = await template_file.read()
        template_data = json.loads(content.decode('utf-8'))
        
        # Validate it's a proper template by creating a LeaseConfiguration
        template = LeaseConfiguration(**template_data)
        
        # Convert to the format expected by the form
        config_data = template.model_dump(mode='json')
        
        # Get saved configurations for display
        configurations = config_manager.list_configurations()
        
        return templates.TemplateResponse("form.html", {
            "request": request,
            "config_data": config_data,
            "configurations": configurations,
            "upload_success": "Template loaded successfully!"
        })
        
    except Exception as e:
        # Get configurations for display even on error
        configurations = config_manager.list_configurations()
        
        return templates.TemplateResponse("form.html", {
            "request": request,
            "configurations": configurations,
            "upload_error": f"Error loading template: {str(e)}"
        })


@app.post("/generate-payment-schedule")
async def generate_payment_schedule(
    request: Request,
    lease_data: dict
):
    """Generate and export payment schedule as separate document"""
    try:
        # Extract payment schedule data
        payment_schedule = lease_data.get("additional_terms", {}).get("payment_schedule")
        if not payment_schedule:
            return HTMLResponse("No payment schedule data found", status_code=400)
        
        # Render payment schedule template
        schedule_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Schedule</title>
            <style>
                body {{ font-family: Times, serif; margin: 40px; }}
                h1 {{ text-align: center; margin-bottom: 30px; }}
                .payment-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .payment-table th, .payment-table td {{ border: 1px solid black; padding: 8px; text-align: left; }}
                .payment-table th {{ background-color: #f0f0f0; }}
            </style>
        </head>
        <body>
            <h1>PAYMENT SCHEDULE</h1>
            <p><strong>Tenant:</strong> {lease_data.get('parties', {}).get('tenant_name', '')}</p>
            <p><strong>Property:</strong> {lease_data.get('property_details', {}).get('mailing_address', '')}</p>
            <p><strong>Lease Term:</strong> {lease_data.get('lease_terms', {}).get('start_date', '')} to {lease_data.get('lease_terms', {}).get('end_date', '')}</p>
        """
        
        if payment_schedule.get("custom_entries"):
            schedule_html += """
            <table class="payment-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Due Date</th>
                        <th>Rent</th>
                        <th>Security & Pet Deposit</th>
                        <th>Total</th>
                        <th>Comment</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for i, entry in enumerate(payment_schedule["custom_entries"], 1):
                due_date = entry.get("due_date", "")
                if isinstance(due_date, str):
                    due_date_str = due_date
                else:
                    due_date_str = due_date.strftime('%m/%d/%Y') if due_date else ''
                
                schedule_html += f"""
                    <tr>
                        <td>{entry.get('entry_number', '')}</td>
                        <td>{due_date_str}</td>
                        <td>{format_currency(entry.get('rent_amount', 0))}</td>
                        <td>{format_currency(entry.get('security_deposit', 0) + entry.get('pet_deposit', 0))}</td>
                        <td>{format_currency(entry.get('total', 0))}</td>
                        <td>{entry.get('comment', '')}</td>
                    </tr>
                """
            
            schedule_html += """
                </tbody>
            </table>
            """
        
        schedule_html += """
        </body>
        </html>
        """
        
        # Generate PDF
        pdf = weasyprint.HTML(string=schedule_html).write_pdf()
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=payment_schedule_{lease_data.get('parties', {}).get('tenant_name', 'tenant').replace(' ', '_').replace('/', '_').lower()}_{lease_data.get('lease_terms', {}).get('start_date', '').replace('/', '_')}.pdf"
            }
        )
        
    except Exception as e:
        return HTMLResponse(f"Error generating payment schedule: {str(e)}", status_code=500)




@app.get("/configurations")
async def list_configurations():
    """API endpoint to get all configurations"""
    return config_manager.list_configurations()


@app.delete("/configurations/{config_id}")
async def delete_configuration(config_id: str):
    """API endpoint to delete a configuration"""
    success = config_manager.delete_configuration(config_id)
    if success:
        return {"message": "Configuration deleted successfully"}
    else:
        return {"error": "Configuration not found"}, 404


@app.get("/edit/{lease_id}")
async def edit_lease(request: Request, lease_id: str):
    # For now, return the form with placeholder data
    # In a real application, you would load the lease data from storage
    return templates.TemplateResponse("edit_form.html", {"request": request, "lease_id": lease_id})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)