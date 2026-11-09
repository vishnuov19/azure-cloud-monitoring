# process.py
import logging, os
import pandas as pd
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError

ACCOUNT_URL = "https://cloudmonitorstorage01.blob.core.windows.net"
PROCESSED_CONTAINER = "processed-data"
REQUIRED_COLUMNS = ["Order_ID", "Product", "Quantity", "Price"]

def get_blob_service_client():
    return BlobServiceClient(account_url=ACCOUNT_URL, credential=DefaultAzureCredential())

def validate_and_clean(df):
    rejected_rows = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Input CSV is missing columns: {missing}")
    valid_mask = pd.Series([True] * len(df), index=df.index)
    null_mask = df[REQUIRED_COLUMNS].isnull().any(axis=1)
    for idx in df[null_mask].index:
        rejected_rows.append({**df.loc[idx].to_dict(), "rejection_reason": "null value in required column"})
    valid_mask &= ~null_mask
    qty_mask = df["Quantity"].apply(lambda x: pd.to_numeric(x, errors="coerce")).le(0) | \
               df["Quantity"].apply(lambda x: pd.to_numeric(x, errors="coerce")).isna()
    for idx in df[qty_mask & valid_mask].index:
        rejected_rows.append({**df.loc[idx].to_dict(), "rejection_reason": "non-positive or invalid Quantity"})
    valid_mask &= ~qty_mask
    price_mask = df["Price"].apply(lambda x: pd.to_numeric(x, errors="coerce")).le(0) | \
                 df["Price"].apply(lambda x: pd.to_numeric(x, errors="coerce")).isna()
    for idx in df[price_mask & valid_mask].index:
        rejected_rows.append({**df.loc[idx].to_dict(), "rejection_reason": "non-positive or invalid Price"})
    valid_mask &= ~price_mask
    clean_df = df[valid_mask].copy().drop_duplicates()
    rejected_df = pd.DataFrame(rejected_rows)
    logging.info(f"Validation complete - valid: {len(clean_df)}, rejected: {len(rejected_df)}")
    return clean_df, rejected_df

def transform(df):
    df["Quantity"] = pd.to_numeric(df["Quantity"])
    df["Price"] = pd.to_numeric(df["Price"])
    df["Total_Sales"] = df["Quantity"] * df["Price"]
    logging.info("Transformation complete - Total_Sales added.")
    return df

def upload_processed(local_path, blob_name):
    try:
        client = get_blob_service_client()
        blob_client = client.get_blob_client(container=PROCESSED_CONTAINER, blob=blob_name)
        with open(local_path, "rb") as f:
            blob_client.upload_blob(f, overwrite=True)
        logging.info(f"Uploaded cleaned file -> {PROCESSED_CONTAINER}/{blob_name}")
        return True
    except AzureError as e:
        logging.error(f"Failed to upload processed file: {e}")
        return False

def run_pipeline(input_path="data/sales_data.csv"):
    logging.info(f"Processing started for: {input_path}")
    if not os.path.exists(input_path):
        logging.error(f"Input file not found: {input_path}")
        return False
    df = pd.read_csv(input_path)
    logging.info(f"Loaded {len(df)} rows from '{input_path}'")
    clean_df, rejected_df = validate_and_clean(df)
    if not rejected_df.empty:
        rejected_path = "data/rejected_rows.csv"
        rejected_df.to_csv(rejected_path, index=False)
        logging.warning(f"{len(rejected_df)} rows rejected - saved to '{rejected_path}'")
    if clean_df.empty:
        logging.error("No valid rows remaining. Aborting.")
        return False
    clean_df = transform(clean_df)
    cleaned_path = "data/cleaned_sales_data.csv"
    clean_df.to_csv(cleaned_path, index=False)
    logging.info(f"Cleaned data saved to '{cleaned_path}'")
    return upload_processed(cleaned_path, "cleaned_sales_data.csv")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_pipeline()