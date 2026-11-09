# main.py
import logging, os, time
import pandas as pd
from monitor import setup_logging, log_pipeline_start, log_pipeline_end, check_storage_connectivity
from upload import upload_file
from download import download_file, list_blobs
from process import run_pipeline

RAW_CSV = "data/sales_data.csv"
DOWNLOADED_CSV = "data/sales_data_downloaded.csv"

def generate_sample_data(path=RAW_CSV):
    if os.path.exists(path):
        logging.info(f"Sample data already exists at '{path}' - skipping generation.")
        return
    os.makedirs("data", exist_ok=True)
    sales = pd.DataFrame({
        "Order_ID": [101, 102, 103, 104, 105],
        "Product":  ["Laptop", "Mouse", "Keyboard", "Monitor", "Webcam"],
        "Quantity": [2, 5, 3, 1, 4],
        "Price":    [55000, 500, 1200, 12000, 3500]
    })
    sales.to_csv(path, index=False)
    logging.info(f"Sample data generated - {len(sales)} rows -> '{path}'")

def main():
    setup_logging()
    log_pipeline_start()
    start_time = time.time()
    success = False
    try:
        logging.info("Step 1/5 - Checking Azure Storage connectivity...")
        if not check_storage_connectivity():
            logging.error("Connectivity check failed. Ensure RBAC is assigned and az login is active.")
            return
        logging.info("Step 2/5 - Generating sample CSV data...")
        generate_sample_data()
        logging.info("Step 3/5 - Uploading raw CSV to raw-data container...")
        if not upload_file(RAW_CSV):
            logging.error("Upload failed. Aborting.")
            return
        logging.info("Step 4/5 - Listing blobs and downloading from raw-data...")
        blobs = list_blobs()
        logging.info(f"Blobs in raw-data: {blobs}")
        if not download_file("sales_data.csv", DOWNLOADED_CSV):
            logging.error("Download failed. Aborting.")
            return
        logging.info("Step 5/5 - Running ETL pipeline...")
        if not run_pipeline(input_path=DOWNLOADED_CSV):
            logging.error("ETL pipeline failed.")
            return
        success = True
        logging.info("All steps completed successfully.")
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
    finally:
        log_pipeline_end(success=success, elapsed_seconds=time.time() - start_time)

if __name__ == "__main__":
    main()