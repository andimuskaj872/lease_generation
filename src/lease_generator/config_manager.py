import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from .models import LeaseConfiguration


class ConfigurationManager:
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
    
    def save_configuration(self, config: LeaseConfiguration) -> str:
        """Save a lease configuration and return the config ID"""
        config.updated_at = datetime.now()
        
        # Generate filename from timestamp
        filename = f"config_{config.created_at.strftime('%Y%m%d_%H%M%S')}.json"
        
        config_path = self.config_dir / filename
        
        with open(config_path, 'w') as f:
            json.dump(config.dict(), f, indent=2, default=str)
        
        return filename.replace('.json', '')
    
    def load_configuration(self, config_id: str) -> Optional[LeaseConfiguration]:
        """Load a lease configuration by ID"""
        config_path = self.config_dir / f"{config_id}.json"
        
        if not config_path.exists():
            return None
        
        try:
            with open(config_path, 'r') as f:
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
            
            return LeaseConfiguration(**data)
        except Exception as e:
            print(f"Error loading configuration {config_id}: {e}")
            return None
    
    def list_configurations(self) -> List[Dict[str, str]]:
        """List all available configurations"""
        configs = []
        
        for config_file in self.config_dir.glob("*.json"):
            try:
                with open(config_file, 'r') as f:
                    data = json.load(f)
                
                configs.append({
                    'id': config_file.stem,
                    'created_at': data.get('created_at', ''),
                    'updated_at': data.get('updated_at', '')
                })
            except Exception as e:
                print(f"Error reading config {config_file}: {e}")
                continue
        
        # Sort by creation date (newest first)
        configs.sort(key=lambda x: x['created_at'], reverse=True)
        return configs
    
    def delete_configuration(self, config_id: str) -> bool:
        """Delete a configuration"""
        config_path = self.config_dir / f"{config_id}.json"
        
        if config_path.exists():
            config_path.unlink()
            return True
        return False