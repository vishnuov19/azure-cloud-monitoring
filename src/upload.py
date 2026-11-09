# upload.py
import logging, os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError

ACCOUNT_URL = "https://cloudmonitorstorage01.blob.core.windows.net"
CONTAINER_NAME = "raw-data"

def get_blob_service_client():
    return BlobServiceClient(account_url=ACCOUNT_URL, credential=DefaultAzureCredential())

def upload_file(local_path, blob_name=None):
    if not os.path.exists(local_path):
        logging.error(f"Upload failed - file not found: {local_path}")
        return False
    blob_name = blob_name or os.path.basename(local_path)
    try:
        client = get_blob_service_client()
        blob_client = client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        logging.info(f"Uploaded '{local_path}' -> {CONTAINER_NAME}/{blob_name}")
        return True
    except AzureError as e:
        logging.error(f"Upload failed for '{blob_name}': {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    upload_file("data/sales_data.csv")