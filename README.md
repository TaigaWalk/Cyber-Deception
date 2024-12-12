# Cyber-Deception
Automated Canary Token Deployment

Overview
Canary tokens are a powerful tool for deception in cybersecurity, designed to alert defenders of potential breaches by acting as enticing bait for attackers. However, manually deploying these tokens across an organization can be tedious, error-prone, and time-intensive.

This repository contains two Python scripts designed to streamline the deployment of canary tokens:
  1. Deployment Script: Automatically deploys and verifies the placement of files on target machines using CrowdStrike’s Real-Time Response (RTR) APIs.
  2. Upload Script: Uploads files to the CrowdStrike cloud for use in RTR operations.

These scripts are platform-agnostic, supporting both macOS and Windows environments.

Problem Statement
Manual Deployment Challenges
1. Time-Consuming: Placing tokens manually across multiple endpoints is inefficient.
2. Error-Prone: Ensuring consistency in token placement and configuration is difficult at scale.
3. Scalability Issues: Large organizations cannot feasibly manage manual deployments for hundreds or thousands of endpoints.

Why This Solution?
To address these challenges, this solution leverages CrowdStrike RTR APIs to automate:
-Directory creation and permission setting.
-File uploading and placement.
-Token renaming for authenticity.
-Verification to ensure deployment success.

Additionally, sensitive credentials like API keys are securely managed using 1Password, ensuring a secure and streamlined authentication process.

High-Level Functionality
Deployment Script (Deployment.py)
Authenticate with 1Password: Retrieves CrowdStrike API credentials securely.
Initialize RTR Connection: Starts an RTR session on the target machine.
Directory Management:
Creates directories with appropriate permissions (macOS: chmod, Windows: icacls).
Ensures directories are prepped for token placement.
File Upload and Placement:
Uploads the specified file to the desired directory.
Renames the file for added authenticity.
Verification:
Validates that the file exists and has appropriate permissions post-deployment.
Cleanup:
Removes the device from the RTR-enabled group once the deployment is complete.
Upload Script (Upload_File_Crowdstrike.py)
File Upload:
Uploads local files to CrowdStrike’s cloud repository for use during RTR operations.
File Verification:
Confirms the successful upload of files.
