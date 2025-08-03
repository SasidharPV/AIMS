"""
ADF Monitoring & Automation System - Configuration Module
"""
import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

load_dotenv()

@dataclass
class AzureConfig:
    """Azure Data Factory configuration"""
    subscription_id: str
    resource_group: str
    data_factory_name: str
    tenant_id: str
    client_id: str
    client_secret: str

@dataclass
class OpenAIConfig:
    """OpenAI configuration"""
    api_key: str
    model: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.3

@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    polling_interval_minutes: int = 5
    max_retry_attempts: int = 3
    retry_delay_minutes: int = 10

@dataclass
class NotificationConfig:
    """Notification configuration"""
    teams_webhook_url: Optional[str] = None
    email_smtp_server: Optional[str] = None
    email_smtp_port: int = 587
    email_from: Optional[str] = None
    email_password: Optional[str] = None
    email_to: Optional[str] = None

@dataclass
class DatabaseConfig:
    """Database configuration"""
    database_path: str = "./adf_monitoring.db"

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.azure = AzureConfig(
            subscription_id=os.getenv("AZURE_SUBSCRIPTION_ID", ""),
            resource_group=os.getenv("AZURE_RESOURCE_GROUP", ""),
            data_factory_name=os.getenv("AZURE_DATA_FACTORY_NAME", ""),
            tenant_id=os.getenv("AZURE_TENANT_ID", ""),
            client_id=os.getenv("AZURE_CLIENT_ID", ""),
            client_secret=os.getenv("AZURE_CLIENT_SECRET", "")
        )
        
        self.openai = OpenAIConfig(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("OPENAI_MODEL", "gpt-4")
        )
        
        self.monitoring = MonitoringConfig(
            polling_interval_minutes=int(os.getenv("POLLING_INTERVAL_MINUTES", "5")),
            max_retry_attempts=int(os.getenv("MAX_RETRY_ATTEMPTS", "3")),
            retry_delay_minutes=int(os.getenv("RETRY_DELAY_MINUTES", "10"))
        )
        
        self.notification = NotificationConfig(
            teams_webhook_url=os.getenv("TEAMS_WEBHOOK_URL"),
            email_smtp_server=os.getenv("EMAIL_SMTP_SERVER"),
            email_smtp_port=int(os.getenv("EMAIL_SMTP_PORT", "587")),
            email_from=os.getenv("EMAIL_FROM"),
            email_password=os.getenv("EMAIL_PASSWORD"),
            email_to=os.getenv("EMAIL_TO")
        )
        
        self.database = DatabaseConfig(
            database_path=os.getenv("DATABASE_PATH", "./adf_monitoring.db")
        )

    def validate(self) -> bool:
        """Validate required configuration"""
        required_fields = [
            self.azure.subscription_id,
            self.azure.resource_group,
            self.azure.data_factory_name,
            self.openai.api_key
        ]
        
        missing_fields = [field for field in required_fields if not field]
        
        if missing_fields:
            print(f"Missing required configuration fields: {len(missing_fields)} fields")
            return False
            
        return True

# Global config instance
config = Config()
