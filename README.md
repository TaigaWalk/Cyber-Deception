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

### 2. `Deployment.py`

This script automates the deployment process by:
- **Identifying Target Hosts**: Using device serial numbers to query and retrieve host information via CrowdStrike API.
- **Setting Up Directories**: Ensuring directories exist with appropriate permissions.
- **Uploading Files**: Placing Canary Tokens in the specified directories.
- **Renaming and Verifying Files**: Confirming file existence and renaming for consistency.
- **Cleaning Up**: Removing the target device from RTR-enabled groups post-deployment.

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
