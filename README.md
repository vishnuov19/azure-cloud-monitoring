# Cloud-Based Data Storage & Monitoring System

A production-ready Azure cloud data pipeline demonstrating secure data ingestion, ETL processing, and cloud storage operations using Python and Azure Blob Storage.

## Project Overview

This project implements an end-to-end data pipeline that:
- Stores raw CSV files in Azure Blob Storage
- Downloads and processes data with validation and transformation logic
- Uploads cleaned results to a separate container
- Logs all operations for monitoring and debugging

Built to demonstrate cloud engineering fundamentals for junior cloud associate roles.

## Architecture

```
┌─────────────────────┐
│  Local Environment  │
│  Windows + Python   │
└──────────┬──────────┘
           │
           │ Azure CLI Identity
           │ (RBAC: Storage Blob Data Contributor)
           ▼
┌─────────────────────────────────────┐
│      Azure Storage Account          │
│   cloudmonitorstorage01             │
│                                     │
│  ┌─────────────┐  ┌──────────────┐ │
│  │  raw-data   │  │ processed-   │ │
│  │  container  │  │ data         │ │
│  │             │  │ container    │ │
│  └─────────────┘  └──────────────┘ │
└─────────────────────────────────────┘
```

**Stack:**
- **Cloud Platform:** Microsoft Azure
- **Storage:** Azure Blob Storage (Standard LRS, Hot tier)
- **Authentication:** Azure CLI + DefaultAzureCredential (RBAC)
- **Language:** Python 3.12
- **Libraries:** azure-storage-blob, azure-identity, pandas

## Features

### 1. Secure Authentication
- Uses Azure Role-Based Access Control (RBAC)
- No hardcoded keys or secrets
- `DefaultAzureCredential` with Azure CLI identity

### 2. Data Validation & Cleaning
- Validates required columns (Order_ID, Product, Quantity, Price)
- Checks for null values and data type correctness
- Ensures positive quantities and prices
- Removes duplicate records
- Logs rejected rows to `rejected_rows.csv`

### 3. Data Transformation
- Calculates derived metrics (Total_Sales = Quantity × Price)
- Converts data types for consistency
- Preserves raw data immutability (original stays in raw-data)

### 4. Comprehensive Logging
- Application-level logs written to `logs/pipeline.log`
- Timestamped entries for all operations
- Success/failure tracking with elapsed time
- Azure SDK request/response logging for debugging

### 5. End-to-End Pipeline
All steps orchestrated in `main.py`:
1. Storage connectivity check
2. Sample data generation
3. Upload to `raw-data` container
4. Download and verify blob access
5. ETL pipeline (validate → transform → upload to `processed-data`)

## Project Structure

```
azure-cloud-monitoring/
├── src/
│   ├── main.py          # Pipeline orchestrator
│   ├── upload.py        # Blob upload operations
│   ├── download.py      # Blob download and listing
│   ├── process.py       # ETL logic (validate, transform, upload)
│   └── monitor.py       # Logging setup and connectivity checks
├── data/                # Local CSV files (gitignored)
├── logs/                # Application logs (gitignored)
├── venv/                # Python virtual environment (gitignored)
├── requirements.txt     # Python dependencies
├── .gitignore
└── README.md
```

## Setup & Deployment

### Prerequisites
- Azure Free Account or subscription
- Azure CLI installed and authenticated (`az login`)
- Python 3.10+ and pip
- Git (for version control)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd azure-cloud-monitoring
   ```

2. **Create Azure resources**
   ```bash
   # Create resource group
   az group create --name rg-cloud-data-monitoring --location centralindia

   # Create storage account
   az storage account create \
     --name cloudmonitorstorage01 \
     --resource-group rg-cloud-data-monitoring \
     --location centralindia \
     --sku Standard_LRS
   ```

3. **Create Blob containers**
   ```bash
   az storage container create --name raw-data \
     --account-name cloudmonitorstorage01 --auth-mode login

   az storage container create --name processed-data \
     --account-name cloudmonitorstorage01 --auth-mode login
   ```

4. **Assign RBAC role**
   ```bash
   # Get your user object ID
   USER_ID=$(az ad signed-in-user show --query id -o tsv)

   # Get storage account scope
   STORAGE_SCOPE=$(az storage account show \
     --name cloudmonitorstorage01 \
     --resource-group rg-cloud-data-monitoring \
     --query id -o tsv)

   # Assign Storage Blob Data Contributor role
   az role assignment create \
     --assignee-object-id $USER_ID \
     --assignee-principal-type User \
     --role "Storage Blob Data Contributor" \
     --scope $STORAGE_SCOPE
   ```

5. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

### Running the Pipeline

```bash
cd src
python main.py
```

**Expected output:**
```
2026-11-09 21:08:03,003 INFO ============================================================
2026-11-09 21:08:03,003 INFO Pipeline started at 2026-11-09T15:38:03.003448+00:00
2026-11-09 21:08:03,004 INFO Step 1/5 - Checking Azure Storage connectivity...
2026-11-09 21:08:04,675 INFO Storage connectivity OK - containers: ['raw-data', 'processed-data', '$logs']
2026-11-09 21:08:04,675 INFO Step 2/5 - Generating sample CSV data...
2026-11-09 21:08:04,931 INFO Sample data generated - 5 rows -> 'data/sales_data.csv'
2026-11-09 21:08:04,931 INFO Step 3/5 - Uploading raw CSV to raw-data container...
2026-11-09 21:08:13,074 INFO Uploaded 'data/sales_data.csv' -> raw-data/sales_data.csv
2026-11-09 21:08:13,075 INFO Step 4/5 - Listing blobs and downloading from raw-data...
2026-11-09 21:08:17,089 INFO Blobs in raw-data: ['sales_data.csv']
2026-11-09 21:08:19,745 INFO Downloaded 'sales_data.csv' -> 'data/sales_data_downloaded.csv'
2026-11-09 21:08:19,745 INFO Step 5/5 - Running ETL pipeline...
2026-11-09 21:08:19,934 INFO Loaded 5 rows from 'data/sales_data_downloaded.csv'
2026-11-09 21:08:19,954 INFO Validation complete - valid: 5, rejected: 0
2026-11-09 21:08:19,965 INFO Transformation complete - Total_Sales added.
2026-11-09 21:08:19,975 INFO Cleaned data saved to 'data/cleaned_sales_data.csv'
2026-11-09 21:08:23,251 INFO Uploaded cleaned file -> processed-data/cleaned_sales_data.csv
2026-11-09 21:08:23,254 INFO All steps completed successfully.
2026-11-09 21:08:23,254 INFO Pipeline finished - status: SUCCESS, elapsed: 20.17s
2026-11-09 21:08:23,254 INFO ============================================================
```

## Verification

### Check uploaded blobs
```bash
az storage blob list --account-name cloudmonitorstorage01 \
  --container-name raw-data --output table --auth-mode login

az storage blob list --account-name cloudmonitorstorage01 \
  --container-name processed-data --output table --auth-mode login
```

### View cleaned data
```bash
cat data/cleaned_sales_data.csv
```

**Sample output:**
```csv
Order_ID,Product,Quantity,Price,Total_Sales
101,Laptop,2,55000,110000
102,Mouse,5,500,2500
103,Keyboard,3,1200,3600
104,Monitor,1,12000,12000
105,Webcam,4,3500,14000
```

### View Azure Monitor metrics
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to Storage Account: `cloudmonitorstorage01`
3. Click **Monitoring → Metrics**
4. View:
   - **Transactions** (request count)
   - **Ingress/Egress** (bytes uploaded/downloaded)
   - **Availability** (% successful requests)
   - **Success E2E Latency** (end-to-end response time)

## Key Concepts Demonstrated

| Concept | Implementation |
|---------|---------------|
| **Cloud Computing** | Azure platform for scalable storage |
| **IaaS vs PaaS** | Blob Storage (PaaS) - managed, no server provisioning |
| **Authentication** | Azure CLI identity verified via `az login` |
| **Authorization** | RBAC role assignment (Storage Blob Data Contributor) |
| **Least Privilege** | Data-plane access only, scoped to storage account |
| **ETL Pipeline** | Extract (download) → Transform (validate + calculate) → Load (upload) |
| **Data Validation** | Schema checks, null handling, type validation |
| **Idempotency** | Overwrite mode prevents duplicate uploads |
| **Logging** | Structured logs with timestamps and severity levels |
| **Resource Organization** | Resource Groups, naming conventions, regional deployment |

## Security & Cost Best Practices

- ✅ No hardcoded credentials (uses RBAC + Azure CLI)
- ✅ Private containers (no anonymous access)
- ✅ TLS 1.2 encryption in transit
- ✅ Standard storage tier (cost-optimized for frequent access)
- ✅ LRS redundancy (lowest cost for dev/test)
- ✅ Small sample datasets (minimal storage costs)
- ✅ `.gitignore` excludes `venv/`, `data/`, `logs/`, secrets

**Cost estimate:** ~$0.02/month for this workload under Azure Free Account limits.

## Dependencies

```txt
azure-storage-blob==12.31.1
azure-identity==1.27.0
pandas==3.1.1
python-dotenv==1.2.4
```

## Interview Talking Points

**"Walk me through your Azure project."**
> "I built a cloud data pipeline that ingests CSV sales data into Azure Blob Storage, validates and transforms it with Python and Pandas, then writes cleaned results back to a separate container. I used Azure RBAC with DefaultAzureCredential for secure authentication—no hardcoded keys—and implemented comprehensive logging for monitoring. The architecture separates raw and processed data to preserve source immutability, and all storage operations use the Azure SDK with proper error handling."

**"What is RBAC and why did you use it?"**
> "RBAC is Role-Based Access Control. Instead of using the storage account key (which grants full admin access), I assigned my Azure identity the Storage Blob Data Contributor role, scoped to just that storage account. This follows the principle of least privilege—I only get read/write access to blob data, not the ability to delete the account or change firewall rules. It's more secure and auditable."

**"How would you handle failures in production?"**
> "The pipeline logs every step with timestamps and error details to `pipeline.log`. Each function returns True/False so failures stop the pipeline early instead of cascading. Rejected rows are saved to `rejected_rows.csv` for manual review. In production, I'd add retry logic with exponential backoff for transient network errors, send alerts to Azure Monitor or a messaging service on failure, and use Azure Functions or Logic Apps to trigger the pipeline on a schedule or event."

**"What's the difference between authentication and authorization?"**
> "Authentication proves who you are—in my case, `az login` verified my Azure identity. Authorization determines what you're allowed to do—RBAC granted my identity permission to read and write blobs, but not delete the storage account. Authentication happens first, then authorization checks whether that identity has the right role assignment."

## Future Enhancements

- [ ] Add Azure Functions trigger for automated pipeline execution
- [ ] Implement retry logic with exponential backoff
- [ ] Add unit tests and integration tests
- [ ] Set up CI/CD pipeline with GitHub Actions
- [ ] Add Azure Application Insights for telemetry
- [ ] Implement data quality metrics dashboard
- [ ] Add email/Slack notifications for pipeline failures
- [ ] Support multiple file formats (Excel, JSON, Parquet)
- [ ] Add data versioning with blob snapshots
- [ ] Implement incremental processing for large datasets

## Cleanup

To avoid charges, delete all resources when done:

```bash
az group delete --name rg-cloud-data-monitoring --yes --no-wait
```

This deletes the resource group and all contained resources (storage account, containers, blobs).

## License

MIT License - feel free to use this project as a portfolio reference or learning resource.

## Author

**Vishnu O V**  
Junior Cloud Associate | Azure | Python  
[GitHub](https://github.com/vishnuov19) | [LinkedIn](https://linkedin.com/in/vishnuov)

---

**Project Status:** ✅ Completed and tested (November 2026)
