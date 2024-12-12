import os
import platform
import subprocess
import json
from falconpy import RealTimeResponseAdmin, OAuth2


# ====================
# Function Definitions
# ====================

def authenticate_1password(vault_name, secret_name):
    """
    Authenticate into 1Password and retrieve a secret.

    This function checks if a valid session with 1Password exists. If not,
    it authenticates using the `op` CLI. Then it retrieves the specified
    secret from the given vault.

    Args:
        vault_name (str): The name of the 1Password vault containing the secret.
        secret_name (str): The name of the secret to retrieve.

    Returns:
        dict: The requested secret data in JSON format.

    Raises:
        CalledProcessError: If the `op` command fails.
        JSONDecodeError: If the retrieved data is not valid JSON.
    """
    try:
        # Check if 1Password session is active; if not, sign in
        session_token = os.getenv("OP_SESSION_my")
        if not session_token:
            print("1Password session not found. Signing in...")
            signin_command = ["op", "signin", "--raw"]
            session_token = subprocess.check_output(signin_command, text=True).strip()
            os.environ["OP_SESSION_my"] = session_token

        # Fetch the secret from the specified vault
        command = [
            "op", "item", "get", secret_name,
            "--vault", vault_name,
            "--format", "json"
        ]
        secret_data = subprocess.check_output(command, text=True, env=os.environ)
        return json.loads(secret_data)

    except subprocess.CalledProcessError as e:
        # Handle errors in executing the `op` command
        if "isn't a vault in this account" in str(e.output):
            print(f"The specified vault '{vault_name}' does not exist. Check the vault name or ID.")
        else:
            print(f"Error interacting with 1Password: {e.output}")
        raise
    except json.JSONDecodeError:
        # Handle cases where the retrieved data is not valid JSON
        print("Failed to parse the secret as JSON.")
        raise


def get_crowdstrike_credentials(vault_name, secret_name):
    """
    Retrieve CrowdStrike API credentials from 1Password.

    This function retrieves a secret from 1Password and extracts the
    `client_id` and `client_secret` fields for CrowdStrike API access.

    Args:
        vault_name (str): The name of the 1Password vault containing the secret.
        secret_name (str): The name of the secret to retrieve.

    Returns:
        tuple: (client_id, client_secret)

    Raises:
        ValueError: If the required fields are missing from the secret.
    """
    secret = authenticate_1password(vault_name, secret_name)

    # Extract client_id and credential
    client_id = next((field["value"] for field in secret.get("fields", []) if field["label"] == "client_id"), None)
    client_secret = next((field["value"] for field in secret.get("fields", []) if field["label"] == "credential"), None)

    if not client_id or not client_secret:
        raise ValueError("Missing Client ID or Client Secret in the retrieved secret.")

    return client_id, client_secret


def check_api_credentials(client_id, client_secret):
    """
    Verify CrowdStrike API credentials.

    Sends a test request to ensure the provided API credentials are valid.

    Args:
        client_id (str): CrowdStrike API Client ID.
        client_secret (str): CrowdStrike API Client Secret.

    Returns:
        bool: True if credentials are valid, False otherwise.
    """
    oauth2 = OAuth2(client_id=client_id, client_secret=client_secret)
    response = oauth2.token()

    # Handle both 200 and 201 as successful responses
    if response["status_code"] == 200:
        print("CrowdStrike API credentials are valid.")
        return True
    else:
        print(f"Failed to authenticate API credentials. Response: {response}")
        return False


def upload_file_to_crowdstrike(client_id, client_secret, file_path, description):
    """
    Upload a file to CrowdStrike for use with Real-Time Response (RTR).

    This function initializes the RTR Admin API client and uploads a
    specified file to CrowdStrike for later use in RTR operations.

    Args:
        client_id (str): CrowdStrike API Client ID.
        client_secret (str): CrowdStrike API Client Secret.
        file_path (str): Path to the file to upload.
        description (str): Description for the uploaded file.

    Raises:
        FileNotFoundError: If the file to upload does not exist.
        Exception: For any errors during the file upload process.
    """
    # Initialize RTR Admin API client
    rtr_admin_api = RealTimeResponseAdmin(client_id=client_id, client_secret=client_secret)

    # Ensure the file exists before attempting upload
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Upload the file
    try:
        with open(file_path, "rb") as file_data:
            files = [
                (
                    'file',
                    (
                        os.path.basename(file_path),
                        file_data,
                        'application/octet-stream'
                    )
                )
            ]
            response = rtr_admin_api.create_put_files(
                name=os.path.basename(file_path),
                description=description,
                files=files
            )

        # Handle the API response
        if response["status_code"] == 200:
            print(f"File '{file_path}' successfully uploaded to CrowdStrike.")
        else:
            print("Failed to upload the file. Response:", response)

    except Exception as e:
        print(f"An error occurred during file upload: {e}")
        raise


# ==========================
# Main Execution Entry Point
# ==========================
if __name__ == "__main__":
    # 1Password vault and secret details
    vault_name = "<insert>"
    secret_name = "<insert>"

    # CHANGE BELOW
    # File details for upload
    if platform.system() == "Windows":
        file_path = r"<insert file path>"
    elif platform.system() == "Darwin":  # macOS
        file_path = "<insert file path>"
    else:
        raise EnvironmentError("Unsupported operating system. Only macOS and Windows are supported.")

    description = "Tokenized Test file for RTR operations"
    #CHANGE ABOVE

    try:
        # Step 1: Retrieve CrowdStrike credentials from 1Password
        client_id, client_secret = get_crowdstrike_credentials(vault_name, secret_name)

        # Step 2: Verify API credentials
        if not check_api_credentials(client_id, client_secret):
            raise Exception("Invalid CrowdStrike API credentials. Aborting operation.")

        # Step 3: Upload the file to CrowdStrike
        upload_file_to_crowdstrike(client_id, client_secret, file_path, description)

    except Exception as err:
        print(f"Failed to complete the operation: {err}")
