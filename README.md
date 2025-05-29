# Automated Canary Token Deployment via CrowdStrike RTR

## Overview

Canary tokens are a powerful tool for deception in cybersecurity, designed to alert defenders of potential breaches by acting as enticing bait for attackers. However, manually deploying these tokens across an organization can be tedious, error-prone, and time-intensive.

This repository provides two Python scripts that automate and streamline the deployment of Canary Tokens using CrowdStrike's Real-Time Response (RTR) API:

- **Deployment Script**: Automatically deploys and verifies the placement of files on target machines using CrowdStrike RTR.
- **Upload Script**: Uploads files to CrowdStrike’s cloud repository for use in RTR operations.

---

## Why These Scripts Were Created

Manual Canary Token deployment poses several challenges:

- **Time-Consuming**: Repetitive directory creation and file transfers.
- **Error-Prone**: Easy to misplace or misconfigure tokens.
- **Lack of Scalability**: Difficult to deploy widely across large environments.

These scripts address these issues by:
- Uploading and placing tokenized files across endpoints.
- Creating directories with correct permissions (macOS and Windows).
- Renaming tokens to increase believability.
- Verifying that deployments succeeded.

---

## Scripts

### 1. `Upload_File_Crowdstrike.py`

Uploads tokenized files to CrowdStrike’s cloud for use in deployments.

**Features:**
- Verifies local file presence.
- Uploads to RTR cloud storage.
- Optional metadata tagging for easier file management.

**Example Output:**
```
Starting file upload to CrowdStrike cloud...
File 'CanaryToken.docx' successfully uploaded and verified in the cloud repository.
Upload completed!
```

---

### 2. `Deployment.py`

Deploys Canary Tokens to endpoints using CrowdStrike RTR APIs.

**Key Steps:**
1. **Authenticate via 1Password**: Securely fetches API credentials.
2. **Establish RTR Session**: Initiates a session with the target endpoint.
3. **Directory Creation**: Ensures directories exist and sets proper permissions.
4. **File Upload & Rename**: Uploads the file, renames it for authenticity.
5. **Verification**: Confirms file placement and accessibility.
6. **Cleanup**: Removes the host from RTR-enabled groups post-deployment.

**Example Output:**
```
Device ID: 47692ac900b243e49ff0619e0883ad52
Host OS: Windows
Host successfully added to RTR enabled group
Session ID: 8bf1b7ac-8424-401e-9bb7-6b996e76369a
Ensured directory exists with updated permissions
File CanaryToken.docx successfully uploaded
Successfully renamed CanaryToken.docx to DecoyToken.docx
Deployment completed successfully!
```

---

## Key Features

- ✅ Cross-platform support (macOS and Windows)
- 🔐 Secure credential management via 1Password CLI
- 📁 Automated directory and permission setup
- 🛡️ Verification to ensure successful token deployment

---

## Prerequisites

1. **Python 3.7+**
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. **CrowdStrike RTR API credentials** with necessary permissions.
4. **1Password CLI (`op`)** installed and authenticated.
5. Prepared **Canary Token** files.

---

## License

This project is licensed under the GPL-3.0 License. See the `LICENSE` file for more details.
