import os
import re
import time
import json
import subprocess
from pathlib import Path
from urllib.parse import urlparse
from PyPDF2 import PdfReader
from falconpy import Hosts, HostGroup, RealTimeResponse, RealTimeResponseAdmin

# ====================
# Configuration Section
# ====================
vault_name = "<insert>"  # 1Password vault name
secret_name = "<insert>"  # 1Password secret name

# File Location
# Workstation serial

"""" *** CHANGE BELOW *** """
serial = "<insert>"  # Host serial number for the target machine
username = "<insert>"  # Host user account username
file_to_put = r"<insert>"  # File to deploy
renamed_file = r"<insert>"  # Optional: New name for the uploaded file
win_root_file_path = r"<insert>"
win_file_path = r"<insert>"
mac_file_path = "<insert>"
"""" *** CHANGE ABOVE *** """

# ====================
# PDF Utility Functions
# ====================

def check_pdf_for_links(pdf_path):
    """Check if the PDF contains external links and return the first link."""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        if "/Annots" in page:
            annotations = page["/Annots"]
            for annot in annotations:
                uri = annot.get_object().get("/URI")
                if uri:
                    print(f"Found external link in PDF: {uri}")
                    return uri  # Return the first found link
    return None


def trust_pdf_url(domain):
    """Add the domain to macOS trusted URL list for PDF viewing."""
    script = f"""
    tell application "Preview"
        do shell script "defaults write com.apple.Preview WebSecurityEnabled -bool true"
        do shell script "defaults write com.apple.Preview WebAllowedURLSchemes -array-add {domain}"
    end tell
    """
    try:
        subprocess.run(["osascript", "-e", script], check=True)
        print(f"Added {domain} to macOS trusted domains.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to add {domain} to macOS trusted domains. Error: {e}")

# ====================
# Function Definitions
# ====================

def authenticate_1password(vault_name, secret_name):
    """Authenticate into 1Password and retrieve a secret."""
    try:
        session_token = os.getenv("OP_SESSION_my")
        if not session_token:
            print("1Password session not found. Signing in...")
            signin_command = ["op", "signin", "--raw"]
            session_token = subprocess.check_output(signin_command, text=True).strip()
            os.environ["OP_SESSION_my"] = session_token
            print()  # Add blank line

        command = [
            "op", "item", "get", secret_name,
            "--vault", vault_name,
            "--format", "json"
        ]
        secret_data = json.loads(subprocess.check_output(command, text=True, env=os.environ))
        client_id = next((field["value"] for field in secret_data.get("fields", []) if field["label"] == "client_id"), None)
        client_secret = next((field["value"] for field in secret_data.get("fields", []) if field["label"] == "credential"), None)

        if not client_id or not client_secret:
            raise ValueError("Missing Client ID or Client Secret in the retrieved secret.")

        return client_id, client_secret

    except subprocess.CalledProcessError as e:
        print(f"Error interacting with 1Password: {e.output}")
        raise
    except json.JSONDecodeError:
        print("Failed to parse the secret as JSON.")
        raise


def initialize_apis(client_id, client_secret):
    """Initialize CrowdStrike API clients."""
    host_api = Hosts(client_id=client_id, client_secret=client_secret)
    host_group_api = HostGroup(auth_object=host_api)
    rtr_admin_api = RealTimeResponseAdmin(auth_object=host_api)
    rtr_api = RealTimeResponse(auth_object=host_api)
    return host_api, host_group_api, rtr_admin_api, rtr_api


def get_uploaded_files():
    """Retrieve a list of files uploaded to the RTR session."""
    put_file_ids = rtr_admin_api.list_put_files()["body"]["resources"]
    put_files = rtr_admin_api.get_put_files_v2(ids=put_file_ids)["body"]["resources"]

    print("\nUploaded files:")
    for element in put_files:
        print(element["name"])


def host_info():
    """Gather host info and return Device ID and Host Operating System."""
    host_filter = f"serial_number:*'*{serial}*'"

    # Get device ID of a specific serial
    device_id = host_api.query_devices_by_filter_scroll(filter=host_filter)["body"]["resources"][0]

    print("Device ID: " + str(device_id))

    online_status = host_api.get_online_state(ids=device_id)["body"]["resources"][0]["state"]

    if str(online_status) != "online":
        print("\nHost is offline. Please verify that the serial is correct then try again.")
        quit()

    # Get host operating system
    host_OS = host_api.get_device_details(ids=device_id)["body"]["resources"][0]["platform_name"]

    print("\nHost OS: " + str(host_OS))

    return device_id, host_OS


def enable_rtr(device_id):
    """Add host to RTR enabled group."""
    host_filter = f"device_id:'{device_id}'"

    add_hosts = host_group_api.perform_group_action(
        action_name="add-hosts",
        ids="<insert>",
        filter=host_filter,
    )

    if str(
        add_hosts["body"]["resources"][0]["assignment_rule"]
        != "'device_id:[],hostname:[]'"
    ):
        print("\nHost successfully added to RTR enabled group")
        print(
            "\nNew assignment rule: "
            + str(add_hosts["body"]["resources"][0]["assignment_rule"])
            + "\n"
        )
    else:
        print("\nHost could not be added to RTR enabled group\n")
        print(add_hosts)


def start_rtr_connection(device_id):
    """Start the RTR connection and return the Session ID."""
    session_id = ""
    regex = "[A-Za-z0-9]+-[A-Za-z0-9]+-[A-Za-z0-9]+-[A-Za-z0-9]+-[A-Za-z0-9]+"

    # Attempt to start RTR session, sleeping if RTR is not enabled yet
    while not re.match(regex, session_id):
        try:
            session_id = rtr_api.init_session(device_id=device_id, queue_offline=False)[
                "body"
            ]["resources"][0]["session_id"]

            print("Session ID: " + str(session_id))
        except IndexError:
            print("RTR is not yet enabled, sleeping 60 seconds\n")
            time.sleep(60)

    return session_id


def check_directory(session_id, file_path):
    """Check if directory exists and if so, prompt the user if they would like to continue."""
    # Execute cd command and get request ID
    check_if_directory_exists = rtr_admin_api.execute_admin_command(
        base_command="cd",
        session_id=session_id,
        command_string="cd " + file_path,
        persist=False,
    )["body"]["resources"][0]["cloud_request_id"]

    # Sleep to prevent RTR commands from executing too quickly
    time.sleep(2)

    # Check status of cd command
    check_if_directory_exists_response = rtr_admin_api.check_admin_command_status(
        cloud_request_id=check_if_directory_exists
    )["body"]["resources"][0]["stderr"]

    if "Cannot find path" in str(check_if_directory_exists_response):
        print("\nFolder does not exist, creating folder")
    else:
        user_response = (
            input(
                "\nDirectory already exists. Would you like to continue anyway? (y/n): "
            )
            .lower()
            .strip()
            == "y"
        )

        if not user_response:
            print("\nExiting program")
            quit()

    # Sleep to prevent RTR commands from executing too quickly
    time.sleep(2)


def create_directory(session_id, host_OS, file_path):
    """Ensure the directory exists and has the correct permissions."""
    file_path = os.path.normpath(file_path)  # Normalize the file path for consistency

    if host_OS == "Windows":
        print(f"\nCreating directory on Windows: {file_path}")

        # Create the directory
        mkdir_command = f'mkdir "{file_path}"'
        mkdir_response = rtr_admin_api.execute_admin_command(
            base_command="mkdir",
            session_id=session_id,
            command_string=mkdir_command,
            persist=False,
        )
        if mkdir_response["status_code"] != 201:
            print(f"Directory creation failed for {file_path}. Response: {mkdir_response}")
            raise RuntimeError(f"Failed to create directory: {mkdir_response}")

        time.sleep(2)  # Pause to ensure the directory is created

        # Reset and apply permissions
        icacls_reset_command = rf'icacls "{file_path}" /reset /T /C'
        icacls_grant_command = rf'icacls "{file_path}" /grant "{username}":(OI)(CI)(F) /inheritance:e'

        for command in [icacls_reset_command, icacls_grant_command]:
            icacls_response = rtr_admin_api.execute_admin_command(
                base_command="runscript",
                session_id=session_id,
                command_string=f"runscript -Raw='cmd.exe /c {command}'",
                persist=False,
            )
            if icacls_response["status_code"] != 201:
                print(f"Failed to apply permissions with command: {command}. Response: {icacls_response}")
                raise RuntimeError(f"Permission application failed: {icacls_response}")

    elif host_OS == "Mac":
        print(f"\nCreating directory on macOS: {file_path}")

        custom_script = rf"""
        if [ -d "{file_path}" ]; then
            chmod -R 777 "{file_path}";
        else
            mkdir -p "{file_path}" && chmod -R 777 "{file_path}";
        fi
        """
        mac_response = rtr_admin_api.execute_admin_command(
            base_command="runscript",
            session_id=session_id,
            command_string=f"runscript -Raw='{custom_script}'",
            persist=False,
        )
        if mac_response["status_code"] != 201:
            print(f"Failed to create or modify directory on macOS. Response: {mac_response}")
            raise RuntimeError(f"Failed to modify directory on macOS: {mac_response}")

    else:
        raise ValueError("Unsupported operating system.")

    print(f"\nEnsured directory {file_path} exists with updated permissions.")
    time.sleep(2)  # Prevent rapid RTR command execution



def put_file(session_id, file_path):
    """Put file in above directory."""
    # Execute cd command and get request ID
    change_directory = rtr_admin_api.execute_admin_command(
        base_command="cd",
        session_id=session_id,
        command_string="cd " + file_path,
        persist=False,
    )["body"]["resources"][0]["cloud_request_id"]

    # Sleep to prevent RTR commands from executing too quickly
    time.sleep(2)

    # Check status of cd command
    cd_response = rtr_admin_api.check_admin_command_status(
        cloud_request_id=change_directory
    )["body"]["resources"][0]["stdout"]

    print("\nChanged directory to " + str(cd_response))

    # Sleep to prevent RTR commands from executing too quickly
    time.sleep(2)

    # Execute put command and get request ID
    put_command = rtr_admin_api.execute_admin_command(
        base_command="put",
        session_id=session_id,
        command_string="put " + file_to_put,
        persist=False,
    )

    # Sleep to prevent RTR commands from executing too quickly
    time.sleep(2)

    # # Check status of put command
    try:
        put_response = rtr_admin_api.check_admin_command_status(
            cloud_request_id=put_command["body"]["resources"][0]["cloud_request_id"]
        )

        if "200" in str(put_response["status_code"]):
            print(file_to_put + " successfully put in " + file_path)
        else:
            print("Errors occurred putting " + file_to_put + " in " + file_path + "\n")
            print(put_response)
    except IndexError:
        print("Unable to find that filename.")
        print("Verify that file_to_put is in the below list and try again:\n")
        get_uploaded_files()
        quit()

    # Sleep to prevent RTR commands from executing too quickly
    time.sleep(2)


def rename_file(session_id, host_OS, file_path):
    """Rename file and apply permissions."""
    # Execute mv command and get request ID
    mv_file = rtr_admin_api.execute_admin_command(
        base_command="mv",
        session_id=session_id,
        command_string=f'mv "{file_to_put}" "{renamed_file}"',
        persist=False,
    )["body"]["resources"][0]["cloud_request_id"]

    time.sleep(2)  # Prevent rapid RTR commands

    # Check status of mv command
    mv_response = rtr_admin_api.check_admin_command_status(cloud_request_id=mv_file)

    if "200" in str(mv_response["status_code"]):
        print(f"\nSuccessfully renamed {file_to_put} to {renamed_file}")

        # Apply permissions to the renamed file
        full_file_path = os.path.join(file_path, renamed_file)
        change_permissions(session_id, host_OS, full_file_path, is_file=True)

        # Unblock the renamed file (Windows only)
        if host_OS == "Windows":
            unblock_file(session_id, full_file_path)

    else:
        print(f"\nErrors renaming {file_to_put}\n")
        print(mv_response)

    time.sleep(2)  # Prevent rapid RTR commands



def change_permissions(session_id, host_OS, path, is_file=False):
    """Change permissions for a file or directory to allow full read/write access."""
    path = os.path.normpath(path)  # Normalize the path for consistency

    # Set target_type before referencing it
    target_type = "file" if is_file else "directory"

    if host_OS == "Windows":
        print(f"\nApplying permissions to {target_type} on Windows: {path}")

        # Reset permissions
        reset_command = rf'icacls "{path}" /reset /T /C'

        # Grant full permissions
        grant_command = rf'icacls "{path}" /grant "{username}":(OI)(CI)(F) /inheritance:e'

        # Execute both commands
        for command in [reset_command, grant_command]:
            response = rtr_admin_api.execute_admin_command(
                base_command="runscript",
                session_id=session_id,
                command_string=f"runscript -Raw='cmd.exe /c {command}'",
                persist=False,
            )
            if response["status_code"] != 201:
                raise RuntimeError(f"Failed to apply permissions with command: {command}. Response: {response}")

        print(f"\nPermissions applied successfully to {target_type} on Windows.")

    elif host_OS == "Mac":
        print(f"\nApplying permissions to {target_type} on macOS: {path}")

        # macOS logic: Adjust permissions and ownership
        custom_script = rf"""
        chmod -R 777 "{path}";
        chown -R {username} "{path}";
        """

        mac_response = rtr_admin_api.execute_admin_command(
            base_command="runscript",
            session_id=session_id,
            command_string=f"runscript -Raw='{custom_script}'",
            persist=False,
        )

        if mac_response["status_code"] != 201:
            raise RuntimeError(f"Failed to set permissions for {target_type} {path}. Response: {mac_response}")

        print(f"\nPermissions applied successfully on macOS.")

    else:
        raise ValueError("Unsupported operating system.")

    time.sleep(2)  # Prevent rapid RTR command execution


def unblock_file(session_id, file_path):
    """Unblock the file since it did not originate on the host."""
    if renamed_file:
        full_file_path = os.path.join(file_path, renamed_file)
    else:
        full_file_path = os.path.join(file_path, file_to_put)

    # PowerShell command to unblock the file
    unblock_command = rf'Unblock-File -Path "{full_file_path}"'

    # Execute the unblock command via RTR
    unblock_response = rtr_admin_api.execute_admin_command(
        base_command="runscript",
        session_id=session_id,
        command_string=f"runscript -Raw='powershell.exe -Command \"{unblock_command}\"'",
        persist=False,
    )

    if unblock_response["status_code"] == 201:
        print("\nFile unblocked successfully")
    else:
        print("\nFile unblock failed")
        print(unblock_response)

    # Sleep to prevent RTR commands from executing too quickly
    time.sleep(2)



def remove_from_rtr(device_id):
    """Remove host from RTR enabled group."""
    device_filter = f"device_id:'{device_id}'"

    # Remove from CD Deployment host group, which disables RTR
    rtr_removal = host_group_api.perform_group_action(
        action_name="remove-hosts",
        ids="<insert>",
        filter=device_filter,
    )

    if "200" in str(rtr_removal["status_code"]):
        print("\n" + str(serial) + " removed from RTR enabled group")
    else:
        print("\n" + str(serial) + " could not be removed from RTR enabled group\n")
        print(rtr_removal)


def main():
    device_id, host_OS = host_info()

    file_path = os.path.normpath(win_file_path if host_OS == "Windows" else mac_file_path)

    enable_rtr(device_id)

    session_id = start_rtr_connection(device_id)

    check_directory(session_id, file_path)
    create_directory(session_id, host_OS, file_path)  # Permissions applied to directory here
    put_file(session_id, file_path)

    if renamed_file:
        rename_file(session_id, host_OS, file_path)  # Permissions applied to renamed file here

        renamed_file_path = os.path.normpath(os.path.join(file_path, renamed_file))

        print(f"\nVerifying renamed file exists on remote device: '{renamed_file_path}'...")

        try:
            validate_file_command = (
                rtr_admin_api.execute_admin_command(
                    base_command="ls",
                    session_id=session_id,
                    command_string=f"ls \"{renamed_file_path}\"",
                    persist=False,
                ) if host_OS == "Mac" else
                rtr_admin_api.execute_admin_command(
                    base_command="runscript",
                    session_id=session_id,
                    command_string=f"runscript -Raw='dir \"{renamed_file_path}\"'",
                    persist=False,
                )
            )
            resources = validate_file_command["body"].get("resources", [])
            if not resources or "No such file or directory" in resources[0].get("stderr", ""):
                raise FileNotFoundError(f"Renamed file '{renamed_file}' not found.")
            print(f"\nRenamed file '{renamed_file}' confirmed on remote device.")
        except Exception as e:
            print(f"\nError verifying renamed file: {e}")
            raise

    remove_from_rtr(device_id)
    rtr_api.delete_session(session_id=session_id)



if __name__ == "__main__":
    try:
        # Authenticate using 1Password
        client_id, client_secret = authenticate_1password(vault_name, secret_name)

        # Initialize APIs
        host_api, host_group_api, rtr_admin_api, rtr_api = initialize_apis(client_id, client_secret)

        # Run the main deployment logic
        main()

        # Success message
        print("\nDeployment completed successfully! The file has been deployed and verified.")

    except Exception as e:
        print(f"An error occurred during deployment: {e}")
