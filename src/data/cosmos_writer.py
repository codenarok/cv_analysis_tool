import logging
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.identity import DefaultAzureCredential # Import DefaultAzureCredential

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_cosmos_client(endpoint: str) -> CosmosClient | None: # Removed key parameter
    """Initializes and returns a CosmosClient instance using DefaultAzureCredential."""
    try:
        # Use DefaultAzureCredential for authentication
        credential = DefaultAzureCredential()
        client = CosmosClient(endpoint, credential=credential)
        logging.info("Cosmos DB client initialized successfully using Azure Identity.")
        return client
    except Exception as e:
        logging.error(f"Failed to initialize Cosmos DB client using Azure Identity: {e}")
        return None

def get_cosmos_container(client: CosmosClient, db_name: str, container_name: str):
    """Gets or creates a Cosmos DB database and container."""
    try:
        database = client.create_database_if_not_exists(id=db_name)
        logging.info(f"Database '{db_name}' ensured.")
        # Define a partition key - using 'Reference Number' or 'Link' might be good candidates
        # For simplicity, let's use '/Job Title' for now, but consider a more unique ID
        partition_key_path = PartitionKey(path="/Job Title")
        container = database.create_container_if_not_exists(
            id=container_name,
            partition_key=partition_key_path,
            offer_throughput=400
        )
        logging.info(f"Container '{container_name}' ensured.")
        return container
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Error getting/creating Cosmos DB container: {e.message}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred with Cosmos DB container: {e}")
        return None

def write_job_to_cosmos(container, job_data: dict):
    """Writes (upserts) a single job dictionary to the Cosmos DB container."""
    if not container or not job_data:
        logging.warning("Cosmos container or job data is missing, cannot write.")
        return

    try:
        # Add an 'id' field if it doesn't exist, using 'Link' or 'Reference Number' if available
        # Cosmos DB requires an 'id' field for items.
        if 'id' not in job_data:
            if job_data.get('Link'):
                job_data['id'] = job_data['Link'] # Use Link as unique ID
            elif job_data.get('Reference Number'):
                 job_data['id'] = job_data['Reference Number'] # Fallback to Ref Num
            else:
                 # If neither is available, we might need a different strategy or log an error
                 logging.error(f"Cannot determine unique ID for job: {job_data.get('Job Title')}. Skipping Cosmos write.")
                 return

        logging.debug(f"Upserting job with id: {job_data['id']}")
        container.upsert_item(body=job_data)
        logging.info(f"Successfully upserted job '{job_data.get('Job Title', job_data['id'])}' to Cosmos DB.")
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f"Cosmos DB HTTP error writing job id {job_data.get('id', 'N/A')}: {e.message}")
    except Exception as e:
        logging.error(f"Unexpected error writing job id {job_data.get('id', 'N/A')} to Cosmos DB: {e}")

if __name__ == '__main__':
    # Example Usage (requires .env file with Cosmos details, except key)
    import os
    from dotenv import load_dotenv
    load_dotenv()

    endpoint = os.getenv('COSMOS_ENDPOINT')
    db_name = os.getenv('COSMOS_DATABASE_NAME')
    container_name = os.getenv('COSMOS_CONTAINER_NAME')

    # Updated check
    if not all([endpoint, db_name, container_name]):
        print("Error: Missing Cosmos DB configuration (ENDPOINT, DATABASE_NAME, CONTAINER_NAME) in .env file for example.")
    else:
        # Pass only endpoint
        client = initialize_cosmos_client(endpoint)
        if client:
            container = get_cosmos_container(client, db_name, container_name)
            if container:
                sample_job = {
                    'Scrape Date': '2025-04-25',
                    'Job Title': 'Test Job - Cosmos Writer',
                    'Reference Number': 'TEST-001',
                    'Link': 'http://example.com/test-cosmos',
                    'Department': 'Testing Dept',
                    # Add other fields as needed
                }
                print(f"Attempting to write sample job to Cosmos DB...")
                write_job_to_cosmos(container, sample_job)
                print("Sample write attempt finished. Check logs and Azure portal.")
