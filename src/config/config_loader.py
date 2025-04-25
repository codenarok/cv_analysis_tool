import os
from dotenv import load_dotenv

def load_config():
    """Loads configuration from a .env file."""
    load_dotenv() # Load environment variables from .env file

    config = {
        'TARGET_URL': os.getenv('TARGET_URL', 'https://www.civilservicejobs.service.gov.uk/csr/index.cgi'),
        'CV_FILE_PATH': os.getenv('CV_FILE_PATH'),
        'AZURE_LANGUAGE_ENDPOINT': os.getenv('AZURE_LANGUAGE_ENDPOINT'),
        'AZURE_LANGUAGE_KEY': os.getenv('AZURE_LANGUAGE_KEY'),
        'OUTPUT_CSV_FILE': os.getenv('OUTPUT_CSV_FILE', 'matched_jobs.csv'),
        # Ensure conversion to int happens here with proper defaults
        'LOGIN_WAIT_TIME': int(os.getenv('LOGIN_WAIT_TIME', '60')), # Default to string '60'
        'MATCH_THRESHOLD': int(os.getenv('MATCH_THRESHOLD', '5')),  # Default to string '5'
    }

    # Basic validation
    if not config['CV_FILE_PATH']:
        raise ValueError("CV_FILE_PATH environment variable not set.")
    if not config['AZURE_LANGUAGE_ENDPOINT']:
        raise ValueError("AZURE_LANGUAGE_ENDPOINT environment variable not set.")
    if not config['AZURE_LANGUAGE_KEY']:
        raise ValueError("AZURE_LANGUAGE_KEY environment variable not set.")

    return config

if __name__ == '__main__':
    # Example usage: Load and print config
    try:
        app_config = load_config()
        print("Configuration loaded successfully:")
        for key, value in app_config.items():
            print(f"- {key}: {value}")
    except ValueError as e:
        print(f"Error loading configuration: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

