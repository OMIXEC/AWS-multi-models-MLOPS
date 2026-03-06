import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContainerClient

load_dotenv()

CONNECTION_STRING = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
CONTAINER_NAME = os.environ.get("AZURE_CONTAINER_NAME", "models")


def get_blob_service_client():
    return BlobServiceClient.from_connection_string(CONNECTION_STRING)


def get_container_client():
    client = get_blob_service_client()
    return client.get_container_client(CONTAINER_NAME)


def download_file(blob_name, file_path):
    container = get_container_client()
    blob_client = container.get_blob_client(blob_name)

    with open(file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())
    print(f"Downloaded {blob_name} to {file_path}")


def download_dir(local_path, model_name):
    container = get_container_client()

    os.makedirs(local_path, exist_ok=True)

    blob_list = container.list_blobs(name_starts_with=model_name)

    for blob in blob_list:
        if blob.name.endswith("/"):
            continue

        file_name = blob.name.replace(model_name, "")
        local_file_path = os.path.join(local_path, file_name)

        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        blob_client = container.get_blob_client(blob.name)
        with open(local_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        print(f"Downloaded {blob.name} to {local_file_path}")


def upload_file(file_path, blob_name):
    container = get_container_client()
    blob_client = container.get_blob_client(blob_name)

    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    print(f"Uploaded {file_path} to {blob_name}")


def upload_dir(local_dir, prefix):
    container = get_container_client()

    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            blob_name = os.path.join(prefix, local_path.replace(local_dir + "/", ""))

            blob_client = container.get_blob_client(blob_name)
            with open(local_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            print(f"Uploaded {local_path} to {blob_name}")
