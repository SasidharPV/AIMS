"""
Enterprise Configuration Management for ADF Monitor Pro
Handles multiple environments, AI providers, and system settings
"""
import os
import json
import yaml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import uuid
from datetime import datetime

@dataclass
class EnvironmentConfig:
    """Configuration for an ADF environment"""
    name: str
    subscription_id: str
    resource_group: str
    data_factory: str
    region: str
    tenant_id: str
    client_id: str
    client_secret: str
    status: str = "Active"
    polling_interval: int = 300  # seconds
    retry_attempts: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "subscription_id": self.subscription_id,
            "resource_group": self.resource_group,
            "data_factory": self.data_factory,
            "region": self.region,
            "tenant_id": self.tenant_id,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "status": self.status,
            "polling_interval": self.polling_interval,
            "retry_attempts": self.retry_attempts
        }

@dataclass
class AIProviderConfig:
    """Configuration for an AI provider"""
    provider_id: str
    provider_name: str
    model_name: str
    api_endpoint: str
    api_key: str
    temperature: float = 0.3
    max_tokens: int = 1000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    confidence_threshold: int = 75
    retry_confidence: int = 80
    active: bool = True
    cost_per_1k_tokens: float = 0.03
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "api_endpoint": self.api_endpoint,
            "api_key": self.api_key,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "confidence_threshold": self.confidence_threshold,
            "retry_confidence": self.retry_confidence,
            "active": self.active,
            "cost_per_1k_tokens": self.cost_per_1k_tokens
        }

@dataclass
class NotificationConfig:
    """Configuration for notifications"""
    email_enabled: bool = False
    email_smtp_server: str = ""
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_recipients: List[str] = None
    
    teams_enabled: bool = False
    teams_webhook_url: str = ""
    
    slack_enabled: bool = False
    slack_webhook_url: str = ""
    
    console_enabled: bool = True
    
    def __post_init__(self):
        if self.email_recipients is None:
            self.email_recipients = []

class EnterpriseConfigManager:
    """Manages enterprise configuration for the ADF Monitor Pro application"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration file paths
        self.environments_file = self.config_dir / "environments.yaml"
        self.ai_providers_file = self.config_dir / "ai_providers.yaml"
        self.notifications_file = self.config_dir / "notifications.yaml"
        self.system_config_file = self.config_dir / "system_config.yaml"
        
        # Initialize default configurations if files don't exist
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default configuration files"""
        
        # Default environments
        if not self.environments_file.exists():
            default_environments = {
                "environments": [
                    {
                        "name": "Production",
                        "subscription_id": "your-prod-subscription-id",
                        "resource_group": "prod-rg-adf",
                        "data_factory": "prod-adf-main",
                        "region": "eastus",
                        "tenant_id": "your-tenant-id",
                        "client_id": "your-client-id",
                        "client_secret": "your-client-secret",
                        "status": "Active",
                        "polling_interval": 300,
                        "retry_attempts": 3
                    },
                    {
                        "name": "Staging",
                        "subscription_id": "your-stage-subscription-id",
                        "resource_group": "stage-rg-adf",
                        "data_factory": "stage-adf-main",
                        "region": "eastus",
                        "tenant_id": "your-tenant-id",
                        "client_id": "your-client-id",
                        "client_secret": "your-client-secret",
                        "status": "Active",
                        "polling_interval": 600,
                        "retry_attempts": 2
                    }
                ]
            }
            
            with open(self.environments_file, 'w') as f:
                yaml.dump(default_environments, f, default_flow_style=False)
        
        # Default AI providers
        if not self.ai_providers_file.exists():
            default_ai_providers = {
                "ai_providers": [
                    {
                        "provider_id": "openai-gpt4",
                        "provider_name": "OpenAI GPT-4",
                        "model_name": "gpt-4",
                        "api_endpoint": "https://api.openai.com/v1/chat/completions",
                        "api_key": "your-openai-api-key",
                        "temperature": 0.3,
                        "max_tokens": 1000,
                        "top_p": 0.9,
                        "frequency_penalty": 0.0,
                        "confidence_threshold": 75,
                        "retry_confidence": 80,
                        "active": True,
                        "cost_per_1k_tokens": 0.03
                    },
                    {
                        "provider_id": "azure-openai",
                        "provider_name": "Azure OpenAI",
                        "model_name": "gpt-4",
                        "api_endpoint": "https://your-resource.openai.azure.com/",
                        "api_key": "your-azure-openai-key",
                        "temperature": 0.3,
                        "max_tokens": 1000,
                        "top_p": 0.9,
                        "frequency_penalty": 0.0,
                        "confidence_threshold": 75,
                        "retry_confidence": 80,
                        "active": False,
                        "cost_per_1k_tokens": 0.02
                    }
                ]
            }
            
            with open(self.ai_providers_file, 'w') as f:
                yaml.dump(default_ai_providers, f, default_flow_style=False)
        
        # Default notifications
        if not self.notifications_file.exists():
            default_notifications = {
                "notifications": {
                    "email_enabled": False,
                    "email_smtp_server": "smtp.gmail.com",
                    "email_smtp_port": 587,
                    "email_username": "your-email@company.com",
                    "email_password": "your-app-password",
                    "email_recipients": ["admin@company.com", "devops@company.com"],
                    "teams_enabled": False,
                    "teams_webhook_url": "https://your-company.webhook.office.com/...",
                    "slack_enabled": False,
                    "slack_webhook_url": "https://hooks.slack.com/services/...",
                    "console_enabled": True
                }
            }
            
            with open(self.notifications_file, 'w') as f:
                yaml.dump(default_notifications, f, default_flow_style=False)
        
        # Default system configuration
        if not self.system_config_file.exists():
            default_system_config = {
                "system": {
                    "app_name": "ADF Monitor Pro",
                    "version": "2.0.0",
                    "database_url": "sqlite:///adf_monitor_enterprise.db",
                    "log_level": "INFO",
                    "log_file": "logs/adf_monitor.log",
                    "enable_audit_trail": True,
                    "enable_performance_monitoring": True,
                    "session_timeout_hours": 8,
                    "max_concurrent_users": 50,
                    "backup_retention_days": 90,
                    "monitoring": {
                        "enable_health_checks": True,
                        "health_check_interval": 60,
                        "enable_metrics_collection": True,
                        "metrics_retention_days": 30
                    },
                    "security": {
                        "enable_authentication": True,
                        "enable_rbac": True,
                        "password_policy": {
                            "min_length": 8,
                            "require_uppercase": True,
                            "require_lowercase": True,
                            "require_numbers": True,
                            "require_special_chars": True
                        },
                        "session_security": {
                            "secure_cookies": True,
                            "same_site": "strict",
                            "enable_csrf_protection": True
                        }
                    }
                }
            }
            
            with open(self.system_config_file, 'w') as f:
                yaml.dump(default_system_config, f, default_flow_style=False)
    
    def get_environments(self) -> List[EnvironmentConfig]:
        """Get all configured environments"""
        with open(self.environments_file, 'r') as f:
            data = yaml.safe_load(f)
        
        environments = []
        for env_data in data.get('environments', []):
            environments.append(EnvironmentConfig(**env_data))
        
        return environments
    
    def add_environment(self, env_config: EnvironmentConfig) -> bool:
        """Add a new environment configuration"""
        try:
            with open(self.environments_file, 'r') as f:
                data = yaml.safe_load(f)
            
            # Check if environment already exists
            existing_names = [env['name'] for env in data.get('environments', [])]
            if env_config.name in existing_names:
                return False
            
            data['environments'].append(env_config.to_dict())
            
            with open(self.environments_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            return True
        except Exception:
            return False
    
    def update_environment(self, env_name: str, env_config: EnvironmentConfig) -> bool:
        """Update an existing environment configuration"""
        try:
            with open(self.environments_file, 'r') as f:
                data = yaml.safe_load(f)
            
            # Find and update the environment
            for i, env in enumerate(data.get('environments', [])):
                if env['name'] == env_name:
                    data['environments'][i] = env_config.to_dict()
                    break
            else:
                return False
            
            with open(self.environments_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            return True
        except Exception:
            return False
    
    def delete_environment(self, env_name: str) -> bool:
        """Delete an environment configuration"""
        try:
            with open(self.environments_file, 'r') as f:
                data = yaml.safe_load(f)
            
            data['environments'] = [env for env in data.get('environments', []) 
                                   if env['name'] != env_name]
            
            with open(self.environments_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            return True
        except Exception:
            return False
    
    def get_ai_providers(self) -> List[AIProviderConfig]:
        """Get all configured AI providers"""
        with open(self.ai_providers_file, 'r') as f:
            data = yaml.safe_load(f)
        
        providers = []
        for provider_data in data.get('ai_providers', []):
            providers.append(AIProviderConfig(**provider_data))
        
        return providers
    
    def add_ai_provider(self, provider_config: AIProviderConfig) -> bool:
        """Add a new AI provider configuration"""
        try:
            with open(self.ai_providers_file, 'r') as f:
                data = yaml.safe_load(f)
            
            # Check if provider already exists
            existing_ids = [p['provider_id'] for p in data.get('ai_providers', [])]
            if provider_config.provider_id in existing_ids:
                return False
            
            data['ai_providers'].append(provider_config.to_dict())
            
            with open(self.ai_providers_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            return True
        except Exception:
            return False
    
    def get_notification_config(self) -> NotificationConfig:
        """Get notification configuration"""
        with open(self.notifications_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return NotificationConfig(**data.get('notifications', {}))
    
    def update_notification_config(self, notification_config: NotificationConfig) -> bool:
        """Update notification configuration"""
        try:
            data = {"notifications": notification_config.__dict__}
            
            with open(self.notifications_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
            
            return True
        except Exception:
            return False
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        with open(self.system_config_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return data.get('system', {})
    
    def export_configuration(self, export_path: str) -> bool:
        """Export all configurations to a single file"""
        try:
            export_data = {
                "environments": [],
                "ai_providers": [],
                "notifications": {},
                "system": {},
                "export_metadata": {
                    "timestamp": str(datetime.now()),
                    "version": "2.0.0",
                    "export_id": str(uuid.uuid4())
                }
            }
            
            # Load all configurations
            with open(self.environments_file, 'r') as f:
                env_data = yaml.safe_load(f)
                export_data["environments"] = env_data.get('environments', [])
            
            with open(self.ai_providers_file, 'r') as f:
                ai_data = yaml.safe_load(f)
                export_data["ai_providers"] = ai_data.get('ai_providers', [])
            
            with open(self.notifications_file, 'r') as f:
                notif_data = yaml.safe_load(f)
                export_data["notifications"] = notif_data.get('notifications', {})
            
            with open(self.system_config_file, 'r') as f:
                sys_data = yaml.safe_load(f)
                export_data["system"] = sys_data.get('system', {})
            
            # Write to export file
            with open(export_path, 'w') as f:
                yaml.dump(export_data, f, default_flow_style=False)
            
            return True
        except Exception:
            return False
    
    def import_configuration(self, import_path: str) -> bool:
        """Import configurations from a file"""
        try:
            with open(import_path, 'r') as f:
                import_data = yaml.safe_load(f)
            
            # Import environments
            if 'environments' in import_data:
                env_data = {"environments": import_data['environments']}
                with open(self.environments_file, 'w') as f:
                    yaml.dump(env_data, f, default_flow_style=False)
            
            # Import AI providers
            if 'ai_providers' in import_data:
                ai_data = {"ai_providers": import_data['ai_providers']}
                with open(self.ai_providers_file, 'w') as f:
                    yaml.dump(ai_data, f, default_flow_style=False)
            
            # Import notifications
            if 'notifications' in import_data:
                notif_data = {"notifications": import_data['notifications']}
                with open(self.notifications_file, 'w') as f:
                    yaml.dump(notif_data, f, default_flow_style=False)
            
            # Import system config
            if 'system' in import_data:
                sys_data = {"system": import_data['system']}
                with open(self.system_config_file, 'w') as f:
                    yaml.dump(sys_data, f, default_flow_style=False)
            
            return True
        except Exception:
            return False

# Global configuration manager instance
config_manager = EnterpriseConfigManager()

def get_config_manager() -> EnterpriseConfigManager:
    """Get the global configuration manager instance"""
    return config_manager
