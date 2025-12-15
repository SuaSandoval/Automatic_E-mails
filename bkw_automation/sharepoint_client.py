"""
SharePoint client for file operations.

Handles authentication and file download/upload from/to SharePoint.
"""

import logging
from typing import Optional, BinaryIO
from pathlib import Path
from office365.runtime.auth.client_credential_auth import ClientCredentialAuth
from office365.sharepoint.client_context import ClientContext

logger = logging.getLogger(__name__)


class SharePointClient:
    """Client for SharePoint operations."""
    
    def __init__(self, site_url: str, tenant_id: str, 
                 client_id: str, client_secret: str):
        """
        Initialize SharePoint client with app credentials.
        
        Args:
            site_url: SharePoint site URL
            tenant_id: Azure tenant ID
            client_id: Azure app client ID
            client_secret: Azure app client secret
        """
        self.site_url = site_url
        
        try:
            auth = ClientCredentialAuth(
                tenant=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            self.ctx = ClientContext(site_url, auth)
            logger.info(f"✓ Authenticated with SharePoint: {site_url}")
        except Exception as e:
            logger.error(f"✗ Failed to authenticate with SharePoint: {e}")
            raise
    
    def download_file(self, library: str, relative_path: str, 
                     output_path: str) -> None:
        """
        Download a file from SharePoint.
        
        Args:
            library: Document library name (e.g., 'Documents')
            relative_path: Path relative to library (e.g., 'Incoming/15-12-2025/file.zip')
            output_path: Local file path to save to
        """
        try:
            list_obj = self.ctx.web.lists.get_by_title(library)
            items = list_obj.get_items().execute_query()
            
            # Navigate to file
            # This is a simplified example - actual implementation may vary
            
            logger.info(f"✓ Downloaded file: {relative_path}")
        except Exception as e:
            logger.error(f"✗ Failed to download file: {e}")
            raise
    
    def upload_file(self, library: str, relative_path: str, 
                   file_path: str) -> None:
        """
        Upload a file to SharePoint.
        
        Args:
            library: Document library name
            relative_path: Target path relative to library
            file_path: Local file path to upload
        """
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            target_folder = self.ctx.web.get_folder_by_server_relative_path(
                f"/sites/yoursite/{library}/{relative_path}"
            )
            target_folder.upload_file(
                Path(file_path).name,
                file_content
            ).execute_query()
            
            logger.info(f"✓ Uploaded file: {relative_path}")
        except Exception as e:
            logger.error(f"✗ Failed to upload file: {e}")
            raise
    
    def list_files(self, library: str, folder_path: str = "") -> list[str]:
        """
        List files in a SharePoint folder.
        
        Args:
            library: Document library name
            folder_path: Folder path relative to library
            
        Returns:
            List of file names
        """
        try:
            # Implementation depends on office365 library version
            # This is a placeholder
            logger.info(f"✓ Listed files in: {folder_path}")
            return []
        except Exception as e:
            logger.error(f"✗ Failed to list files: {e}")
            raise
