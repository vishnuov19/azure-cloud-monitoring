# monitor.py
import logging, os
from datetime import datetime, timezone
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError

ACCOUNT_URL = "https://cloudmonitorstorage01.blob.core.windows.net"
LOG_FILE = "logs/pipeline.log"

def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(fmt)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(fmt)
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_pipeline_start():
    logging.info("=" * 60)
    logging.info(f"Pipeline started at {datetime.now(timezone.utc).isoformat()}")

def log_pipeline_end(success, elapsed_seconds):
    status = "SUCCESS" if success else "FAILURE"
    logging.info(f"Pipeline finished - status: {status}, elapsed: {elapsed_seconds:.2f}s")
    logging.info("=" * 60)

def check_storage_connectivity():
    try:
        client = BlobServiceClient(account_url=ACCOUNT_URL, credential=DefaultAzureCredential())
        containers = [c["name"] for c in client.list_containers()]
        logging.info(f"Storage connectivity OK - containers: {containers}")
        return True
    except AzureError as e:
        logging.error(f"Storage connectivity check failed: {e}")
        return False

def print_azure_monitor_guidance():
    guidance = (
        "\n--- Azure Monitor - where to look in the Portal ---\n"
        "1. Go to portal.azure.com\n"
        "2. Open Storage Account: cloudmonitorstorage01\n"
        "3. Click Monitoring -> Metrics in the left menu\n"
        "4. Key metrics: Transactions, Ingress/Egress, Availability, Latency\n"
        "5. Use Insights for a pre-built dashboard overview\n"
        "---------------------------------------------------"
    )
    print(guidance)
    logging.info("Azure Monitor guidance printed.")

if __name__ == "__main__":
    setup_logging()
    log_pipeline_start()
    check_storage_connectivity()
    print_azure_monitor_guidance()
    log_pipeline_end(success=True, elapsed_seconds=0)