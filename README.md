# Automated Canary Token Deployment via CrowdStrike RTR

## Overview

Manual Canary Token deployment is a tedious and error-prone process, especially when managing multiple endpoints. Canary Tokens act as digital tripwires, alerting defenders when malicious actors interact with them. However, deploying these tokens manually across various devices poses significant challenges:
- **Time-Consuming**: Manually creating directories and placing tokens.
- **Prone to Errors**: Incorrect configurations can lead to ineffective deployments.
- **Lack of Scalability**: Enterprises with large networks cannot efficiently scale manual processes.

This repository contains two scripts designed to automate and streamline Canary Token deployment using CrowdStrike's Real-Time Response (RTR) API.

## Why These Scripts Were Created

To address the challenges of manual deployment, these scripts:
- Upload  and deploy tokenized files securely to endpoints using CrowdStrike RTR.
- Automate directory creation with proper permissions.
- Rename files to match the desired naming conventions.
- Ensure permissions are correctly applied for both macOS and Windows environments.
- Provide verification steps to confirm successful deployment.

## Scripts

### 1. `Upload_File_Crowdstrike.py`

This script uploads tokenized files to CrowdStrike's cloud repository for access during deployment. Key features:
- **File Validation**: Ensures the file exists locally before uploading.
- **CrowdStrike Integration**: Uses the RTR API to upload files to the cloud.
- **Metadata Handling**: Includes optional descriptions for better file identification.

### Upload Script Output
When running the upload script, you can expect output similar to this:
```
Starting file upload to CrowdStrike cloud...
File 'CanaryToken.docx' successfully uploaded and verified in the cloud repository.
Upload completed!
```

### 2. `Deployment.py`

This script automates the deployment process by:
- **Identifying Target Hosts**: Using device serial numbers to query and retrieve host information via CrowdStrike API.
- **Setting Up Directories**: Ensuring directories exist with appropriate permissions.
- **Uploading Files**: Placing Canary Tokens in the specified directories.
- **Renaming and Verifying Files**: Confirming file existence and renaming for consistency.
- **Cleaning Up**: Removing the target device from RTR-enabled groups post-deployment.

### Deployment Script Output
When running the deployment script, you can expect output similar to this:

```
Device ID: 47692ac900b243e49ff0619e0883ad52
Host OS: Windows
Host successfully added to RTR enabled group
New assignment rule: device_id:[],hostname:['TargetHost.local']
Session ID: 8bf1b7ac-8424-401e-9bb7-6b996e76369a
Folder does not exist, creating folder
Ensured directory C:\Users\JohnDoe\Documents\Sensitive exists with updated permissions
Changed directory to C:\Users\JohnDoe\Documents\Sensitive
File CanaryToken.docx successfully put in C:\Users\JohnDoe\Documents\Sensitive
Successfully renamed CanaryToken.docx to DecoyToken.docx
Renamed file 'DecoyToken.docx' confirmed on remote device
Deployment completed successfully!
```

## Key Features

- **Cross-Platform Compatibility**: Supports macOS and Windows environments.
- **Secure Authentication**: Leverages 1Password for fetching API credentials securely.
- **Automated Permissions**: Ensures folders and files are accessible by the intended users.
- **Verification**: Validates file placement and permissions.

## Prerequisites

1. **Python Environment**: Ensure Python 3.7 or higher is installed.
2. **Dependencies**: Install required packages from `requirements.txt`.
3. **CrowdStrike RTR Access**: Ensure you have API credentials with permissions to use RTR features.
4. **1Password CLI**: Install and configure the `op` CLI for secure credential management.
5. **Tokenized Files**: Prepare the Canary Tokens you wish to deploy.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
