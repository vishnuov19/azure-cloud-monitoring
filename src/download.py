# download.py
import logging, os
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError, ResourceNotFoundError

ACCOUNT_URL = "https://cloudmonitorstorage01.blob.core.windows.net"
CONTAINER_NAME = "raw-data"

def get_blob_service_client():
    return BlobServiceClient(account_url=ACCOUNT_URL, credential=DefaultAzureCredential())

def list_blobs():
    try:
        client = get_blob_service_client()
        container_client = client.get_container_client(CONTAINER_NAME)
        blobs = [b.name for b in container_client.list_blobs()]
        logging.info(f"Blobs in '{CONTAINER_NAME}': {blobs}")
        return blobs
    except AzureError as e:
        logging.error(f"Failed to list blobs: {e}")
        return []

def download_file(blob_name, local_path=None):
    local_path = local_path or os.path.join("data", blob_name)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    try:
        client = get_blob_service_client()
        blob_client = client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
        with open(local_path, "wb") as f:
            f.write(blob_client.download_blob().readall())
        logging.info(f"Downloaded '{blob_name}' -> '{local_path}'")
        return True
    except ResourceNotFoundError:
        logging.error(f"Blob not found: {CONTAINER_NAME}/{blob_name}")
        return False
    except AzureError as e:
        logging.error(f"Download failed for '{blob_name}': {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    list_blobs()
    download_file("sales_data.csv", "data/sales_data_downloaded.csv")
