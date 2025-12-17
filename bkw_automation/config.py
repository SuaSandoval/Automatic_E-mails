"""
Configuration settings for BKW automation.

Load settings from environment variables or .env file.
"""

from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # SharePoint configuration
    sharepoint_site_url: str = "https://yourorg.sharepoint.com/sites/yoursite"
    sharepoint_document_library: str = "Documents"
    sharepoint_folder_incoming: str = "Incoming"
    sharepoint_folder_processed: str = "Processed"
    sharepoint_username: Optional[str] = None
    sharepoint_password: Optional[str] = None
    
    # Azure configuration
    azure_subscription_id: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    
    # Email configuration
    email_recipients: list[str] = []
    email_subject_template: str = "BKW Processed Data - {date}"
    smtp_server: str = "smtp.office365.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Processing configuration
    processing_schedule: str = "0 8 * * *"  # Daily at 8 AM (cron format)
    log_level: str = "INFO"
    
    # Paths
    project_root: Path = Path(__file__).parent.parent
    logs_dir: Path = project_root / "logs"
    data_dir: Path = project_root / "data"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Permit additional env vars not defined in the model


# Create settings instance
settings = Settings()

# Ensure directories exist
settings.logs_dir.mkdir(exist_ok=True)
settings.data_dir.mkdir(exist_ok=True)
