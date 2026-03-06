import os
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient

load_dotenv()

AZURE_STORAGE_ACCOUNT_URL = os.environ.get("AZURE_STORAGE_ACCOUNT_URL", "")
AZURE_STORAGE_ACCOUNT_NAME = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME", "")
AZURE_STORAGE_CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
AZURE_STORAGE_CONTAINER_NAME = os.environ.get("AZURE_STORAGE_CONTAINER_NAME", "models")


def get_blob_service_client():
    """Get BlobServiceClient using connection string or DefaultAzureCredential."""
    if AZURE_STORAGE_CONNECTION_STRING:
        return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    elif AZURE_STORAGE_ACCOUNT_URL:
        credential = DefaultAzureCredential()
        return BlobServiceClient(
            account_url=AZURE_STORAGE_ACCOUNT_URL, credential=credential
        )
    else:
        raise ValueError(
            "AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_URL must be set"
        )


def get_container_client(container_name=None):
    """Get ContainerClient for the specified container."""
    blob_service_client = get_blob_service_client()
    container = container_name or AZURE_STORAGE_CONTAINER_NAME
    return blob_service_client.get_container_client(container)


def create_container(container_name=None):
    """Create a new blob container if it doesn't exist."""
    container_name = container_name or AZURE_STORAGE_CONTAINER_NAME
    blob_service_client = get_blob_service_client()

    try:
        container_client = blob_service_client.get_container_client(container_name)
        if container_client.exists():
            print(f"Container '{container_name}' already exists.")
            return container_client

        container_client = blob_service_client.create_container(container_name)
        print(f"Container '{container_name}' created successfully.")
        return container_client
    except Exception as ex:
        print(f"Error creating container: {ex}")
        raise


def upload_blob(container_name, file_path, blob_name=None):
    """Upload a local file to blob storage."""
    container_client = get_container_client(container_name)

    blob_name = blob_name or os.path.basename(file_path)

    try:
        blob_client = container_client.get_blob_client(blob_name)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        print(f"Uploaded '{file_path}' as '{blob_name}' successfully.")
    except Exception as ex:
        print(f"Error uploading blob: {ex}")
        raise


def download_blob(container_name, blob_name, download_path):
    """Download a blob from storage to local file."""
    container_client = get_container_client(container_name)

    try:
        blob_client = container_client.get_blob_client(blob_name)
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        print(f"Downloaded '{blob_name}' to '{download_path}' successfully.")
    except Exception as ex:
        print(f"Error downloading blob: {ex}")
        raise


def list_blobs(container_name, prefix=None):
    """List all blobs in a container."""
    container_client = get_container_client(container_name)

    try:
        blobs = container_client.list_blobs(name_starts_with=prefix)
        blob_list = []
        for blob in blobs:
            blob_list.append(blob.name)
            print(f"  - {blob.name}")
        return blob_list
    except Exception as ex:
        print(f"Error listing blobs: {ex}")
        raise


def delete_blob(container_name, blob_name):
    """Delete a blob from storage."""
    container_client = get_container_client(container_name)

    try:
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.delete_blob()
        print(f"Deleted '{blob_name}' successfully.")
    except Exception as ex:
        print(f"Error deleting blob: {ex}")
        raise


def upload_directory(container_name, local_dir, prefix=""):
    """Upload all files from a local directory to blob storage."""
    container_client = get_container_client(container_name)

    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            blob_name = os.path.join(prefix, local_path.replace(local_dir + "/", ""))

            try:
                blob_client = container_client.get_blob_client(blob_name)
                with open(local_path, "rb") as data:
                    blob_client.upload_blob(data, overwrite=True)
                print(f"Uploaded '{local_path}' as '{blob_name}'.")
            except Exception as ex:
                print(f"Error uploading '{local_path}': {ex}")


def download_directory(container_name, local_dir, prefix=""):
    """Download all blobs from a prefix to local directory."""
    container_client = get_container_client(container_name)

    os.makedirs(local_dir, exist_ok=True)

    try:
        blobs = container_client.list_blobs(name_starts_with=prefix)
        for blob in blobs:
            if blob.name.endswith("/"):
                continue

            file_name = blob.name.replace(prefix, "")
            local_file_path = os.path.join(local_dir, file_name)

            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

            blob_client = container_client.get_blob_client(blob.name)
            with open(local_file_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            print(f"Downloaded '{blob.name}' to '{local_file_path}'.")
    except Exception as ex:
        print(f"Error downloading directory: {ex}")
        raise


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Azure Blob Storage Management")
    parser.add_argument(
        "action",
        choices=[
            "create",
            "upload",
            "download",
            "list",
            "delete",
            "upload-dir",
            "download-dir",
        ],
        help="Action to perform",
    )
    parser.add_argument(
        "--container", default=AZURE_STORAGE_CONTAINER_NAME, help="Container name"
    )
    parser.add_argument("--file", help="File path (for upload/download)")
    parser.add_argument("--blob", help="Blob name (for upload/download/delete)")
    parser.add_argument("--prefix", help="Prefix for listing/downloading")
    parser.add_argument("--dir", help="Directory path (for upload-dir/download-dir)")

    args = parser.parse_args()

    if args.action == "create":
        create_container(args.container)
    elif args.action == "upload":
        if not args.file or not args.blob:
            print("Error: --file and --blob required for upload")
            sys.exit(1)
        upload_blob(args.container, args.file, args.blob)
    elif args.action == "download":
        if not args.blob or not args.file:
            print("Error: --blob and --file required for download")
            sys.exit(1)
        download_blob(args.container, args.blob, args.file)
    elif args.action == "list":
        list_blobs(args.container, args.prefix)
    elif args.action == "delete":
        if not args.blob:
            print("Error: --blob required for delete")
            sys.exit(1)
        delete_blob(args.container, args.blob)
    elif args.action == "upload-dir":
        if not args.dir:
            print("Error: --dir required for upload-dir")
            sys.exit(1)
        upload_directory(args.container, args.dir, args.prefix or "")
    elif args.action == "download-dir":
        if not args.dir:
            print("Error: --dir required for download-dir")
            sys.exit(1)
        download_directory(args.container, args.dir, args.prefix or "")
