import os
from google.cloud import storage

BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "your-bucket-name")


def download_file(blob_name, file_path):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(file_path)
    print(f"Downloaded {blob_name} to {file_path}")


def download_dir(local_path, model_name):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    os.makedirs(local_path, exist_ok=True)

    blobs = bucket.list_blobs(prefix=model_name)

    for blob in blobs:
        if blob.name.endswith("/"):
            continue

        file_name = blob.name.replace(model_name, "")
        local_file_path = os.path.join(local_path, file_name)

        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        blob.download_to_filename(local_file_path)
        print(f"Downloaded {blob.name} to {local_file_path}")


def upload_file(file_path, blob_name):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
    print(f"Uploaded {file_path} to {blob_name}")


def upload_dir(local_dir, prefix):
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            blob_name = os.path.join(prefix, local_path.replace(local_dir + "/", ""))

            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_path)
            print(f"Uploaded {local_path} to {blob_name}")
