from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import TextAnalyticsClient
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_azure_client(endpoint, key):
    """Initializes and returns the Azure TextAnalyticsClient."""
    if not endpoint or not key:
        logging.error("Azure endpoint or key is missing.")
        raise ValueError("Azure endpoint and key must be provided.")
    try:
        logging.info(f"Initializing Azure Text Analytics client with endpoint: {endpoint[:20]}...") # Log partial endpoint
        credential = AzureKeyCredential(key)
        client = TextAnalyticsClient(endpoint=endpoint, credential=credential)
        logging.info("Azure Text Analytics client initialized successfully.")
        return client
    except Exception as e:
        logging.error(f"Failed to initialize Azure Text Analytics client: {e}")
        raise

def analyze_text_with_azure(client: TextAnalyticsClient, text: str, mode='key_phrases'):
    """Analyzes text using Azure AI Language service (Key Phrases or Entities)."""
    if not text:
        logging.warning("Received empty text for analysis.")
        return []

    # Azure limits document size, split if necessary (simple split, might need refinement)
    # Max 5,120 chars per document for key phrases/entities
    max_chars = 5100 
    documents = [text[i:i+max_chars] for i in range(0, len(text), max_chars)]
    
    # Limit number of documents per request (max 5 for free tier, 10 for standard)
    max_docs_per_request = 5 
    results = []

    try:
        for i in range(0, len(documents), max_docs_per_request):
            batch = documents[i:i+max_docs_per_request]
            logging.info(f"Sending batch of {len(batch)} document(s) to Azure for {mode} analysis...")
            
            if mode == 'key_phrases':
                response = client.extract_key_phrases(documents=batch)
                for doc in response:
                    if not doc.is_error:
                        results.extend(doc.key_phrases)
                    else:
                        logging.error(f"Azure API Error: {doc.id}, Error Code: {doc.error.code}, Message: {doc.error.message}")
            elif mode == 'entities':
                response = client.recognize_entities(documents=batch)
                for doc in response:
                    if not doc.is_error:
                        # Extract entity text, you might want category/subcategory too
                        results.extend([entity.text for entity in doc.entities]) 
                    else:
                        logging.error(f"Azure API Error: {doc.id}, Error Code: {doc.error.code}, Message: {doc.error.message}")
            else:
                logging.error(f"Unsupported analysis mode: {mode}")
                raise ValueError(f"Unsupported analysis mode: {mode}. Use 'key_phrases' or 'entities'.")
        
        logging.info(f"Azure analysis ({mode}) completed. Found {len(results)} results.")
        # Return unique results
        return list(set(results))

    except Exception as e:
        logging.error(f"Error during Azure AI analysis ({mode}): {e}")
        # Depending on the error, you might want to retry or return partial results
        return [] # Return empty list on error for now

if __name__ == '__main__':
    # Example Usage (Requires environment variables to be set)
    # Load dotenv if you have a .env file
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logging.info(".env file loaded (if exists).")
    except ImportError:
        logging.warning("python-dotenv not installed, skipping .env load.")
        pass

    azure_endpoint = os.getenv('AZURE_LANGUAGE_ENDPOINT')
    azure_key = os.getenv('AZURE_LANGUAGE_KEY')

    if not azure_endpoint or not azure_key:
        print("Skipping example: Set AZURE_LANGUAGE_ENDPOINT and AZURE_LANGUAGE_KEY environment variables.")
    else:
        try:
            client = initialize_azure_client(azure_endpoint, azure_key)
            
            sample_text = (
                "Dr. Smith, a renowned scientist from New York, presented his findings on climate change "
                "at the international conference in Paris. His research highlights the impact of carbon emissions "
                "and suggests renewable energy solutions. The event took place last Tuesday."
            )
            
            print("\n--- Analyzing Sample Text for Key Phrases ---")
            key_phrases = analyze_text_with_azure(client, sample_text, mode='key_phrases')
            print("Key Phrases:", key_phrases)

            print("\n--- Analyzing Sample Text for Entities ---")
            entities = analyze_text_with_azure(client, sample_text, mode='entities')
            print("Entities:", entities)

        except ValueError as e:
            print(f"Configuration Error: {e}")
        except Exception as e:
            print(f"An error occurred during the example: {e}")
