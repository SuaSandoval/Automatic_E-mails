# SharePoint Setup Guide

## Quick Start

Your notebook now includes SharePoint integration! Here's how to set it up:

### 1. Get Azure AD Credentials

You need to create an app registration in Azure AD:

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations** > **New registration**
3. Fill in the form:
   - Name: `BKW Automation` (or similar)
   - Supported account types: Single tenant
   - Redirect URI: Leave blank for now
4. Click **Register**

### 2. Create Client Secret

1. In your app registration, go to **Certificates & secrets**
2. Click **New client secret**
3. Set expiration (e.g., 2 years)
4. Copy the **Value** (this is your `AZURE_CLIENT_SECRET`)

### 3. Set API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission** > **Microsoft Graph** > **Application permissions**
3. Search for and add these permissions:
   - `Sites.FullControl.All` (for SharePoint site access)
   - `Files.ReadWrite.All` (for file operations)
4. Click **Grant admin consent**

### 4. Get Your SharePoint Info

1. **Tenant ID**: In Azure AD > Overview, copy the **Directory (tenant) ID**
2. **Client ID**: In your app registration > Overview, copy the **Application (client) ID**
3. **SharePoint Site URL**: Open your SharePoint site and copy the URL (e.g., `https://yourorg.sharepoint.com/sites/BKW`)

### 5. Create .env File

Create a file named `.env` in your project root with your credentials:

```
SHAREPOINT_SITE_URL=https://yourorg.sharepoint.com/sites/BKW
SHAREPOINT_LIBRARY=Documents
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

**⚠️ Important:** Never commit `.env` to version control!

### 6. Run the Notebook

The notebook will now:
1. Load your SharePoint credentials
2. Initialize the SharePoint client
3. Download data from SharePoint
4. Process the data
5. Upload results back to SharePoint

## Troubleshooting

### "Credentials not configured" message

- Check that `.env` file exists in your project root
- Verify all four environment variables are set
- Restart your notebook kernel (Ctrl+Shift+F5)

### "Authentication failed"

- Verify credentials in `.env` are correct
- Check that app registration has proper API permissions
- Ensure admin has granted consent to permissions

### "Could not find library"

- Verify `SHAREPOINT_LIBRARY` name matches your SharePoint (usually "Documents")
- Check URL is correct

### Missing dependencies

Run in terminal:
```bash
pip install office365-rest-python-client
pip install python-dotenv
```

## Usage in Notebook

The notebook includes these functions:

- **Cell 1.5**: Configure SharePoint settings
- **Cell 8**: Upload processed data to SharePoint

To use: Set credentials in `.env`, then run all cells.

## Next Steps

1. ✅ Set up Azure AD app registration
2. ✅ Create `.env` file with credentials
3. ✅ Run the notebook cells
4. ✅ Check SharePoint for processed files in "Processed/BKW_Data" folder

For more help, see [Office365 Python Client Documentation](https://github.com/vgrem/Office365-REST-Python-Client)
