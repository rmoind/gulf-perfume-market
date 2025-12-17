from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import os
import sys


# Google BigQuery
# Objective: Ingest large-scale social logs and query them.

# CONFIGURATION

KEY_PATH = "gcp_keys.json"

PROJECT_ID = "perfume-analytics-demo" 
DATASET_ID = "social_data"
TABLE_ID = "sentiment_logs"

def upload_and_query_bigdata():
    """
    1. Uploads local DataFrame to BigQuery (Simulating Ingestion).
    2. Queries BigQuery using SQL (Simulating Extraction).
    """
    
    # 1. Validation Check
    if not os.path.exists(KEY_PATH):
        print(f"\n CRITICAL ERROR: '{KEY_PATH}' not found.")
        print("To validate the 'Big Data' criteria, you must:")
        print("1. Create a Google Cloud Project.")
        print("2. Download a Service Account JSON Key.")
        print("3. Save it as 'gcp_keys.json' in this folder.\n")
        return

    try:
        print(" Authenticating with Google Cloud...")
        credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
        
        # Use the project_id found inside the JSON key automatically
        client = bigquery.Client(credentials=credentials, project=credentials.project_id)
        project_id = credentials.project_id # specific to your key

        # 2. Prepare Data (Simulating a large CSV load)
        data_to_upload = pd.DataFrame([
            {"Brand": "Lattafa", "Sentiment_Score": 0.85, "Platform": "TikTok", "Mentions": 1500},
            {"Brand": "Xerjoff", "Sentiment_Score": 0.92, "Platform": "Instagram", "Mentions": 320},
            {"Brand": "Ajmal", "Sentiment_Score": 0.76, "Platform": "Twitter", "Mentions": 890},
            {"Brand": "Al Haramain", "Sentiment_Score": 0.81, "Platform": "TikTok", "Mentions": 1200},
        ])

        # 3. Create Dataset & Table reference
        dataset_ref = f"{project_id}.{DATASET_ID}"
        table_ref = f"{project_id}.{DATASET_ID}.{TABLE_ID}"

        # Create Dataset if not exists
        print(f" Setting up Dataset: {dataset_ref}...")
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)

        # 4. Upload Data (Ingestion)
        print(f" Uploading data to Table: {table_ref}...")
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",
        )
        job = client.load_table_from_dataframe(data_to_upload, table_ref, job_config=job_config)
        job.result() 
        print(" Ingestion Complete.")

        # 5. EXTRACT
        print(" Executing BigQuery SQL Extraction...")
        
        query = f"""
            SELECT Brand, Platform, Mentions, Sentiment_Score
            FROM `{table_ref}`
            WHERE Sentiment_Score > 0.8
            ORDER BY Mentions DESC
        """
        
        query_job = client.query(query)
        results = query_job.to_dataframe()
        
        print("\n--- BIG DATA RESULTS (High Sentiment) ---")
        print(results.to_markdown(index=False))
        
        # Save extraction to prove storage
        results.to_csv("bigquery_extract.csv", index=False)
        print("\n Extraction saved to 'bigquery_extract.csv'")

    except Exception as e:
        print(f"\n BigQuery Connection Error: {e}")
        print("Tip: Ensure the Service Account has 'BigQuery Admin' roles.")

if __name__ == "__main__":
    upload_and_query_bigdata()