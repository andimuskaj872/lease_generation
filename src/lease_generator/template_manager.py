import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from .models import LeaseConfiguration
from .templates import get_default_templates


class TemplateManager:
    def __init__(self, template_dir: str = "custom_templates"):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(exist_ok=True)
    
    def get_all_templates(self) -> List[LeaseConfiguration]:
        """Get all templates (default + custom)"""
        templates = []
        
        # Add default templates
        templates.extend(get_default_templates())
        
        # Add custom templates
        custom_templates = self.load_custom_templates()
        templates.extend(custom_templates)
        
        return templates
    
    def load_custom_templates(self) -> List[LeaseConfiguration]:
        """Load custom templates from storage"""
        templates = []
        
        for template_file in self.template_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    data = json.load(f)
                
                # Convert string dates back to datetime objects
                if 'created_at' in data:
                    data['created_at'] = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
                if 'updated_at' in data:
                    data['updated_at'] = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
                
                # Convert date strings in lease_terms
                if 'lease_terms' in data:
                    if 'start_date' in data['lease_terms']:
                        data['lease_terms']['start_date'] = data['lease_terms']['start_date']
                    if 'end_date' in data['lease_terms']:
                        data['lease_terms']['end_date'] = data['lease_terms']['end_date']
                
                template = LeaseConfiguration(**data)
                templates.append(template)
            except Exception as e:
                print(f"Error loading template {template_file}: {e}")
                continue
        
        return templates
    
    def get_template_by_name(self, name: str) -> Optional[LeaseConfiguration]:
        """Get a template by its name"""
        all_templates = self.get_all_templates()
        return next((t for t in all_templates if t.name == name), None)
    
    def save_template(self, template: LeaseConfiguration) -> str:
        """Save a template and return the template ID"""
        template.updated_at = datetime.now()
        
        # Generate filename from name (sanitized)
        safe_name = "".join(c for c in template.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        filename = f"{safe_name}_template.json"
        
        template_path = self.template_dir / filename
        
        with open(template_path, 'w') as f:
            json.dump(template.model_dump(mode='json'), f, indent=2)
        
        return filename.replace('_template.json', '')
    
    def update_template(self, original_name: str, updated_template: LeaseConfiguration) -> bool:
        """Update an existing template"""
        # Check if it's a default template
        default_templates = get_default_templates()
        is_default = any(t.name == original_name for t in default_templates)
        
        if is_default:
            # Save as custom template (can't modify defaults directly)
            updated_template.name = f"{updated_template.name} (Custom)"
            self.save_template(updated_template)
            return True
        else:
            # Update custom template
            self.save_template(updated_template)
            return True
    
    def delete_template(self, name: str) -> bool:
        """Delete a custom template (cannot delete default templates)"""
        # Check if it's a default template
        default_templates = get_default_templates()
        is_default = any(t.name == name for t in default_templates)
        
        if is_default:
            return False  # Cannot delete default templates
        
        # Find and delete custom template file
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        filename = f"{safe_name}_template.json"
        template_path = self.template_dir / filename
        
        if template_path.exists():
            template_path.unlink()
            return True
        return False
    
    def is_default_template(self, name: str) -> bool:
        """Check if a template is a default template"""
        default_templates = get_default_templates()
        return any(t.name == name for t in default_templates)
    
    def list_templates(self) -> List[Dict[str, str]]:
        """List all templates with metadata"""
        templates = []
        all_templates = self.get_all_templates()
        
        for template in all_templates:
            templates.append({
                'name': template.name,
                'description': template.description,
                'type': 'default' if self.is_default_template(template.name) else 'custom',
                'created_at': template.created_at.isoformat(),
                'updated_at': template.updated_at.isoformat()
            })
        
        return templates