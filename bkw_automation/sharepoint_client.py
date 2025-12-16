"""
SharePoint client for file operations.

Handles authentication and file download/upload from/to SharePoint.
"""

import logging
from typing import Optional, List
from pathlib import Path
from urllib.parse import urlparse

from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File

logger = logging.getLogger(__name__)


class SharePointClient:
    """Client for SharePoint operations.

    Supports two authentication modes:
    - App (client credentials via Azure AD)
    - User (username/password via SharePoint Online)
    """

    def __init__(
        self,
        site_url: str,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Initialize SharePoint client.

        Provide either app credentials (client_id/client_secret[/tenant]) or
        user credentials (username/password).

        Args:
            site_url: SharePoint site URL
            tenant_id: Azure tenant ID (optional; app auth)
            client_id: Azure app client ID (optional; app auth)
            client_secret: Azure app client secret (optional; app auth)
            username: M365 username (optional; user auth)
            password: M365 password (optional; user auth)
        """
        self.site_url = site_url.rstrip("/")

        # derive server-relative site path, e.g., /sites/yoursite
        parsed = urlparse(self.site_url)
        self._site_root = parsed.path.rstrip("/") or "/"

        try:
            # Prefer app auth if fully provided, else try user auth
            if client_id and client_secret:
                credentials = ClientCredential(
                    tenant=tenant_id,  # some versions accept None
                    client_id=client_id,
                    client_secret=client_secret,
                )
                self.ctx = ClientContext(self.site_url, credentials)
                logger.info(f"✓ Authenticated with SharePoint (app): {self.site_url}")
            elif username and password:
                self.ctx = ClientContext(self.site_url).with_credentials(
                    UserCredential(username, password)
                )
                logger.info(f"✓ Authenticated with SharePoint (user): {self.site_url}")
            else:
                raise ValueError(
                    "No SharePoint credentials provided. Provide app or user credentials."
                )
        except Exception as e:
            logger.error(f"✗ Failed to authenticate with SharePoint: {e}")
            raise
    
    def _library_root(self, library: str) -> str:
        """Return server-relative URL for the library root."""
        lib = library.strip("/")
        return f"{self._site_root}/{lib}" if self._site_root != "/" else f"/{lib}"

    def download_file(self, library: str, relative_path: str, output_path: str) -> None:
        """
        Download a file from SharePoint.

        Args:
            library: Document library name (e.g., 'Documents')
            relative_path: Path relative to library (e.g., 'Incoming/2025-12-15/file.xlsx')
            output_path: Local file path to save to
        """
        try:
            server_relative_url = f"{self._library_root(library)}/{relative_path.strip('/')}"
            response = File.open_binary(self.ctx, server_relative_url)
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as local_file:
                local_file.write(response.content)
            logger.info(f"✓ Downloaded file: {server_relative_url} -> {output_path}")
        except Exception as e:
            logger.error(f"✗ Failed to download file '{relative_path}': {e}")
            raise
    
    def upload_file(self, library: str, relative_path: str, file_path: str) -> None:
        """
        Upload a file to SharePoint.
        
        Args:
            library: Document library name
            relative_path: Target path relative to library
            file_path: Local file path to upload
        """
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()

            # split folder from filename
            rel = relative_path.strip("/")
            folder_part = "/".join(rel.split("/")[:-1])
            target_folder_url = (
                f"{self._library_root(library)}/{folder_part}" if folder_part else self._library_root(library)
            )

            target_folder = self.ctx.web.get_folder_by_server_relative_path(target_folder_url)
            target_folder.ensure_folder_path("")  # no-op to ensure chain
            target_folder.upload_file(Path(file_path).name, file_content).execute_query()

            logger.info(f"✓ Uploaded file: {relative_path}")
        except Exception as e:
            logger.error(f"✗ Failed to upload file: {e}")
            raise

    def list_files(self, library: str, folder_path: str = "") -> List[str]:
        """
        List files in a SharePoint folder.
        
        Args:
            library: Document library name
            folder_path: Folder path relative to library
        Returns:
            List of filenames in the folder
        """
        try:
            folder_rel = folder_path.strip("/")
            folder_url = (
                f"{self._library_root(library)}/{folder_rel}" if folder_rel else self._library_root(library)
            )
            folder = self.ctx.web.get_folder_by_server_relative_path(folder_url)
            files = folder.files.get().execute_query()
            names = [f.name for f in files]
            logger.info(f"✓ Listed {len(names)} files in: {folder_url}")
            return names
        except Exception as e:
            logger.error(f"✗ Failed to list files in '{folder_path}': {e}")
            raise
