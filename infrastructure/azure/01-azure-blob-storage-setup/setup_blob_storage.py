import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

load_dotenv()

AZURE_STORAGE_ACCOUNT_URL = os.environ.get("AZURE_STORAGE_ACCOUNT_URL", "")
AZURE_STORAGE_CONTAINER_NAME = os.environ.get("AZURE_STORAGE_CONTAINER_NAME", "models")


def upload_blob_to_container(account_url, container_name, local_file_path, blob_name):
    """Uploads a local file to an Azure Blob Storage container."""
    try:
        # Create a generic credential object
        default_credential = DefaultAzureCredential()

        # Create the BlobServiceClient object
        blob_service_client = BlobServiceClient(
            account_url, credential=default_credential
        )

        # Get the container client
        container_client = blob_service_client.get_container_client(
            container=container_name
        )

        # Create a blob client using the local file name as the name for the blob
        blob_client = container_client.get_blob_client(blob=blob_name)

        print(f"Uploading to Azure Storage as blob: {blob_name}")

        # Upload the created file
        with open(file=local_file_path, mode="rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        print("Upload complete.")

    except Exception as ex:
        print("Exception:")
        print(ex)


if __name__ == "__main__":
    # Example usage:
    # account_url = "https://<storageaccountname>.blob.core.windows.net"
    # upload_blob_to_container(account_url, "ml-models", "model.pt", "models/model.pt")
    pass
