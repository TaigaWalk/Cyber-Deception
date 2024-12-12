## Overview

Canary tokens are a powerful tool for deception in cybersecurity, designed to alert defenders of potential breaches by acting as enticing bait for attackers. However, manually deploying these tokens across an organization can be tedious, error-prone, and time-intensive.

This repository contains two Python scripts designed to streamline the deployment of canary tokens:
- **Deployment Script**: Automatically deploys and verifies the placement of files on target machines using CrowdStrike’s Real-Time Response (RTR) APIs.
- **Upload Script**: Uploads files to the CrowdStrike cloud for use in RTR operations.

These scripts are platform-agnostic, supporting both macOS and Windows environments.

---

## Problem Statement

### Manual Deployment Challenges
- **Time-Consuming**: Placing tokens manually across multiple endpoints is inefficient.
- **Error-Prone**: Ensuring consistency in token placement and configuration is difficult at scale.
- **Scalability Issues**: Large organizations cannot feasibly manage manual deployments for hundreds or thousands of endpoints.

### Why This Solution?
To address these challenges, this solution leverages CrowdStrike RTR APIs to automate:
- Directory creation and permission setting.
- File uploading and placement.
- Token renaming for authenticity.
- Verification to ensure deployment success.

Additionally, sensitive credentials like API keys are securely managed using 1Password, ensuring a secure and streamlined authentication process.

---

## High-Level Functionality

### Upload Script (`Upload_File_Crowdstrike.py`)
1. **File Upload**:
   - Uploads local files to CrowdStrike’s cloud repository for use during RTR operations.
2. **File Verification**:
   - Confirms the successful upload of files.

### Deployment Script (`Deployment.py`)
1. **Authenticate with 1Password**: Retrieves CrowdStrike API credentials securely.
2. **Initialize RTR Connection**: Starts an RTR session on the target machine.
3. **Directory Management**:
   - Creates directories with appropriate permissions (macOS: `chmod`, Windows: `icacls`).
   - Ensures directories are prepped for token placement.
4. **File Upload and Placement**:
   - Uploads the specified file to the desired directory.
   - Renames the file for added authenticity.
5. **Verification**:
   - Validates that the file exists and has appropriate permissions post-deployment.
6. **Cleanup**:
   - Removes the device from the RTR-enabled group once the deployment is complete.

## Platform Compatibility:
- Both scripts support macOS and Windows.
