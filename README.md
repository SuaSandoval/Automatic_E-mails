# Email Processing Workflow: Power Automate + Azure Automation + Python

## Overview
This is a **three-step hybrid solution** combining Power Automate, Azure Automation, and Python:

1. **Step 1 - Power Automate**: Capture incoming Rotoforst emails and save ZIP files to SharePoint with dynamic date-based folder structure
2. **Step 2 - Azure Automation + Python**: Extract, transform, and convert Excel files to CSV; generate email body content
3. **Step 3 - Email Delivery**: Send processed CSV files via Python + Azure or Power Automate scheduler

---

## 💰 Cost Requirements

### Required Licenses/Subscriptions:

1. **Microsoft Power Automate**
   - **Office 365 / Microsoft 365**: Included (for basic email operations)
   - Cost: Included in M365 subscription

2. **Microsoft Azure** (for Automation Account + Python scripts)
   - **Azure Automation Account**: ~$6-15/month depending on usage
   - **Storage Account** (optional, for logs): ~$0.50-2/month
   - **Free Trial**: 12 months free tier available

3. **SharePoint Online** (for file storage)
   - Included with Microsoft 365 Business licenses
   - Used for ZIP file staging and document storage

### Cost Summary:
- **Power Automate**: Included with M365
- **Azure Automation**: ~$6-15/month
- **SharePoint**: Included with M365
- **Total monthly cost**: ~$6-15 (if you have M365)

### Cost-Saving Notes:
- Azure offers 12 months free trial with credits
- Python/Azure Automation is much cheaper than Encodian ($30/month)
- No additional document conversion services needed

---

## 📋 Prerequisites

- [ ] Microsoft 365 account with Exchange Online
- [ ] Power Automate access (via Microsoft 365)
- [ ] SharePoint site to store incoming ZIP files
- [ ] Azure subscription (free trial or paid)
- [ ] Azure Automation Account created
- [ ] Python 3.8+ installed (for development/testing)
- [ ] Mailbox to monitor for Rotoforst emails
- [ ] List of recipient email addresses for CSV files
- [ ] Sender email: Rotoforst (fixed)
- [ ] Fixed subject line for emails

---

## 🔧 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: POWER AUTOMATE - EMAIL CAPTURE                          │
├─────────────────────────────────────────────────────────────────┤
│ 1. Trigger: Email from Rotoforst arrives                        │
│ 2. Guard: Verify sender & subject                               │
│ 3. Create dynamic folder: Documents/Incoming/DD-MM-YYYY         │
│ 4. Save ZIP file: Rodaten - Gestern.zip                         │
│ 5. Save metadata: metadata.txt (timestamp, sender, etc.)        │
│ Result: Files stored in SharePoint                              │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: AZURE AUTOMATION + PYTHON - DATA TRANSFORMATION        │
├─────────────────────────────────────────────────────────────────┤
│ 1. Scheduled runbook (or webhook trigger)                       │
│ 2. Python script execution:                                     │
│    a. Download ZIP from SharePoint                              │
│    b. Extract Excel files                                       │
│    c. Transform/clean data (complex logic)                      │
│    d. Convert Excel → CSV                                       │
│    e. Generate email body content                               │
│ 3. Save processed CSV files                                     │
│ Result: CSV files ready & email content prepared                │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: EMAIL DELIVERY                                          │
├─────────────────────────────────────────────────────────────────┤
│ Option A: Python + Azure (in same runbook)                      │
│   - Send email via Azure Mail or SMTP                           │
│   - Attach CSV files                                            │
│   - Execute immediately or schedule                             │
│                                                                 │
│ Option B: Power Automate (scheduled trigger)                    │
│   - Check for processed CSV files in SharePoint                 │
│   - Send email with CSV attachment                              │
│   - Schedule: e.g., 8:00 AM daily                               │
│                                                                 │
│ Result: Recipients get processed CSV files via email            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 STEP 1: Power Automate - Email Capture & File Storage

### Overview
Power Automate captures emails from Rotoforst and saves them to SharePoint with a dynamic date-based folder structure.

### Trigger Configuration

**When a new email arrives (V3)** - Office 365 Outlook:

- **Folder**: Inbox
- **From**: `rotoforst@domain.com` (Rotoforst's actual email)
- **Subject Filter**: Your fixed subject line (e.g., "Rodaten Gestern")
- **Has Attachment**: Yes
- **Include Attachments**: Yes

### Step 1: Guard Condition (Optional but Recommended)

Add a **Condition** to verify sender and subject:

**Expression:**
```
@and(
  equals(triggerOutputs()?['body/from'], 'rotoforst@domain.com'),
  equals(triggerOutputs()?['body/subject'], 'Rodaten Gestern')
)
```

- **If True**: Continue to next step
- **If False**: Terminate with status "Canceled"

### Step 2: Initialize Variables

Create two variables:

1. **varFolderDate** (String):
   - Value: `@{formatDateTime(utcNow(), 'dd-MM-yyyy')}`
   - This creates today's date in DD-MM-YYYY format

2. **varSharePointPath** (String):
   - Value: `@{concat('Documents/Incoming/', variables('varFolderDate'))}`
   - Example result: `Documents/Incoming/15-12-2025`

### Step 3: Create Folder (if not exists)

**Get folder properties** (SharePoint):
- Site: Select your SharePoint site
- Folder: `Documents/Incoming/15-12-2025` (use the varSharePointPath)

If this fails (folder doesn't exist), add an action:

**Create folder** (SharePoint):
- Site: Your SharePoint site
- Folder Path: `/Documents/Incoming`
- Folder Name: `@{variables('varFolderDate')}`

### Step 4: Save ZIP Attachment

**Apply to each** → value: `Attachments` from trigger

Inside the loop:

**Condition**: Check if file is .zip
- Expression: `@endsWith(items('Apply_to_each')?['name'], '.zip')`

**If Yes**:
1. **Create file** (SharePoint):
   - Site: Your SharePoint site
   - Folder Path: `/Documents/Incoming/@{variables('varFolderDate')}`
   - File Name: `Rodaten - Gestern.zip`
   - File Content: `@{items('Apply_to_each')?['contentBytes']}`

**If No**: Skip or log

### Step 5: Save Metadata File

After the ZIP is saved, add another action:

**Create file** (SharePoint) - metadata.txt:
- Site: Your SharePoint site
- Folder Path: `/Documents/Incoming/@{variables('varFolderDate')}`
- File Name: `metadata.txt`
- File Content:
  ```
  From: rotoforst@domain.com
  Date: @{variables('varFolderDate')}
  Subject: @{triggerOutputs()?['body/subject']}
  Timestamp: @{utcNow()}
  ```

### Step 6: Send Confirmation (Optional)

**Send an email (V2)**:
- To: your email or admin
- Subject: `Rotoforst file received - @{variables('varFolderDate')}`
- Body: `ZIP file saved to: Documents/Incoming/@{variables('varFolderDate')}`

---

## 🐍 STEP 2: Azure Automation + Python - Data Transformation

### Overview
An Azure Automation runbook executes a Python script to:
1. Download ZIP from SharePoint
2. Extract and transform Excel files
3. Convert to CSV format
4. Generate email body content

### Prerequisites

1. **Azure Automation Account** (create in Azure portal):
   - Automation Account Name: `BKWAutomation` (example)
   - Managed Identity: Enable system-assigned

2. **Python Modules** (add to Automation Account):
   - `openpyxl` (read/write Excel)
   - `pandas` (data manipulation)
   - `office365-rest-python-client` (SharePoint access)

### Setup Steps

#### 1. Create Azure Automation Account

1. Go to Azure Portal → **Automation Accounts**
2. Click **Create**
3. Fill:
   - Name: `BKWAutomation`
   - Resource Group: your group
   - Region: your region
4. Enable **System assigned managed identity**
5. Click **Create**

#### 2. Grant SharePoint Access

1. Go to your SharePoint site
2. Settings → **Site permissions**
3. Grant "Contribute" access to the managed identity
   - Or use app registration (advanced)

#### 3. Python Runbook Template

Create a **Python 3 Runbook** in Azure Automation:

**Name**: `Process_BKW_Files`

**Python Code**:

```python
import sys
import os
import json
import zipfile
import pandas as pd
from datetime import datetime
from io import BytesIO
import urllib.request
import urllib.parse

# Azure imports (install via Update Modules)
# from office365.runtime.auth.client_credential_auth import ClientCredentialAuth
# from office365.sharepoint.client_context import ClientContext

def download_from_sharepoint(site_url, file_relative_path, client_id, client_secret, tenant_id):
    """
    Download file from SharePoint using app registration.
    Alternative: Use Managed Identity with Graph API
    """
    # This example uses app registration authentication
    # You can alternatively use Managed Identity
    pass

def extract_zip(zip_bytes):
    """Extract ZIP file from bytes."""
    try:
        zip_file = zipfile.ZipFile(BytesIO(zip_bytes))
        extracted_files = {}
        for file_name in zip_file.namelist():
            if file_name.endswith(('.xlsx', '.xls')):
                extracted_files[file_name] = zip_file.read(file_name)
        return extracted_files
    except Exception as e:
        print(f"Error extracting ZIP: {str(e)}")
        return {}

def transform_excel_to_csv(excel_bytes, file_name):
    """
    Read Excel file, transform data, convert to CSV.
    """
    try:
        # Read Excel
        df = pd.read_excel(BytesIO(excel_bytes))
        
        # YOUR TRANSFORMATION LOGIC HERE
        # Example: remove empty rows, filter by status, convert dates, etc.
        
        # Remove empty rows
        df = df.dropna(how='all')
        
        # Example: Filter only 'Active' status (adjust to your logic)
        # if 'Status' in df.columns:
        #     df = df[df['Status'] == 'Active']
        
        # Convert to CSV string
        csv_content = df.to_csv(index=False)
        
        # Change extension from .xlsx to .csv
        csv_file_name = file_name.replace('.xlsx', '.csv').replace('.xls', '.csv')
        
        return csv_content, csv_file_name
        
    except Exception as e:
        print(f"Error transforming {file_name}: {str(e)}")
        return None, file_name

def generate_email_body(files_processed):
    """Generate email body with processing summary."""
    body = f"""
    <html>
    <body>
    <h2>BKW Data Processing Report</h2>
    <p>Processing Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}</p>
    <h3>Processed Files:</h3>
    <ul>
    """
    
    for file_name in files_processed:
        body += f"<li>{file_name}</li>"
    
    body += """
    </ul>
    <p>All files have been processed and converted to CSV format.</p>
    <p>Please review the attached CSV files for accuracy.</p>
    </body>
    </html>
    """
    
    return body

def main():
    """Main function to process BKW files."""
    
    # Get parameters from runbook input (or set hardcoded for testing)
    sharepoint_site = "https://yourorgname.sharepoint.com/sites/yoursite"
    folder_path = "Documents/Incoming/15-12-2025"
    zip_file_name = "Rodaten - Gestern.zip"
    
    print(f"Starting BKW file processing from {folder_path}")
    
    # STEP 1: Download ZIP from SharePoint
    # (Implementation depends on your auth method)
    # zip_bytes = download_from_sharepoint(...)
    
    # For testing, read from local file or mock data
    # zip_bytes = b'...'  # Your ZIP bytes here
    
    # STEP 2: Extract ZIP
    excel_files = extract_zip(zip_bytes)
    print(f"Extracted {len(excel_files)} Excel file(s)")
    
    # STEP 3: Transform each Excel to CSV
    csv_files = {}
    for excel_name, excel_data in excel_files.items():
        csv_content, csv_name = transform_excel_to_csv(excel_data, excel_name)
        if csv_content:
            csv_files[csv_name] = csv_content
            print(f"Converted {excel_name} → {csv_name}")
    
    # STEP 4: Generate email body
    email_body = generate_email_body(list(csv_files.keys()))
    
    # STEP 5: Save CSV files (to SharePoint, local storage, or pass to next step)
    # save_files_to_sharepoint(csv_files, output_folder)
    
    # STEP 6: Return output for Power Automate or email sending
    output = {
        "status": "success",
        "csv_files": list(csv_files.keys()),
        "email_body": email_body,
        "timestamp": datetime.now().isoformat()
    }
    
    print(json.dumps(output))
    return output

if __name__ == "__main__":
    main()
```

### Step-by-Step Usage

1. **In Azure Portal** → Automation Account → **Runbooks** → **Create Runbook**
   - Name: `Process_BKW_Files`
   - Type: `Python 3`

2. **Paste the Python code** above (customize transformation logic)

3. **Update Modules**:
   - Runtime Environments → Add modules: `openpyxl`, `pandas`, `azure-identity`, etc.

4. **Test the Runbook**:
   - Click **Test pane**
   - Adjust file paths in the code
   - Run and check output

### Key Customization Points

**File Transformation Logic** (line ~80):
```python
# Remove empty rows
df = df.dropna(how='all')

# Filter rows (example)
df = df[df['Column_Name'] == 'Value']

# Change data types
df['DateColumn'] = pd.to_datetime(df['DateColumn'])

# Rename columns
df = df.rename(columns={'OldName': 'NewName'})

# Remove duplicates
df = df.drop_duplicates()

# Fill missing values
df = df.fillna('')
```

---

## 📧 STEP 3: Email Delivery Options

### Option A: Python + Azure (Built-in to Runbook)

Add email sending to the same Python script:

```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from io import StringIO

def send_email_with_csv(csv_files, email_body, recipients):
    """Send email with CSV attachments."""
    
    sender = "noreply@yourorg.com"  # Your org's email
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    
    # Get credentials from Azure Key Vault (secure)
    # For now, use environment variables or hardcode for testing
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = f"BKW Processed Data - {datetime.now().strftime('%d-%m-%Y')}"
        
        # Attach email body
        msg.attach(MIMEText(email_body, 'html'))
        
        # Attach CSV files
        for csv_name, csv_content in csv_files.items():
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(csv_content.encode('utf-8'))
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename= {csv_name}')
            msg.attach(attachment)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        print(f"Email sent to {recipients}")
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

# In main() function:
recipients = ['recipient1@company.com', 'recipient2@company.com']
send_email_with_csv(csv_files, email_body, recipients)
```

**Scheduling:**
1. In Azure Automation → Runbook → **Link to schedule**
2. Create schedule: Daily at 8:00 AM
3. Runbook runs automatically every day

### Option B: Power Automate - Scheduled Email Sending

Create a **scheduled cloud flow** in Power Automate:

**Trigger**: **Scheduled cloud flow**
- Frequency: Daily
- Time: 8:00 AM
- Timezone: Your timezone

**Actions**:

1. **SharePoint - Get files (properties only)**:
   - Site: Your SharePoint
   - Library: Documents
   - Folder path: `/Incoming/@{formatDateTime(addDays(utcNow(), -1), 'dd-MM-yyyy')}`
   - (Gets yesterday's folder)

2. **Apply to each** → value: value from "Get files"

3. Inside loop:
   - **Condition**: Check if file ends with `.csv`
   - **If Yes**: Continue

4. **Send an email (V2)**:
   - To: `recipient1@company.com`; `recipient2@company.com`
   - Subject: `BKW Processed Data - @{formatDateTime(utcNow(), 'dd-MM-yyyy')}`
   - Body: Your email template
   - Attachments: Dynamically attach CSV files from SharePoint

**Note**: SharePoint attachment is tricky in Power Automate. Use:
- **Get file content** (SharePoint) for each CSV
- Then attach to email

---

## 📂 Folder Structure in SharePoint

```
Documents/
├── Incoming/
│   ├── 15-12-2025/
│   │   ├── Rodaten - Gestern.zip
│   │   └── metadata.txt
│   ├── 14-12-2025/
│   │   ├── Rodaten - Gestern.zip
│   │   └── metadata.txt
│
├── Processed/
│   ├── 15-12-2025/
│   │   ├── file1.csv
│   │   ├── file2.csv
│   │   └── processing_log.txt
│
├── Archive/
│   └── (old files for backup)
```

---

## ⚠️ Important Considerations

### File Size Limits:
- **Email attachments**: Max 25-30 MB per email
- **Azure**: Max 10-100 MB per file (depends on runbook type)
- **SharePoint**: Max 100 GB per site

### Performance:
- Large ZIP files may take 2-5 minutes to process
- Python script timeout: default 10 minutes per runbook (adjustable)
- Consider scheduling during off-peak hours

### Error Handling:
- Add try/except blocks in Python script for robustness
- Log errors to Application Insights or file
- Send error notification emails if processing fails
- Implement retry logic for transient failures

### Security:
- Store credentials in Azure Key Vault (never hardcode)
- Use Managed Identity for SharePoint access
- Encrypt sensitive data in transit
- Restrict SharePoint folder permissions to minimal access
- Monitor logs for failed attempts

---

## 🧪 Testing Checklist

**Power Automate Flow:**
- [ ] Email trigger fires correctly from Rotoforst
- [ ] ZIP file saves to correct SharePoint folder with date structure
- [ ] Metadata.txt file is created correctly
- [ ] Confirmation email received

**Azure Automation Runbook:**
- [ ] Python script runs without syntax errors
- [ ] ZIP file extracts correctly from SharePoint
- [ ] Excel files are found and readable
- [ ] Data transformation logic works as expected
- [ ] CSV files are generated with correct format
- [ ] Email body is generated properly

**Email Delivery:**
- [ ] CSV files are attached to email
- [ ] Recipients receive emails at scheduled time
- [ ] Email subject/body display correctly
- [ ] Files are not corrupted in transit

---

## 🐛 Common Issues & Solutions

### Issue 1: Power Automate trigger not firing
**Solution**: 
- Verify exact sender email in trigger settings
- Check exact subject line (case-sensitive)
- Ensure "Has Attachment" is set to "Yes"
- Test with manual trigger first

### Issue 2: Files not saving to SharePoint
**Solution**: 
- Verify SharePoint site URL is correct
- Check folder path exists (create manually if needed)
- Ensure Power Automate has "Contribute" permissions
- Check file name doesn't exceed SharePoint limits (255 chars)

### Issue 3: Python script fails in Azure Automation
**Solution**: 
- Check module versions are compatible
- Use Test pane to run and see detailed error messages
- Verify JSON format in print statements
- Add logging to track execution flow

### Issue 4: CSV files are empty or corrupted
**Solution**: 
- Check Excel file is not corrupted before processing
- Verify column names are readable (no special characters)
- Test transformation logic locally first
- Check file encoding is UTF-8

### Issue 5: Email not sending at scheduled time
**Solution**: 
- Check schedule is enabled and correct timezone
- Verify recipient email addresses are valid
- Check SMTP credentials in Key Vault
- Review runbook execution history for errors

---

## 📚 Additional Resources

- **Power Automate**: https://learn.microsoft.com/power-automate/
- **Azure Automation**: https://learn.microsoft.com/azure/automation/
- **Python Documentation**: https://docs.python.org/3/
- **Pandas**: https://pandas.pydata.org/docs/
- **SharePoint REST API**: https://learn.microsoft.com/sharepoint/dev/apis/rest/

---

## 📞 Support

If you encounter issues:
1. **Power Automate**: Check run history → expand failed action → see error details
2. **Azure Automation**: Check job history → output pane → see print/log statements
3. **General**: Test each component separately before combining
4. **Documentation**: Refer to Microsoft docs or community forums

---

## 🔄 Workflow Variations

### Variation 1: Trigger from Azure instead of Power Automate
- Remove Power Automate flow
- Create Azure Function triggered by email via Logic Apps
- Have Function call Python runbook directly

### Variation 2: Process multiple folders
- Modify Power Automate to loop through multiple SharePoint folders
- Python script processes all files in each folder

### Variation 3: Real-time processing
- Replace scheduled trigger with webhook
- Power Automate calls Azure Automation webhook when file is detected
- Results returned immediately to Power Automate

### Variation 4: Store in Azure Blob Storage instead of SharePoint
- Use Azure Storage Account for file storage
- Python script uploads CSVs to Blob Storage
- Power Automate retrieves from Blob for email

---

## 📋 Implementation Checklist

**Week 1: Setup**
- [ ] Create Azure Automation Account
- [ ] Set up SharePoint folder structure
- [ ] Create Power Automate email capture flow
- [ ] Test email trigger with sample email

**Week 2: Python Development**
- [ ] Set up Python environment locally
- [ ] Write and test ZIP extraction
- [ ] Implement data transformation logic
- [ ] Test CSV generation

**Week 3: Azure Integration**
- [ ] Create Python runbook in Azure
- [ ] Add required modules
- [ ] Test runbook in Test pane
- [ ] Configure SharePoint authentication

**Week 4: Email & Scheduling**
- [ ] Implement email sending logic
- [ ] Set up scheduled trigger
- [ ] Configure error notifications
- [ ] Run end-to-end test

**Week 5: Production**
- [ ] Deploy to production
- [ ] Monitor first few runs
- [ ] Adjust transformation logic if needed
- [ ] Document process for team

---

## 📅 Maintenance

**Daily**:
- Monitor email inbox for incoming files
- Check flow run history for errors

**Weekly**:
- Review processed files and CSV output
- Check for any failed transformations

**Monthly**:
- Archive old files from "Incoming" folder
- Review Azure Automation job history
- Update recipient email list if needed
- Check Azure costs and optimize if needed

**Quarterly**:
- Review transformation logic (any new requirements?)
- Update Python dependencies
- Test with new data formats
- Document any changes

---

**Version**: 2.0 (Hybrid: Power Automate + Azure Automation + Python)  
**Last Updated**: December 15, 2025  
**Architecture**: Three-tier solution (Capture → Transform → Deliver)
