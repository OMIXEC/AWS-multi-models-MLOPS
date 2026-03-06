import os
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv()

GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "your-bucket-name")


def create_bucket(bucket_name, location="US"):
    """Creates a new bucket in Google Cloud Storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    bucket.storage_class = "STANDARD"
    new_bucket = storage_client.create_bucket(bucket, location=location)

    print(
        f"Bucket {new_bucket.name} created in {new_bucket.location} with storage class {new_bucket.storage_class}"
    )
    return new_bucket


def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")


if __name__ == "__main__":
    # Example usage:
    # create_bucket("my-ml-models-bucket-gcp")
    # upload_blob("my-ml-models-bucket-gcp", "model.pt", "models/model.pt")
    pass
